from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
import os
import uuid
from datetime import datetime

from app.models.media import MediaFile, Project, Media
from app.schemas.media import MediaFileCreate, MediaFileUpdate, ProjectCreate, ProjectUpdate, MediaCreate
from app.core.config import settings
from app.utils.storage import save_upload


class MediaService:
    async def get_media_file(self, db: AsyncSession, media_file_id: int) -> Optional[MediaFile]:
        """Get media file by ID."""
        result = await db.execute(
            select(MediaFile)
            .where(MediaFile.id == media_file_id)
            .options(selectinload(MediaFile.user), selectinload(MediaFile.project))
        )
        return result.scalar_one_or_none()
    
    async def get_media_files_by_user(
        self, 
        db: AsyncSession, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        file_type: Optional[str] = None
    ) -> List[MediaFile]:
        """Get media files for a user."""
        query = select(MediaFile).where(MediaFile.user_id == user_id)
        
        if file_type:
            query = query.where(MediaFile.file_type == file_type)
        
        query = query.offset(skip).limit(limit).options(
            selectinload(MediaFile.project)
        )
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_media_files_by_project(
        self, 
        db: AsyncSession, 
        project_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[MediaFile]:
        """Get media files for a project."""
        result = await db.execute(
            select(MediaFile)
            .where(MediaFile.project_id == project_id)
            .offset(skip)
            .limit(limit)
            .options(selectinload(MediaFile.user))
        )
        return result.scalars().all()
    
    async def create_media_file(self, db: AsyncSession, media_data: MediaFileCreate, user_id: int) -> MediaFile:
        """Create a new media file."""
        media_file = MediaFile(
            **media_data.dict(),
            user_id=user_id,
            processing_status="pending",
            transcription_status="pending",
            ai_analysis_status="pending"
        )
        
        db.add(media_file)
        await db.commit()
        await db.refresh(media_file)
        return media_file
    
    async def update_media_file(
        self, 
        db: AsyncSession, 
        media_file_id: int, 
        media_data: MediaFileUpdate
    ) -> Optional[MediaFile]:
        """Update media file."""
        media_file = await self.get_media_file(db, media_file_id)
        if not media_file:
            return None
        
        update_data = media_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(media_file, field, value)
        
        await db.commit()
        await db.refresh(media_file)
        return media_file
    
    async def delete_media_file(self, db: AsyncSession, media_file_id: int) -> bool:
        """Delete media file."""
        media_file = await self.get_media_file(db, media_file_id)
        if not media_file:
            return False
        
        # Delete physical file
        try:
            if os.path.exists(media_file.file_path):
                os.remove(media_file.file_path)
        except Exception:
            pass  # Continue with database deletion even if file deletion fails
        
        await db.delete(media_file)
        await db.commit()
        return True
    
    async def search_media_files(
        self, 
        db: AsyncSession, 
        user_id: int, 
        query: str, 
        file_types: Optional[List[str]] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[MediaFile]:
        """Search media files by filename, tags, or transcription."""
        base_query = select(MediaFile).where(MediaFile.user_id == user_id)
        
        # Add file type filter
        if file_types:
            base_query = base_query.where(MediaFile.file_type.in_(file_types))
        
        # Add search conditions
        search_conditions = [
            MediaFile.filename.ilike(f"%{query}%"),
            MediaFile.original_filename.ilike(f"%{query}%"),
            MediaFile.transcription_text.ilike(f"%{query}%"),
            MediaFile.summary.ilike(f"%{query}%")
        ]
        
        base_query = base_query.where(
            or_(*search_conditions)
        ).offset(skip).limit(limit)
        
        result = await db.execute(base_query)
        return result.scalars().all()
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """Generate unique filename for upload."""
        file_extension = os.path.splitext(original_filename)[1]
        unique_id = str(uuid.uuid4())
        return f"{unique_id}{file_extension}"
    
    def get_file_type_from_mime(self, mime_type: str) -> str:
        """Determine file type from MIME type."""
        if mime_type.startswith('image/'):
            return 'image'
        elif mime_type.startswith('video/'):
            return 'video'
        elif mime_type.startswith('audio/'):
            return 'audio'
        elif mime_type in ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            return 'document'
        else:
            return 'other'
    
    async def get_processing_statistics(self, db: AsyncSession, user_id: int) -> Dict[str, Any]:
        """Get processing statistics for user's media files."""
        result = await db.execute(
            select(MediaFile).where(MediaFile.user_id == user_id)
        )
        media_files = result.scalars().all()
        
        stats = {
            'total_files': len(media_files),
            'by_type': {},
            'by_status': {},
            'total_size': 0,
            'processed_count': 0
        }
        
        for media_file in media_files:
            # Count by type
            file_type = media_file.file_type
            stats['by_type'][file_type] = stats['by_type'].get(file_type, 0) + 1
            
            # Count by status
            status = media_file.processing_status
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            
            # Sum file sizes
            stats['total_size'] += media_file.file_size
            
            # Count processed files
            if status == 'completed':
                stats['processed_count'] += 1
        
        return stats


class ProjectService:
    async def get_project(self, db: AsyncSession, project_id: int) -> Optional[Project]:
        """Get project by ID."""
        result = await db.execute(
            select(Project)
            .where(Project.id == project_id)
            .options(selectinload(Project.user), selectinload(Project.media_files))
        )
        return result.scalar_one_or_none()
    
    async def get_projects_by_user(
        self, 
        db: AsyncSession, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Project]:
        """Get projects for a user."""
        result = await db.execute(
            select(Project)
            .where(Project.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .options(selectinload(Project.media_files))
        )
        return result.scalars().all()
    
    async def create_project(self, db: AsyncSession, project_data: ProjectCreate, user_id: int) -> Project:
        """Create a new project."""
        project = Project(
            **project_data.dict(),
            user_id=user_id
        )
        
        db.add(project)
        await db.commit()
        await db.refresh(project)
        return project
    
    async def update_project(
        self, 
        db: AsyncSession, 
        project_id: int, 
        project_data: ProjectUpdate
    ) -> Optional[Project]:
        """Update project."""
        project = await self.get_project(db, project_id)
        if not project:
            return None
        
        update_data = project_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        
        await db.commit()
        await db.refresh(project)
        return project
    
    async def delete_project(self, db: AsyncSession, project_id: int) -> bool:
        """Delete project."""
        project = await self.get_project(db, project_id)
        if not project:
            return False
        
        await db.delete(project)
        await db.commit()
        return True


# Legacy function for backward compatibility
async def create_media(db: AsyncSession, media_in: MediaCreate, file_bytes: bytes, uploaded_by: int | None = None) -> Media:
    """Legacy function - use MediaService.create_media_file instead."""
    path, rel = save_upload(file_bytes, media_in.filename, subfolder=media_in.media_type)
    m = Media(filename=media_in.filename, path=path, media_type=media_in.media_type, uploaded_by=uploaded_by)
    async with db.begin():
        db.add(m)
        await db.flush()
    return m
