import asyncio
import logging

import aiohttp

from app.core.config import settings
from app.services.summary import SummaryGenerator
from app.services.wiki_parser import WikiParser
from app.utils.unit_of_work import UnitOfWorkFactory

logger = logging.getLogger(__name__)


class WikiParseWorkflow:
    def __init__(self, url: str, uow_factory: UnitOfWorkFactory):
        self.url = url
        self.max_depth = settings.MAX_DEPTH
        self.max_links_per_level = settings.MAX_LINKS_PER_LEVEL
        self.semaphore = asyncio.Semaphore(10)
        self.visited = set()
        self.uow_factory = uow_factory
        self.parser = WikiParser()
        self.summary_generator = SummaryGenerator()
        self._summary_task: asyncio.Task | None = None

    async def run(self):
        logger.info("Starting workflow for %s", self.url)
        async with aiohttp.ClientSession() as http_session:
            await self._process_article(self.url, None, 0, http_session)
            if self._summary_task:
                await self._summary_task
        logger.info("Finished workflow for %s", self.url)

    async def _generate_summary(self, article_id: int):
        logger.info("Generating summary for article ID %s", article_id)
        async with self.uow_factory() as uow:
            await self.summary_generator.generate_for_article_id(article_id, uow)
        logger.info("Generated summary for article ID %s", article_id)

    async def _process_article(
            self,
            url: str,
            parent_id: int | None,
            depth: int,
            http_session: aiohttp.ClientSession,
    ):
        if depth > self.max_depth or url in self.visited:
            return

        self.visited.add(url)

        async with self.semaphore:
            try:
                html = await self.parser.fetch_html(url, http_session)
                title, content = self.parser.extract_title_and_content(html)
                logger.info("Fetched article: depth=%s, url=%s", depth, url)
            except Exception as e:
                logger.warning("Failed to fetch %s: %s", url, e)
                return

            async with self.uow_factory() as uow:
                article = await uow.articles.get_or_create(
                    url=url,
                    title=title,
                    content=content,
                    parent_id=parent_id
                )
                logger.info("Saved article: depth=%s, url=%s", depth, url)

            if depth == 0:
                self._summary_task = asyncio.create_task(
                    self._generate_summary(article.id)
                )

        links = self.parser.extract_links(html)
        logger.debug("Found %s links at depth %s", len(links), depth)

        tasks = []
        count = 0
        for link in links:
            if link in self.visited:
                continue
            tasks.append(self._process_article(link, article.id, depth + 1, http_session))
            count += 1
            if count >= self.max_links_per_level:
                break

        await asyncio.gather(*tasks, return_exceptions=True)
