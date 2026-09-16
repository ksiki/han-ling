from fastapi import APIRouter

from src.api.v1.endpoints import (
    auth_router,
    oauth_router,
    recovery_router,
    registration_router,
    users_router,
)

router = APIRouter(prefix="/v1")

router.include_router(registration_router)
router.include_router(recovery_router)
router.include_router(auth_router)
router.include_router(oauth_router)
router.include_router(users_router)
