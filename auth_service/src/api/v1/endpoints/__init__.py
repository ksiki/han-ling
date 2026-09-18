from .auth import router as auth_router
from .oauth import router as oauth_router
from .profile import router as profile_router
from .recovery import router as recovery_router
from .registration import router as registration_router

__all__ = [
    "auth_router",
    "oauth_router",
    "profile_router",
    "recovery_router",
    "registration_router",
]
