from fastapi import APIRouter

from src.api.v1.endpoints import (
    auth_router,
    oauth_router,
    profile_router,
    recovery_router,
    registration_router,
)

router = APIRouter(prefix="/api/v1")

router.include_router(registration_router)
router.include_router(recovery_router)
router.include_router(auth_router)
router.include_router(oauth_router)
router.include_router(profile_router)
