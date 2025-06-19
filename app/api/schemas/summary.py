from pydantic import BaseModel


class SummaryBase(BaseModel):
    article_id: int
    summary: str


class SummaryCreate(SummaryBase):
    pass


class SummaryRead(SummaryBase):
    id: int

    class Config: # pylint: disable=too-few-public-methods
        from_attributes = True
