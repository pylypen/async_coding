from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from homework_8 import crud, schemas
from homework_8.dependencies import get_db
from typing import List

router = APIRouter()

@router.post("/", response_model=schemas.CVEOut)
async def create_cve(cve: schemas.CVECreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_cve(db=db, cve=cve)

@router.get("/{cve_id}", response_model=schemas.CVEOut)
async def read_cve(cve_id: str, db: AsyncSession = Depends(get_db)):
    db_cve = await crud.get_cve(db, cve_id)
    if db_cve is None:
        raise HTTPException(status_code=404, detail="CVE not found")
    return db_cve
