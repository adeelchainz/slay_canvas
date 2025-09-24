from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
from datetime import datetime


class AssetBase(BaseModel):
    url: Optional[HttpUrl] = None
    asset_metadata: Optional[Dict[str, Any]] = {}
    is_active: Optional[bool] = True


class AssetCreate(AssetBase):
    content: Optional[str] = None   # <-- added for texts


class AssetUpdate(BaseModel):
    url: Optional[HttpUrl] = None
    asset_metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    content: Optional[str] = None   # <-- added for texts


class AssetRead(AssetBase):
    id: int
    type: str
    workspace_id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    content: Optional[str] = None   # <-- include in response

    class Config:
        orm_mode = True
