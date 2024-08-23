import os
import logging
import aiofiles
import asyncio
import json
import time
import argparse
from dateutil import parser
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert
from dotenv import load_dotenv
from models import CVE
from contextlib import contextmanager


logging.getLogger('sqlalchemy.engine.Engine').setLevel(logging.WARNING)
# Завантажуємо змінні з .env
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def process_file(file_path: str):
    async with aiofiles.open(file_path, mode='r') as file:
        contents = await file.read()
        data = json.loads(contents)
        if not isinstance(data, dict) or not data.get('cveMetadata'):
            return

        return {
            'id': data['cveMetadata'].get('cveId'),
            'date_published': get_date_published(data),
            'date_updated': get_date_updated(data),
            'title': data['cveMetadata'].get('assignerShortName'),
            'description': get_description(data),
            'problem_types': get_problem_types(data)
        }


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


async def process_directory(directory: str, batch_size: int = 1000):
    cve_records = []
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith(".json"):
                file_path = os.path.join(root, file_name)
                cve_record = await process_file(file_path)
                if not cve_record:
                    continue

                cve_records.append(cve_record)

                if len(cve_records) >= batch_size:
                    await insert_batch(cve_records)
                    cve_records = []

    if cve_records:
        await insert_batch(cve_records)


async def insert_batch(records):
    async with SessionLocal() as session:
        async with session.begin():
            stmt = insert(CVE).values(records).on_conflict_do_nothing()
            await session.execute(stmt)
            await session.commit()


async def main(directory: str):
    await process_directory(directory)


@contextmanager
def timer(msg: str):
    start = time.perf_counter()
    yield
    print(f"{msg} took {time.perf_counter() - start:.2f} seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process CVE JSON files and store them in a database.")
    parser.add_argument("directory", type=str, help="The path to the directory containing CVE JSON files.")

    args = parser.parse_args()
    with timer("Download CVE into DB"):
        asyncio.run(main(args.directory))
