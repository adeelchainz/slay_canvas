"""
AI Orchestrator for MediaBoard AI
Coordinates all AI workflows and provides high-level interface
"""

from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from .workflows import MediaProcessingWorkflow, CollaborativeWorkflow, RealTimeAnalysisWorkflow
from .agents import AgentState
from app.models.media import MediaFile
from app.schemas.media import MediaFileUpdate


class AIOrchestrator:
    """Main orchestrator for all AI operations"""
    
    def __init__(self):
        self.media_workflow = MediaProcessingWorkflow()
        self.collaborative_workflow = CollaborativeWorkflow()
        self.realtime_workflow = RealTimeAnalysisWorkflow()
        
        # Keep track of processing jobs
        self.active_jobs: Dict[int, AgentState] = {}
        self.job_history: List[Dict[str, Any]] = []
    
    async def process_media_file(self, db: AsyncSession, media_file: MediaFile) -> AgentState:
        """Process a media file through the complete AI workflow"""
        
        try:
            # Update status to processing
            await self._update_media_status(db, media_file.id, "processing")
            
            # Add to active jobs
            self.active_jobs[media_file.id] = AgentState(
                media_file_id=media_file.id,
                file_path=media_file.file_path,
                file_type=media_file.file_type,
                processing_status="started"
            )
            
            # Run the workflow
            result = await self.media_workflow.process_media(
                media_file_id=media_file.id,
                file_path=media_file.file_path,
                file_type=media_file.file_type,
                metadata=media_file.metadata or {}
            )
            
            # Update database with results
            await self._save_ai_results(db, media_file.id, result)
            
            # Remove from active jobs and add to history
            if media_file.id in self.active_jobs:
                del self.active_jobs[media_file.id]
            
            self.job_history.append({
                "media_file_id": media_file.id,
                "completed_at": datetime.utcnow(),
                "status": result.processing_status,
                "errors": result.errors
            })
            
            return result
            
        except Exception as e:
            # Handle errors
            await self._update_media_status(db, media_file.id, "failed")
            
            error_state = AgentState(
                media_file_id=media_file.id,
                file_path=media_file.file_path,
                file_type=media_file.file_type,
                processing_status="error",
                errors=[str(e)]
            )
            
            if media_file.id in self.active_jobs:
                del self.active_jobs[media_file.id]
            
            return error_state
    
    async def get_processing_status(self, media_file_id: int) -> Optional[Dict[str, Any]]:
        """Get current processing status for a media file"""
        
        if media_file_id in self.active_jobs:
            state = self.active_jobs[media_file_id]
            return {
                "media_file_id": media_file_id,
                "status": state.processing_status,
                "progress": self._calculate_progress(state),
                "errors": state.errors,
                "is_active": True
            }
        
        # Check history
        for job in reversed(self.job_history):
            if job["media_file_id"] == media_file_id:
                return {
                    "media_file_id": media_file_id,
                    "status": job["status"],
                    "completed_at": job["completed_at"],
                    "errors": job["errors"],
                    "is_active": False
                }
        
        return None
    
    async def analyze_in_realtime(self, file_info: Dict[str, Any]) -> AgentState:
        """Perform real-time analysis for immediate feedback"""
        
        return await self.realtime_workflow.analyze_in_realtime(file_info)
    
    async def collaborate_on_content(self, content: str, user_feedback: Dict[str, Any]) -> AgentState:
        """Run collaborative workflow"""
        
        return await self.collaborative_workflow.collaborate_on_content(content, user_feedback)
    
    async def generate_content_variations(self, db: AsyncSession, media_file_id: int, content_types: List[str]) -> Dict[str, str]:
        """Generate specific types of content for a media file"""
        
        # This would be extended to generate specific content types on demand
        content_agent = self.media_workflow.content_generation_agent
        
        # For now, return a basic implementation
        variations = {}
        for content_type in content_types:
            variations[content_type] = f"Generated {content_type} content for media file {media_file_id}"
        
        return variations
    
    async def batch_process_media(self, db: AsyncSession, media_files: List[MediaFile]) -> List[AgentState]:
        """Process multiple media files in batch"""
        
        tasks = []
        for media_file in media_files:
            task = self.process_media_file(db, media_file)
            tasks.append(task)
        
        # Process in parallel with concurrency limit
        semaphore = asyncio.Semaphore(3)  # Limit to 3 concurrent processes
        
        async def process_with_semaphore(media_file):
            async with semaphore:
                return await self.process_media_file(db, media_file)
        
        limited_tasks = [process_with_semaphore(mf) for mf in media_files]
        results = await asyncio.gather(*limited_tasks, return_exceptions=True)
        
        return results
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get AI system statistics"""
        
        total_processed = len(self.job_history)
        active_jobs = len(self.active_jobs)
        
        # Calculate success rate
        successful_jobs = sum(1 for job in self.job_history if job["status"] == "completed")
        success_rate = successful_jobs / total_processed if total_processed > 0 else 0
        
        return {
            "total_processed": total_processed,
            "active_jobs": active_jobs,
            "success_rate": success_rate,
            "average_processing_time": self._calculate_avg_processing_time(),
            "system_status": "operational" if success_rate > 0.8 else "degraded"
        }
    
    async def _update_media_status(self, db: AsyncSession, media_file_id: int, status: str):
        """Update media file processing status in database"""
        
        update_data = MediaFileUpdate(processing_status=status)
        
        # This would be implemented with the media service
        # For now, we'll skip the actual database update
        pass
    
    async def _save_ai_results(self, db: AsyncSession, media_file_id: int, result: AgentState):
        """Save AI processing results to database"""
        
        update_data = MediaFileUpdate(
            processing_status=result.processing_status,
            transcription_text=result.transcription,
            summary=result.summary,
            tags=result.tags,
            ai_insights=result.insights,
            processed_at=datetime.utcnow()
        )
        
        # This would be implemented with the media service
        # For now, we'll skip the actual database update
        pass
    
    def _calculate_progress(self, state: AgentState) -> float:
        """Calculate processing progress based on state"""
        
        progress_map = {
            "pending": 0.0,
            "started": 0.1,
            "transcribed": 0.4,
            "analyzed": 0.7,
            "completed": 1.0,
            "error": 0.0
        }
        
        return progress_map.get(state.processing_status, 0.0)
    
    def _calculate_avg_processing_time(self) -> float:
        """Calculate average processing time"""
        
        # This would calculate actual processing times
        # For now, return a mock value
        return 45.5  # seconds
