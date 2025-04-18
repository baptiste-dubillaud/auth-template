import os

from fastapi import APIRouter

from routers.auth.standard import router as email_password_router
from routers.auth.microsoft import router as microsoft_router
from routers.auth.google import router as google_router
from routers.auth.facebook import router as facebook_router
from routers.auth.apple import router as apple_router

from internal.config.config import (
    AUTH_EMAIL_PASSWORD,
    AUTH_MICROSOFT,
    AUTH_GOOGLE,
    AUTH_FACEBOOK,
    AUTH_APPLE,
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# Include the standard router last to avoid conflicts with other routes
# Check if the authentication methods are enabled
if AUTH_EMAIL_PASSWORD == "true":
    router.include_router(email_password_router)
if AUTH_MICROSOFT == "true":
    router.include_router(microsoft_router)
if AUTH_GOOGLE == "true":
    router.include_router(google_router)
if AUTH_FACEBOOK == "true":
    router.include_router(facebook_router)
if AUTH_APPLE == "true":
    router.include_router(apple_router)