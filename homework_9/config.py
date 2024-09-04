from pydantic import BaseModel

class Settings(BaseModel):
    db_uri: str = "postgresql+asyncpg://user:password@127.0.0.1:5432/cve_database"
