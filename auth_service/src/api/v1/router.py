from fastapi import APIRouter

from src.api.v1.endpoints import recovery_router, registration_router

router = APIRouter(prefix="/v1")

router.include_router(registration_router)
router.include_router(recovery_router)
