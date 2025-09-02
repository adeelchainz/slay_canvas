from fastapi import Header, HTTPException, status, Depends
from jose import jwt
from datetime import datetime, timedelta
from typing import Dict, Any
from app.core.config import settings


def create_access_token(data: Dict[str, Any], expires_delta: timedelta = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)  # Default 24 hours
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def get_token_from_header(authorization: str | None = Header(None)) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Missing Authorization header')
    parts = authorization.split()
    if parts[0].lower() != 'bearer' or len(parts) != 2:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Authorization header')
    return parts[1]


def get_current_user_id(token: str = Depends(get_token_from_header)) -> int:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        sub = payload.get('sub')
        return int(sub)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token expired')
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
