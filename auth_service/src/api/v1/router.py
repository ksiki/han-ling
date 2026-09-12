from fastapi import APIRouter

from src.api.v1.endpoints import login_router, register_router

router = APIRouter(prefix="/v1")

router.include_router(login_router, prefix="/login")
router.include_router(register_router, prefix="/register")
