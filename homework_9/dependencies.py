from homework_9.database import SessionLocal

async def get_db():
    async with SessionLocal() as session:
        yield session
