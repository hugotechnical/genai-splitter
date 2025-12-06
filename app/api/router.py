from fastapi import APIRouter
from app.api.v1.splitter import splitter_router

routers = APIRouter()

routers.include_router(splitter_router, tags= ["Splitter Services"])
