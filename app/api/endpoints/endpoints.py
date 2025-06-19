from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.schemas.summary import SummaryRead
from app.services.summary import SummaryService
from app.services.workflow import WikiParseWorkflow
from app.utils.unit_of_work import UnitOfWork, UnitOfWorkFactory

router = APIRouter()


def get_summary_service() -> SummaryService:
    return SummaryService(UnitOfWork())


def get_uow_factory():
    return UnitOfWorkFactory()


@router.post("/parse")
async def parse_article(
        url: str = Query(...),
        uow_factory: UnitOfWorkFactory = Depends(get_uow_factory)
):
    workflow = WikiParseWorkflow(url, uow_factory)
    await workflow.run()
    return {"status": "ok"}


@router.get("/summary", response_model=SummaryRead)
async def get_summary(
        url: str = Query(...),
        service: SummaryService = Depends(get_summary_service)
):
    summary = await service.get_summary_by_url(url)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary
