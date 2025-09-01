from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserRead
from app.db.session import get_db
from app.services.user_service import get_user_by_id
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.auth import get_current_user_id

router = APIRouter()


@router.get('/me', response_model=UserRead)
async def read_profile(db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user
