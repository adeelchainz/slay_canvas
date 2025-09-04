from fastapi import Header, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from datetime import datetime, timedelta
from typing import Dict, Any
from app.core.config import settings

# Create a HTTPBearer security scheme
security = HTTPBearer(
    scheme_name="Bearer Token",
    description="Enter your JWT Bearer token",
    auto_error=True
)


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


def get_token_from_credentials(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract token from HTTPBearer credentials"""
    return credentials.credentials


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        sub = payload.get('sub')
        return int(sub)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token expired')
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
