from fastapi import APIRouter

from .endpoints.service import router as service_router

api_router = APIRouter()

api_router.include_router(service_router, tags=["service"])
