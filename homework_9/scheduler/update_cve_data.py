import aiohttp
import time
import json
from asyncio import run
from dateutil import parser
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
import asyncio
from aiohttp import ClientError
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


async def fetch_delta_json():
    try:
        DELTA_URL = "https://raw.githubusercontent.com/CVEProject/cvelistV5/main/cves/delta.json"
        async with aiohttp.ClientSession() as http_session:
            async with http_session.get(DELTA_URL) as response:
                if response.status == 200:
                    data = await response.read()
                    return json.loads(data)
                return {}
    except Exception as e:
        scheduler._logger.error(f"Error fetching JSON: {e}")
        return {}

async def process_new_cves():
    try:
        delta_data = await fetch_delta_json()
        if delta_data and 'new' in delta_data:
            for cve_data in delta_data['new']:
                cve_link = cve_data.get("githubLink")
                if not cve_link:
                    continue

                await process_cve_link(cve_link)
        if delta_data and 'updated' in delta_data:
            for cve_data in delta_data['updated']:
                cve_link = cve_data.get("githubLink")
                if not cve_link:
                    continue

                await process_cve_link(cve_link)
    except Exception as e:
        scheduler._logger.error(f"process_new_cves: {e}")
        return {}

async def process_cve_link(cve_link: str):
    try:
        async with aiohttp.ClientSession() as http_session:
            async with http_session.get(cve_link) as response:
                if response.status == 200:
                    data = await response.text()
                    json_data = json.loads(data)
                    return await save_cve(json_data)
    except Exception as e:
        scheduler._logger.error(f"Error process_cve_link: {e}")

async def save_cve(cve_data: dict):
    if not isinstance(cve_data, dict) or not cve_data.get('cveMetadata'):
        return

    cve_id = cve_data['cveMetadata']['cveId']
    if cve_id:
        new_cve = {
            "id": cve_id,
            "date_published": get_date_published(cve_data),
            "date_updated": get_date_updated(cve_data),
            "title": cve_data['cveMetadata'].get('assignerShortName'),
            "description": get_description(cve_data),
            "problem_types": get_problem_types(cve_data)
        }
        async with aiohttp.ClientSession() as http_session:
            async with http_session.post("http://127.0.0.1:8001/cves", json=new_cve) as response:
                if response.status == 200:
                    scheduler._logger.info('new cve_data added')
                else:
                    data = await response.text()
                    scheduler._logger.info(json.loads(data))


def get_date_published(data):
    try:
        date_published = parser.parse(data['cveMetadata'].get('datePublished'))
    except Exception:
        return
    return date_published.replace(tzinfo=None).isoformat()


def get_date_updated(data):
    try:
        date_updated = parser.parse(data['cveMetadata'].get('dateUpdated'))
    except Exception:
        return
    return date_updated.replace(tzinfo=None).isoformat()


def get_description(data):
    try:
        return data['containers']['cna']['descriptions'][0].get('value')
    except Exception as e:
        return None


def get_problem_types(data):
    try:
        return data['containers']['cna'].get('problemTypes')
    except Exception as e:
        return None


async def scheduled_cve_update():
    try:
        await process_new_cves()
    except Exception as e:
        logger.error(f"Error occurred during fetch_cve_updates: {e}")

async def main():
    pass

if __name__ == '__main__':

    try:
        # run(main())
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
