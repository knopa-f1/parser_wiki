import asyncio
import aiohttp

from app.core.config import settings
from app.services.wiki_parser import fetch_html, extract_links, extract_title_and_content
from app.services.summary_generator import generate_summary_for_article_id
from app.utils.unit_of_work import UnitOfWork

max_depth = settings.MAX_DEPTH

async def run_parse_workflow(url: str, uow: UnitOfWork):
    async with aiohttp.ClientSession() as http_session:
        html = await fetch_html(url, http_session)
        title, content = extract_title_and_content(html)

        async with uow:
            root_article = await uow.articles.get_or_create(
                url=url,
                title=title,
                content=content,
                parent_id=None
            )

        await asyncio.gather(
            _parse_recursive_links(
                html, root_article.id, 1, http_session, visited={url}
            ),
            generate_summary_for_article_id(root_article.id, uow)
        )


async def _parse_recursive_links(
    html: str,
    parent_id: int,
    current_depth: int,
    http_session: aiohttp.ClientSession,
    visited: set[str]
):
    if current_depth > max_depth:
        return

    links = extract_links(html)
    tasks = []

    for link in links:
        if link in visited:
            continue
        visited.add(link)
        tasks.append(
            _parse_recursive(link, parent_id, current_depth, http_session, visited)
        )

    await asyncio.gather(*tasks)


async def _parse_recursive(
    url: str,
    parent_id: int,
    current_depth: int,
    http_session: aiohttp.ClientSession,
    visited: set[str],
):
    if current_depth > max_depth:
        return

    try:
        html = await fetch_html(url, http_session)
        title, content = extract_title_and_content(html)
    except Exception:
        return

    async with UnitOfWork() as uow:
        saved_article = await uow.articles.get_or_create(
                        url=url,
                        title=title,
                        content=content,
                        parent_id=parent_id
        )

    await _parse_recursive_links(
        html, saved_article.id, current_depth + 1, http_session, visited
    )
