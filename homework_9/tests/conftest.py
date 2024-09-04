import pytest_asyncio
import httpx
from homework_9.app import app
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from homework_9.models import Base
from homework_9.dependencies import get_db
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

@pytest_asyncio.fixture(scope="module")
async def async_session():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    session = async_session()

    try:
        yield session
    finally:
        await session.close()
        await engine.dispose()

@pytest_asyncio.fixture(scope="module")
async def test_app(async_session):
    def _get_test_db():
        try:
            yield async_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()

@pytest_asyncio.fixture(scope="module")
async def client(test_app):
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# Додано фікстуру для правильного керування подієвим кільцем
@pytest_asyncio.fixture(scope="module", autouse=True)
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()