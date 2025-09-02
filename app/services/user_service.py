from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def get_user_by_google_id(self, db: AsyncSession, google_id: str) -> Optional[User]:
        """Get user by Google ID."""
        result = await db.execute(select(User).where(User.google_id == google_id))
        return result.scalar_one_or_none()
    
    async def get_users(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Get list of users."""
        result = await db.execute(
            select(User)
            .offset(skip)
            .limit(limit)
            .options(selectinload(User.projects), selectinload(User.media_files))
        )
        return result.scalars().all()
    
    async def create_user(self, db: AsyncSession, user_data: UserCreate) -> User:
        """Create a new user."""
        user = User(**user_data.dict())
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    async def create_or_update_oauth_user(self, db: AsyncSession, google_id: str, email: str, name: str, avatar_url: str = None) -> User:
        """Create or update user from OAuth data."""
        # Check if user exists by Google ID
        user = await self.get_user_by_google_id(db, google_id)
        
        if user:
            # Update existing user
            user.name = name
            user.email = email
            if avatar_url:
                user.avatar_url = avatar_url
            user.is_active = True
            await db.commit()
            await db.refresh(user)
            return user
        
        # Check if user exists by email
        user = await self.get_user_by_email(db, email)
        if user:
            # Link Google ID to existing user
            user.google_id = google_id
            user.name = name
            if avatar_url:
                user.avatar_url = avatar_url
            user.is_active = True
            await db.commit()
            await db.refresh(user)
            return user
        
        # Create new user
        user_data = UserCreate(
            email=email,
            name=name,
            google_id=google_id,
            avatar_url=avatar_url,
            is_active=True
        )
        return await self.create_user(db, user_data)
    
    async def update_user(self, db: AsyncSession, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user."""
        user = await self.get_user_by_id(db, user_id)
        if not user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        return user
    
    async def delete_user(self, db: AsyncSession, user_id: int) -> bool:
        """Delete user."""
        user = await self.get_user_by_id(db, user_id)
        if not user:
            return False
        
        await db.delete(user)
        await db.commit()
        return True
    
    async def activate_user(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Activate user account."""
        user = await self.get_user_by_id(db, user_id)
        if not user:
            return None
        
        user.is_active = True
        user.is_verified = True
        await db.commit()
        await db.refresh(user)
        return user
    
    async def deactivate_user(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Deactivate user account."""
        user = await self.get_user_by_id(db, user_id)
        if not user:
            return None
        
        user.is_active = False
        await db.commit()
        await db.refresh(user)
        return user


# Legacy function for backward compatibility
async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """Legacy function - use UserService.get_user_by_id instead."""
    service = UserService()
    return await service.get_user_by_id(db, user_id)
