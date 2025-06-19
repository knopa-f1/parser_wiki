from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select

from app.db.article import Article
from app.db.summary import Summary
from app.services.summary import SummaryGenerator
from app.services.wiki_parser import WikiParser


@pytest.mark.anyio
async def test_parse_article_with_patch(client, db_session):
    test_url = "https://en.wikipedia.org/wiki/Test_Page"
    test_title = "Mock Title"
    test_content = "Mock content"
    test_summary = "This is a summary."

    async def mock_generate_summary(article_id, uow):
        async with uow:
            summary = Summary(article_id=article_id, summary=test_summary)
            uow.session.add(summary)
            await uow.commit()
            return summary

    with patch.object(WikiParser, "fetch_html", new=AsyncMock(return_value="<html></html>")), \
            patch.object(WikiParser, "extract_title_and_content", return_value=(test_title, test_content)), \
            patch.object(WikiParser, "extract_links", return_value=[]), \
            patch.object(SummaryGenerator, "generate_for_article_id", new=AsyncMock(side_effect=mock_generate_summary)):
        response = await client.post(f"/parse?url={test_url}")
        assert response.status_code == 200

        result = await db_session.execute(select(Article).where(Article.url == test_url))
        article = result.scalar_one_or_none()
        assert article is not None
        assert article.title == test_title
        assert article.content == test_content

        result = await db_session.execute(select(Summary).where(Summary.article_id == article.id))
        summary = result.scalar_one_or_none()
        assert summary is not None
        assert summary.summary == test_summary


@pytest.mark.anyio
async def test_get_summary_endpoint(client, db_session):
    test_url = "https://en.wikipedia.org/wiki/test"
    article = Article(url=test_url, title="Test title", content="Test content")
    db_session.add(article)
    await db_session.flush()

    summary = Summary(article_id=article.id, summary="Test summary content")
    db_session.add(summary)
    await db_session.commit()

    response = await client.get("/summary", params={"url": test_url})

    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == "Test summary content"
