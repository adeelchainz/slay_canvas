from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class MediaFileBase(BaseModel):
    filename: str
    original_filename: str
    file_type: str
    mime_type: str


class MediaFileCreate(MediaFileBase):
    file_path: str
    file_size: int
    project_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = {}


class MediaFileUpdate(BaseModel):
    filename: Optional[str] = None
    processing_status: Optional[str] = None
    transcription_status: Optional[str] = None
    ai_analysis_status: Optional[str] = None
    transcription_text: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    ai_insights: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class MediaFileInDB(MediaFileBase):
    id: int
    file_path: str
    file_size: int
    processing_status: str
    transcription_status: str
    ai_analysis_status: str
    duration: Optional[float]
    dimensions: Optional[Dict[str, int]]
    metadata: Dict[str, Any]
    transcription_text: Optional[str]
    summary: Optional[str]
    tags: List[str]
    ai_insights: Dict[str, Any]
    user_id: int
    project_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class MediaFile(MediaFileInDB):
    pass


class MediaFilePublic(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_type: str
    mime_type: str
    file_size: int
    processing_status: str
    transcription_status: str
    ai_analysis_status: str
    duration: Optional[float]
    dimensions: Optional[Dict[str, int]]
    tags: List[str]
    project_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Project schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: Optional[bool] = False


class ProjectCreate(ProjectBase):
    settings: Optional[Dict[str, Any]] = {}
    canvas_data: Optional[Dict[str, Any]] = {}


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None
    canvas_data: Optional[Dict[str, Any]] = None
    collaborators: Optional[List[int]] = None


class ProjectInDB(ProjectBase):
    id: int
    settings: Dict[str, Any]
    canvas_data: Dict[str, Any]
    collaborators: List[int]
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class Project(ProjectInDB):
    media_files: Optional[List[MediaFilePublic]] = []


class ProjectPublic(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_public: bool
    created_at: datetime
    media_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


# Legacy schemas for backward compatibility
class MediaCreate(BaseModel):
    filename: str
    media_type: str


class MediaRead(BaseModel):
    id: int
    filename: str
    path: str
    media_type: str

    class Config:
        from_attributes = True


# Upload and processing schemas
class UploadResponse(BaseModel):
    media_file: MediaFilePublic
    upload_url: Optional[str] = None
    message: str = "File uploaded successfully"


class ProcessingStatus(BaseModel):
    media_id: int
    processing_status: str
    transcription_status: str
    ai_analysis_status: str
    progress: Optional[float] = None
    error_message: Optional[str] = None
