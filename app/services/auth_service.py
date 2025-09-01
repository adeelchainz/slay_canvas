import jwt
from datetime import datetime, timedelta
from app.core.config import settings
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


JWT_ALGORITHM = 'HS256'


def create_access_token(subject: str, expires_delta: int = 60 * 60 * 24 * 7) -> str:
    now = datetime.utcnow()
    payload = {
        'sub': subject,
        'iat': now,
        'exp': now + timedelta(seconds=expires_delta),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)


async def login_or_create_google_user(userinfo: dict, db: AsyncSession = None) -> str:
    """Given Google userinfo, ensure a local user exists and return a JWT."""
    email = userinfo.get('email')
    async with db.begin():
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                email=email,
                full_name=userinfo.get('name'),
                avatar_url=userinfo.get('picture'),
                provider='google',
            )
            db.add(user)
            await db.flush()
    token = create_access_token(subject=str(user.id))
    return token
