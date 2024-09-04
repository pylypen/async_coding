import aiohttp
import time
import json
from asyncio import run
from dateutil import parser
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from fastapi import Depends, HTTPException
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
import logging
import asyncio
from aiohttp import ClientError
import requests
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

#############Loging############
logging.basicConfig(level=logging.INFO)

# Set up a specific logger for apscheduler
logging.getLogger('apscheduler').setLevel(logging.INFO)
logger = logging.getLogger(__name__)
#########################

############DB conf#############
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Text, DateTime, JSON

Base = declarative_base()


class CVE(Base):
    __tablename__ = 'cves'

    id = Column(String, primary_key=True)
    date_published = Column(DateTime)
    date_updated = Column(DateTime)
    title = Column(String)
    description = Column(Text)
    problem_types = Column(JSON)
#####################

@asynccontextmanager
async def get_db() -> AsyncSession:
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    session = async_session()

    try:
        yield session
    finally:
        await session.close()
        await engine.dispose()

##########################
def fetch_delta_json():
    DELTA_URL = "https://raw.githubusercontent.com/CVEProject/cvelistV5/main/cves/delta.json"
    try:
        response = requests.get(DELTA_URL)
        return response.json()  # Parses the response as JSON
    except requests.exceptions.RequestException as e:
        scheduler._logger.error(f"Error fetching JSON: {e}")
        return {}

async def process_new_cves(session: AsyncSession):
    try:
        delta_data = fetch_delta_json()
        if delta_data and 'new' in delta_data:
            for cve_data in delta_data['new']:
                cve_link = cve_data.get("githubLink")
                if not cve_link:
                    continue

                await process_cve_link(session, cve_link)
        if delta_data and 'updated' in delta_data:
            for cve_data in delta_data['updated']:
                cve_link = cve_data.get("githubLink")
                if not cve_link:
                    continue

                await process_cve_link(session, cve_link)
    except Exception as e:
        scheduler._logger.error(f"process_new_cves: {e}")
        return {}

async def process_cve_link(session: AsyncSession, cve_link: str):
    try:
        response = requests.get(cve_link)

        return await save_cve(session, response.json())
    except requests.exceptions.RequestException as e:
        return {}

async def save_cve(session: AsyncSession, cve_data: dict):
    if not isinstance(cve_data, dict) or not cve_data.get('cveMetadata'):
        return

    cve_id = cve_data['cveMetadata']['cveId']
    query = select(CVE).filter(CVE.id == cve_id)
    result = await session.execute(query)
    cve = result.scalar_one_or_none()

    if cve is None:
        new_cve = CVE(
            id=cve_id,
            date_published=get_date_published(cve_data),
            date_updated=get_date_updated(cve_data),
            title=cve_data['cveMetadata'].get('assignerShortName'),
            description=get_description(cve_data),
            problem_types=get_problem_types(cve_data)
        )
        session.add(new_cve)
    else:
        scheduler._logger.info('cve_data exist')

    await session.commit()

def get_date_published(data):
    try:
        date_published = parser.parse(data['cveMetadata'].get('datePublished'))
    except Exception:
        return
    return date_published.replace(tzinfo=None)


def get_date_updated(data):
    try:
        date_updated = parser.parse(data['cveMetadata'].get('dateUpdated'))
    except Exception:
        return
    return date_updated.replace(tzinfo=None)


def get_description(data):
    try:
        return data['containers']['cna']['descriptions'][0].get('value')
    except Exception as e:
        return None


def get_problem_types(data):
    try:
        return json.dumps(data['containers']['cna'].get('problemTypes'))
    except Exception as e:
        return None


async def scheduled_cve_update():
    try:
        async with get_db() as session:
            await process_new_cves(session)
    except Exception as e:
        logger.error(f"Error occurred during fetch_cve_updates: {e}")


if __name__ == '__main__':
    try:
        # run(scheduled_cve_update())
        scheduler = AsyncIOScheduler()
        scheduler.add_job(scheduled_cve_update, trigger='interval', minutes=1)
        scheduler.start()
    except Exception as e:
        print(e)


    try:
        scheduler.print_jobs()
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
