from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import CVE
from schemas import CVECreate


async def create_cve(db: AsyncSession, cve: CVECreate):
    db_cve = CVE(**cve.dict())

    db_cve.date_published = db_cve.date_published.replace(tzinfo=None)
    db_cve.date_updated = db_cve.date_updated.replace(tzinfo=None)

    db.add(db_cve)
    await db.commit()
    await db.refresh(db_cve)
    return db_cve

async def get_cve(db: AsyncSession, cve_id: str):
    result = await db.execute(select(CVE).filter(CVE.id == cve_id))
    return result.scalars().first()

