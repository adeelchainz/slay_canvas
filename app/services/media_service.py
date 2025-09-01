from sqlalchemy.ext.asyncio import AsyncSession
from app.models.media import Media
from app.schemas.media import MediaCreate
from app.utils.storage import save_upload


async def create_media(db: AsyncSession, media_in: MediaCreate, file_bytes: bytes, uploaded_by: int | None = None) -> Media:
    path, rel = save_upload(file_bytes, media_in.filename, subfolder=media_in.media_type)
    m = Media(filename=media_in.filename, path=path, media_type=media_in.media_type, uploaded_by=uploaded_by)
    async with db.begin():
        db.add(m)
        await db.flush()
    return m
