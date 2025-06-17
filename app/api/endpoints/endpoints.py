from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.schemas.summary import SummaryRead
from app.services.workflow import run_parse_workflow
from app.services.summary_generator import get_summary_by_url
from app.utils.unit_of_work import UnitOfWork

router = APIRouter()


@router.post("/parse")
async def parse_article(
    url: str = Query(...),
    uow: UnitOfWork = Depends(UnitOfWork)
):
    await run_parse_workflow(url, uow)
    return {"status": "ok"}


@router.get("/summary", response_model=SummaryRead)
async def get_summary(
    url: str = Query(...),
    uow: UnitOfWork = Depends(UnitOfWork)
):
    summary = await get_summary_by_url(url, uow)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary
