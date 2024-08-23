import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from logging.config import fileConfig
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Завантаження змінних з .env файлу
load_dotenv()

# Налаштування логування Alembic
from models import CVE as Base
fileConfig(context.config.config_file_name)

# Отримуємо URL бази даних з конфігурації
config = context.config
DATABASE_URL = os.getenv("DATABASE_URL")
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Створення асинхронного двигуна
connectable = create_async_engine(DATABASE_URL, echo=True)

async def run_migrations_online():
    # Використовуємо асинхронний контекстний менеджер для з'єднання
    async with connectable.connect() as connection:
        # Використовуємо run_sync для роботи з інспекцією або іншими синхронними операціями
        await connection.run_sync(do_run_migrations)

def do_run_migrations(connection):
    """Запуск міграцій у синхронному контексті"""
    context.configure(connection=connection, target_metadata=Base.metadata)

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_offline():
    """Запуск міграцій в оффлайн-режимі"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=Base.metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    # Викликаємо асинхронну функцію для онлайн міграцій
    asyncio.run(run_migrations_online())
