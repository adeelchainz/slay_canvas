"""
Pydantic schemas for Board operations
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class BoardBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Board title")
    description: Optional[str] = Field(None, max_length=1000, description="Board description")
    is_private: bool = Field(True, description="Whether the board is private")
    
    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty or just whitespace')
        return v.strip()


class BoardCreate(BoardBase):
    """Schema for creating a new board"""
    pass


class BoardUpdate(BaseModel):
    """Schema for updating an existing board"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    is_private: Optional[bool] = None
    
    @validator('title')
    def validate_title(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Title cannot be empty or just whitespace')
        return v.strip() if v else v


class BoardInDB(BoardBase):
    """Schema for board data in database"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class BoardPublic(BaseModel):
    """Schema for board data returned to users"""
    id: int
    title: str
    description: Optional[str]
    is_private: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class BoardListResponse(BaseModel):
    """Schema for board list response"""
    boards: list[BoardPublic]
    total: int
    page: int
    per_page: int
    
    
class BoardResponse(BaseModel):
    """Schema for single board response"""
    message: str
    board: BoardPublic
