"""
Board service for managing board operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
import logging

from app.models.board import Board
from app.models.user import User
from app.schemas.board import BoardCreate, BoardUpdate


logger = logging.getLogger(__name__)


class BoardService:
    """Service class for board operations"""

    async def create_board(
        self, 
        db: AsyncSession, 
        board_data: BoardCreate, 
        user_id: int
    ) -> Optional[Board]:
        """Create a new board for the user"""
        try:
            # Create new board
            board = Board(
                title=board_data.title,
                description=board_data.description,
                is_private=board_data.is_private,
                user_id=user_id
            )
            
            db.add(board)
            await db.commit()
            await db.refresh(board)
            
            logger.info(f"Board created successfully: {board.id} for user {user_id}")
            return board
            
        except Exception as e:
            logger.error(f"Error creating board: {str(e)}")
            await db.rollback()
            return None

    async def get_board_by_id(
        self, 
        db: AsyncSession, 
        board_id: int, 
        user_id: int
    ) -> Optional[Board]:
        """Get a board by ID, ensuring user owns it"""
        try:
            result = await db.execute(
                select(Board).where(
                    and_(
                        Board.id == board_id,
                        Board.user_id == user_id
                    )
                )
            )
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error fetching board {board_id}: {str(e)}")
            return None

    async def get_user_boards(
        self, 
        db: AsyncSession, 
        user_id: int,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Board], int]:
        """Get all boards for a user with pagination"""
        try:
            # Calculate offset
            offset = (page - 1) * per_page
            
            # Get total count
            count_result = await db.execute(
                select(func.count(Board.id)).where(Board.user_id == user_id)
            )
            total = count_result.scalar()
            
            # Get boards with pagination
            result = await db.execute(
                select(Board)
                .where(Board.user_id == user_id)
                .order_by(Board.updated_at.desc(), Board.created_at.desc())
                .offset(offset)
                .limit(per_page)
            )
            boards = result.scalars().all()
            
            logger.info(f"Retrieved {len(boards)} boards for user {user_id}")
            return list(boards), total
            
        except Exception as e:
            logger.error(f"Error fetching user boards: {str(e)}")
            return [], 0

    async def update_board(
        self, 
        db: AsyncSession, 
        board_id: int, 
        board_data: BoardUpdate, 
        user_id: int
    ) -> Optional[Board]:
        """Update a board (only if user owns it)"""
        try:
            # Get the board
            board = await self.get_board_by_id(db, board_id, user_id)
            if not board:
                return None
            
            # Update fields that are provided
            update_data = board_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(board, field, value)
            
            await db.commit()
            await db.refresh(board)
            
            logger.info(f"Board {board_id} updated successfully by user {user_id}")
            return board
            
        except Exception as e:
            logger.error(f"Error updating board {board_id}: {str(e)}")
            await db.rollback()
            return None

    async def delete_board(
        self, 
        db: AsyncSession, 
        board_id: int, 
        user_id: int
    ) -> bool:
        """Delete a board (only if user owns it)"""
        try:
            # Get the board
            board = await self.get_board_by_id(db, board_id, user_id)
            if not board:
                return False
            
            await db.delete(board)
            await db.commit()
            
            logger.info(f"Board {board_id} deleted successfully by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting board {board_id}: {str(e)}")
            await db.rollback()
            return False

    async def search_user_boards(
        self, 
        db: AsyncSession, 
        user_id: int,
        search_term: str,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Board], int]:
        """Search boards by title or description"""
        try:
            # Calculate offset
            offset = (page - 1) * per_page
            
            # Create search filter
            search_filter = and_(
                Board.user_id == user_id,
                Board.title.ilike(f"%{search_term}%")
            )
            
            # Get total count
            count_result = await db.execute(
                select(func.count(Board.id)).where(search_filter)
            )
            total = count_result.scalar()
            
            # Get boards with pagination
            result = await db.execute(
                select(Board)
                .where(search_filter)
                .order_by(Board.updated_at.desc(), Board.created_at.desc())
                .offset(offset)
                .limit(per_page)
            )
            boards = result.scalars().all()
            
            logger.info(f"Found {len(boards)} boards for search '{search_term}' by user {user_id}")
            return list(boards), total
            
        except Exception as e:
            logger.error(f"Error searching boards: {str(e)}")
            return [], 0
