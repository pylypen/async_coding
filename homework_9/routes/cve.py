from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from urllib3 import request

from homework_9 import crud, schemas
from homework_9.dependencies import get_db


router = APIRouter()

@router.get("/")
async def list_cve(skip: int = 0, limit: int = 10, session: AsyncSession = Depends(get_db)):
    return await crud.get_cves(session, skip, limit)

@router.post("/", response_model=schemas.CVEOut)
async def create_cve(cve: schemas.CVECreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_cve(db=db, cve=cve)

@router.get("/{cve_id}", response_model=schemas.CVEOut)
async def read_cve(cve_id: str, db: AsyncSession = Depends(get_db)):
    db_cve = await crud.get_cve(db, cve_id)
    if db_cve is None:
        raise HTTPException(status_code=404, detail="CVE not found")
    return db_cve


@router.get("/search/date-range")
async def search_by_date_range(start_date: str, end_date: str, session: AsyncSession = Depends(get_db)):
    return await crud.search_by_date_range(session, start_date, end_date)


@router.get("/search/text")
async def search_by_text(query: str, session: AsyncSession = Depends(get_db)):
    return await crud.search_by_text(session, query)

