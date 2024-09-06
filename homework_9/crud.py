from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from homework_9.models import CVE
from homework_9.schemas import CVECreate
from dateutil import parser


async def create_cve(db: AsyncSession, cve: CVECreate):
    db_cve = CVE(**cve.dict())

    check_cve = await get_cve(db, db_cve.id)
    if check_cve:
        return check_cve

    db_cve.date_published = db_cve.date_published.replace(tzinfo=None)
    db_cve.date_updated = db_cve.date_updated.replace(tzinfo=None)

    db.add(db_cve)
    await db.commit()
    await db.refresh(db_cve)
    return db_cve

async def get_cve(db: AsyncSession, cve_id: str):
    result = await db.execute(select(CVE).filter(CVE.id == cve_id))
    return result.scalars().first()

async def get_cves(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(select(CVE).offset(skip).limit(limit))
    return result.scalars().all()

async def search_by_date_range(db: AsyncSession, start_date: str, end_date: str):
    start_date = parser.parse(start_date).replace(tzinfo=None)
    end_date = parser.parse(end_date).replace(tzinfo=None)

    query = select(CVE).where(CVE.date_published.between(start_date, end_date))
    results = await db.execute(query)
    return results.scalars().all()

async def search_by_text(db: AsyncSession, query: str):
    like_query = f"%{query}%"
    query = select(CVE).where(CVE.description.ilike(like_query))
    results = await db.execute(query)
    return results.scalars().all()
