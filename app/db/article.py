from sqlalchemy import String, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.api.schemas.article import ArticleRead
from app.db.database import Base


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String, unique=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("articles.id"), nullable=True)

    parent = relationship("Article", remote_side=[id], backref="children")

    def to_pydantic(self) -> ArticleRead:
        return ArticleRead(
            id=self.id,
            url=self.url,
            title=self.title,
            content=self.content,
            parent_id=self.parent_id
        )
