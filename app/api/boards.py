"""
Board API endpoints for managing user boards
Handles CRUD operations for boards with proper authorization
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from app.db.session import get_async_session
from app.services.board_service import BoardService
from app.schemas.board import (
    BoardCreate, BoardUpdate, BoardPublic, BoardResponse, 
    BoardListResponse
)
from app.schemas.user import MessageResponse
from app.utils.auth import get_current_user_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/boards", tags=["boards"])


def get_board_service() -> BoardService:
    return BoardService()


@router.post("/", response_model=BoardResponse, status_code=201)
async def create_board(
    board_data: BoardCreate,
    db: AsyncSession = Depends(get_async_session),
    board_service: BoardService = Depends(get_board_service),
    current_user_id: int = Depends(get_current_user_id)
):
    """Create a new board"""
    try:
        board = await board_service.create_board(db, board_data, current_user_id)
        if not board:
            raise HTTPException(status_code=500, detail="Failed to create board")
        
        board_public = BoardPublic.from_orm(board)
        
        return BoardResponse(
            message="Board created successfully",
            board=board_public
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create board error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create board")


@router.get("/", response_model=BoardListResponse)
async def get_user_boards(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term for board title"),
    db: AsyncSession = Depends(get_async_session),
    board_service: BoardService = Depends(get_board_service),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get all boards for the current user with optional search"""
    try:
        if search:
            boards, total = await board_service.search_user_boards(
                db, current_user_id, search, page, per_page
            )
        else:
            boards, total = await board_service.get_user_boards(
                db, current_user_id, page, per_page
            )
        
        boards_public = [BoardPublic.from_orm(board) for board in boards]
        
        return BoardListResponse(
            boards=boards_public,
            total=total,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        logger.error(f"Get user boards error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch boards")


@router.get("/{board_id}", response_model=BoardPublic)
async def get_board(
    board_id: int,
    db: AsyncSession = Depends(get_async_session),
    board_service: BoardService = Depends(get_board_service),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get a specific board by ID"""
    try:
        board = await board_service.get_board_by_id(db, board_id, current_user_id)
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        return BoardPublic.from_orm(board)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get board error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch board")


@router.put("/{board_id}", response_model=BoardResponse)
async def update_board(
    board_id: int,
    board_data: BoardUpdate,
    db: AsyncSession = Depends(get_async_session),
    board_service: BoardService = Depends(get_board_service),
    current_user_id: int = Depends(get_current_user_id)
):
    """Update a board (rename, change description, privacy settings)"""
    try:
        board = await board_service.update_board(db, board_id, board_data, current_user_id)
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        board_public = BoardPublic.from_orm(board)
        
        return BoardResponse(
            message="Board updated successfully",
            board=board_public
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update board error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update board")


@router.delete("/{board_id}", response_model=MessageResponse)
async def delete_board(
    board_id: int,
    db: AsyncSession = Depends(get_async_session),
    board_service: BoardService = Depends(get_board_service),
    current_user_id: int = Depends(get_current_user_id)
):
    """Delete a board"""
    try:
        success = await board_service.delete_board(db, board_id, current_user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Board not found")
        
        return MessageResponse(message="Board deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete board error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete board")


# Board statistics endpoint
@router.get("/stats/summary")
async def get_board_stats(
    db: AsyncSession = Depends(get_async_session),
    board_service: BoardService = Depends(get_board_service),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get board statistics for the current user"""
    try:
        boards, total = await board_service.get_user_boards(db, current_user_id, 1, 1000)  # Get all boards
        
        # Calculate statistics
        private_count = sum(1 for board in boards if board.is_private)
        public_count = total - private_count
        
        return {
            "total_boards": total,
            "private_boards": private_count,
            "public_boards": public_count,
            "recent_boards": len([b for b in boards[:5]])  # Recent 5
        }
        
    except Exception as e:
        logger.error(f"Get board stats error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch board statistics")
