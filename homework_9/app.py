from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from homework_9.routes import cve
from homework_9.database import engine, init_db
from homework_9.exceptions import custom_exception_handler, http_exception_handler, http_validation_handler
from fastapi.exceptions import ResponseValidationError
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Початок життєвого циклу: ініціалізація бази даних
    await init_db()
    yield
    # Кінець життєвого циклу: закриття з'єднання з базою даних
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

# CORS налаштування, якщо необхідно
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Підключення роутів
app.include_router(cve.router, prefix="/cves", tags=["cves"])

# Налаштування обробників помилок
app.add_exception_handler(Exception, custom_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(ResponseValidationError, http_validation_handler)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
