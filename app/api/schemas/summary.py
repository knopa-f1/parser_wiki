from pydantic import BaseModel


class SummaryBase(BaseModel):
    article_id: int
    summary: str


class SummaryCreate(SummaryBase):
    pass


class SummaryRead(SummaryBase):
    id: int

    class Config:
        from_attributes = True
