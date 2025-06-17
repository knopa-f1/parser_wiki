from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.summary import Summary
from app.repositories.base import BaseRepository


class SummaryRepository(BaseRepository):
    model = Summary

    async def get_by_article_id(self, article_id: int):
        stmt = select(self.model).where(self.model.article_id == article_id)
        res = await self.session.execute(stmt)
        obj =  res.scalars().first()
        return obj.to_pydantic() if obj else None

    async def save(self, summary: Summary):
        self.session.add(summary)
