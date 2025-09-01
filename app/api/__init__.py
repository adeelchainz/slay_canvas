from fastapi import APIRouter

from app.api import auth, users, media, ai

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(media.router, prefix="/media", tags=["media"])
router.include_router(ai.router, prefix="/ai", tags=["ai"])
