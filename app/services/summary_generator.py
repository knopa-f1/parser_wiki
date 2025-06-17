import openai
from openai import AsyncOpenAI

from app.core.config import settings
from app.utils.unit_of_work import UnitOfWork
from app.models.summary import Summary


client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


def get_language_prompt(article_title: str, article_url: str) -> list[dict]:
    if settings.LANG == "ru":
        system_msg = "Ты — помощник, кратко пересказывающий статьи Википедии на русском языке."
        user_msg = f"Сделай краткое содержание статьи Википедии с названием «{article_title}» по ссылке: {article_url}"
    else:
        system_msg = "You are an assistant that summarizes Wikipedia articles in English."
        user_msg = f"Write a short summary of the Wikipedia article titled \"{article_title}\" at {article_url}"

    return [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg},
    ]

async def generate_summary_for_article_id(article_id: int, uow: UnitOfWork):
    async with uow:
        article = await uow.articles.get_by_id(article_id)
        if not article:
            return None

        existing = await uow.summaries.get_by_article_id(article.id)
        if existing:
            return existing

        messages = get_language_prompt(article.title or "", article.url)

    response = await client.chat.completions.create(
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


async def get_summary_by_url(url: str, uow: UnitOfWork):
    async with uow:
        article = await uow.articles.get_by_url(url)
        if not article:
            return None

        summary = await uow.summaries.get_by_article_id(article.id)
        return summary
