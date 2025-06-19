from sqlalchemy import select

from app.api.schemas.article import ArticleRead
from app.db.article import Article
from app.repositories.base import BaseRepository


class ArticleRepository(BaseRepository):
    model = Article

    async def get_by_url(self, url: str) -> ArticleRead | None:
        stmt = select(self.model).where(self.model.url == url)
        result = await self.session.execute(stmt)
        obj = result.scalars().first()
        return obj.to_pydantic() if obj else None

    async def get_by_id(self, obj_id: int) -> ArticleRead | None:
        stmt = select(Article).where(Article.id == obj_id)
        result = await self.session.execute(stmt)
        obj = result.scalars().first()
        return obj.to_pydantic() if obj else None

    async def get_or_create(
            self, url: str, title: str, content: str, parent_id: int | None = None
    ) -> ArticleRead:
        existing = await self.get_by_url(url)
        if existing:
            return existing

        article = Article(url=url, title=title, content=content, parent_id=parent_id)
        self.session.add(article)
        await self.session.commit()

        return await self.get_by_url(url)

    async def save(self, article: Article):
        self.session.add(article)
