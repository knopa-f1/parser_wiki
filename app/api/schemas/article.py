from typing import Optional

from pydantic import BaseModel


class ArticleBase(BaseModel):
    url: str
    title: Optional[str] = None
    content: Optional[str] = None
    parent_id: Optional[int] = None


class ArticleCreate(ArticleBase):
    pass


class ArticleRead(ArticleBase):
    id: int

    class Config:
        from_attributes = True
