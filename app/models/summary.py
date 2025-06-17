from sqlalchemy import Integer, Text, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.api.schemas.summary import SummaryRead
from app.core.database import Base


class Summary(Base):
    __tablename__ = "summaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    article_id: Mapped[int] = mapped_column(Integer, ForeignKey("articles.id"), unique=True)
    summary: Mapped[str] = mapped_column(Text)

    article = relationship("Article", backref="summary")

    def to_pydantic(self) -> SummaryRead:
        return SummaryRead(
            id=self.id,
            article_id=self.article_id,
            summary=self.summary
        )
