from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.schemas.media import MediaCreate, MediaRead
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.media_service import create_media
from app.utils.auth import get_current_user_id

router = APIRouter()


@router.post('/upload', response_model=MediaRead)
async def upload_media(file: UploadFile = File(...), media_type: str = 'image', db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    content = await file.read()
    media_in = MediaCreate(filename=file.filename, media_type=media_type)
    media = await create_media(db, media_in, content, uploaded_by=user_id)
    return media
