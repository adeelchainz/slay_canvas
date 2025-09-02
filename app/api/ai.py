from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.config import settings
from app.db.session import get_db
from app.services.auth_service import get_current_user
from app.services.media_service import MediaService
from app.models.user import User
from ai.orchestrator import AIOrchestrator

# Legacy imports for backward compatibility
from app.schemas.ai import ChatRequest, ChatResponse
from app.utils.auth import get_current_user_id
from engine.adapter import engine
from app.services import ai_service

router = APIRouter()
security = HTTPBearer()

# Initialize AI orchestrator
ai_orchestrator = AIOrchestrator()


class ProcessMediaRequest(BaseModel):
    media_file_id: int
    force_reprocess: bool = False


class ContentGenerationRequest(BaseModel):
    media_file_id: int
    content_types: List[str]  # ["blog_post", "social_media", "script", "q_and_a"]


class CollaborationRequest(BaseModel):
    content: str
    user_feedback: Dict[str, Any]


class ProcessingStatusResponse(BaseModel):
    media_file_id: int
    status: str
    progress: Optional[float] = None
    errors: List[str] = []
    is_active: bool
    completed_at: Optional[str] = None


# New AI endpoints
@router.post("/process-media", response_model=Dict[str, Any])
async def process_media_file(
    request: ProcessMediaRequest,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Process a media file through AI pipeline"""
    
    # Verify user authentication
    user = await get_current_user(db, credentials.credentials)
    
    # Get media file
    media_service = MediaService()
    media_file = await media_service.get_media_file(db, request.media_file_id)
    
    if not media_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media file not found"
        )
    
    # Check if user owns the media file
    if media_file.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Check if already processing
    current_status = await ai_orchestrator.get_processing_status(request.media_file_id)
    if current_status and current_status["is_active"] and not request.force_reprocess:
        return {
            "message": "Media file is already being processed",
            "status": current_status
        }
    
    # Start processing in background
    background_tasks.add_task(
        ai_orchestrator.process_media_file,
        db,
        media_file
    )
    
    return {
        "message": "Media processing started",
        "media_file_id": request.media_file_id,
        "status": "started"
    }


@router.get("/processing-status/{media_file_id}", response_model=ProcessingStatusResponse)
async def get_processing_status(
    media_file_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get processing status for a media file"""
    
    user = await get_current_user(db, credentials.credentials)
    
    # Verify user owns the media file
    media_service = MediaService()
    media_file = await media_service.get_media_file(db, media_file_id)
    
    if not media_file or media_file.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media file not found"
        )
    
    status_info = await ai_orchestrator.get_processing_status(media_file_id)
    
    if not status_info:
        return ProcessingStatusResponse(
            media_file_id=media_file_id,
            status="not_started",
            is_active=False
        )
    
    return ProcessingStatusResponse(**status_info)


@router.post("/generate-content", response_model=Dict[str, str])
async def generate_content_variations(
    request: ContentGenerationRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Generate specific types of content for a media file"""
    
    user = await get_current_user(db, credentials.credentials)
    
    # Verify user owns the media file
    media_service = MediaService()
    media_file = await media_service.get_media_file(db, request.media_file_id)
    
    if not media_file or media_file.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media file not found"
        )
    
    # Generate content variations
    content_variations = await ai_orchestrator.generate_content_variations(
        db, request.media_file_id, request.content_types
    )
    
    return content_variations


@router.get("/health", response_model=Dict[str, str])
async def ai_health_check():
    """Check AI system health"""
    
    try:
        # Basic health checks
        stats = ai_orchestrator.get_system_stats()
        
        if stats["system_status"] == "operational":
            return {"status": "healthy", "message": "AI system is operational"}
        else:
            return {"status": "degraded", "message": "AI system performance is degraded"}
            
    except Exception as e:
        return {"status": "unhealthy", "message": f"AI system error: {str(e)}"}


# Legacy endpoints for backward compatibility
@router.post('/chat', response_model=ChatResponse)
async def chat(req: ChatRequest, user_id: int = Depends(get_current_user_id)):
    # For now, concatenate messages into a prompt
    prompt = '\n'.join([f"{m.role}: {m.content}" for m in req.messages])
    res = await engine.chat(prompt)
    return ChatResponse(reply=res.get('text', ''), sources=res.get('sources'))


@router.post('/transcribe', response_model=ChatResponse)
async def transcribe(file: UploadFile = File(...), user_id: int = Depends(get_current_user_id)):
    audio = await file.read()
    res = await ai_service.transcribe_audio(audio)
    return ChatResponse(reply=res.get('transcription', ''), sources=[])
    res = await engine.transcribe(audio)
    return ChatResponse(reply=res.get('transcript', ''))


@router.post('/analyze_image', response_model=ChatResponse)
async def analyze_image(file: UploadFile = File(...), user_id: int = Depends(get_current_user_id)):
    img = await file.read()
    res = await engine.analyze_image(img)
    return ChatResponse(reply=res.get('description', ''))


@router.post('/summarize', response_model=ChatResponse)
async def summarize(body: dict, user_id: int = Depends(get_current_user_id)):
    text = body.get('text', '')
    res = await ai_service.summarize_text(text)
    return ChatResponse(reply=res)


@router.post('/qa', response_model=ChatResponse)
async def qa(body: dict, user_id: int = Depends(get_current_user_id)):
    context = body.get('context', '')
    question = body.get('question', '')
    res = await ai_service.answer_question(context, question)
    return ChatResponse(reply=res)


@router.post('/generate', response_model=ChatResponse)
async def generate(body: dict, user_id: int = Depends(get_current_user_id)):
    prompt = body.get('prompt', '')
    res = await ai_service.generate_from_prompt(prompt)
    return ChatResponse(reply=res)
