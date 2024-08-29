from fastapi import APIRouter
from .cve import cve_api

api = APIRouter(prefix="/api")
api.include_router(cve_api)
