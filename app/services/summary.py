import logging

from openai import AsyncOpenAI

from app.core.config import settings
from app.db.summary import Summary
from app.utils.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class SummaryGenerator: # pylint: disable=too-few-public-methods
    def __init__(self, client: AsyncOpenAI | None = None):
        self.client = client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    def _get_language_prompt(self, article_title: str, article_url: str) -> list[dict]:
        if settings.LANGUAGE == "ru":
            system_msg = "Ты — помощник, кратко пересказывающий статьи Википедии на русском языке."
            user_msg = f"Напиши краткое содержание статьи Википедии на русском с названием «{article_title}» по ссылке: {article_url}"
        else:
            system_msg = "You are an assistant that summarizes Wikipedia articles in English."
            user_msg = f"Write a short summary of the Wikipedia in English article titled \"{article_title}\" at {article_url}"

        return [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]

    async def generate_for_article_id(self, article_id: int, uow: UnitOfWork):
        async with uow:
            article = await uow.articles.get_by_id(article_id)
            if not article:
                logger.warning("Article with ID %s not found", article_id)
                return None

            existing = await uow.summaries.get_by_article_id(article.id)
            if existing:
                logger.info("Summary already exists for article ID %s", article_id)
                return existing

            messages = self._get_language_prompt(article.title or "", article.url)

        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.5,
            max_tokens=500,
        )

        summary_text = response.choices[0].message.content.strip()

        async with uow:
            summary = Summary(article_id=article.id, summary=summary_text)
            uow.session.add(summary)
            await uow.commit()
            return summary


class SummaryService: # pylint: disable=too-few-public-methods
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_summary_by_url(self, url: str):
        async with self.uow as uow:
            article = await uow.articles.get_by_url(url)
            if not article:
                return None
            return await uow.summaries.get_by_article_id(article.id)
