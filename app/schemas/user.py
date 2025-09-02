from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    name: str  # Changed from full_name to name
    is_active: Optional[bool] = True
    is_verified: Optional[bool] = False


class UserCreate(UserBase):
    password: Optional[str] = None  # Optional for OAuth users
    google_id: Optional[str] = None
    avatar_url: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None  # Changed from full_name to name
    is_active: Optional[bool] = None
    avatar_url: Optional[str] = None
    profile_data: Optional[Dict[str, Any]] = None


class UserInDB(UserBase):
    id: int
    hashed_password: Optional[str]
    google_id: Optional[str]
    avatar_url: Optional[str]
    provider: Optional[str]
    created_at: datetime
    updated_at: datetime
    profile_data: Dict[str, Any]
    subscription_plan: str
    subscription_status: str
    created_at: datetime
    updated_at: Optional[datetime]
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


class User(UserInDB):
    pass


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str]
    provider: Optional[str]
    subscription_plan: str
    subscription_status: str
    created_at: datetime
    updated_at: Optional[datetime]
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    avatar_url: Optional[str]
    is_active: bool
    subscription_plan: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# OAuth specific schemas
class GoogleUserInfo(BaseModel):
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    verified_email: bool = False


class OAuthUserCreate(BaseModel):
    email: EmailStr
    full_name: str
    google_id: Optional[str] = None
    avatar_url: Optional[str] = None
    provider: str = "google"


# Authentication response schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserPublic


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
