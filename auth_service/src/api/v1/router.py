from fastapi import APIRouter

from src.api.v1.endpoints import registration_router

router = APIRouter(prefix="/v1")

router.include_router(registration_router)
