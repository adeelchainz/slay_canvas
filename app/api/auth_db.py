"""
Authentication API with database integration
Handles Google OAuth login and user storage
"""
from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
import secrets
import logging
from typing import Dict, Any

from app.core.config import settings
from app.db.session import get_async_session
from app.services.user_service import UserService
from app.schemas.user import UserInDB
from app.utils.auth import create_access_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])

# OAuth state storage (in production, use Redis or database)
oauth_states: Dict[str, bool] = {}

def get_user_service() -> UserService:
    return UserService()

@router.get("/google/login")
async def google_login():
    """Initiate Google OAuth login"""
    state = secrets.token_urlsafe(32)
    oauth_states[state] = True
    
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        f"scope=openid email profile&"
        f"response_type=code&"
        f"state={state}"
    )
    
    return RedirectResponse(url=google_auth_url)

@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_async_session),
    user_service: UserService = Depends(get_user_service)
):
    """Handle Google OAuth callback and save user to database"""
    
    # Validate state to prevent CSRF
    if state not in oauth_states:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # Remove used state
    del oauth_states[state]
    
    try:
        # Exchange code for tokens
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                }
            )
            
        if token_response.status_code != 200:
            logger.error(f"Token exchange failed: {token_response.text}")
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")
        
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token received")
        
        # Get user info from Google
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
        if user_response.status_code != 200:
            logger.error(f"User info fetch failed: {user_response.text}")
            raise HTTPException(status_code=400, detail="Failed to get user information")
        
        user_data = user_response.json()
        
        # Extract user information
        google_id = user_data.get("id")
        email = user_data.get("email")
        name = user_data.get("name")
        avatar_url = user_data.get("picture")
        
        if not google_id or not email:
            raise HTTPException(status_code=400, detail="Incomplete user data from Google")
        
        # Create or update user in database
        user = await user_service.create_or_update_oauth_user(
            db=db,
            google_id=google_id,
            email=email,
            name=name,
            avatar_url=avatar_url
        )
        
        if not user:
            raise HTTPException(status_code=500, detail="Failed to create or update user")
        
        # Create JWT token for our app
        jwt_token = create_access_token(data={"sub": str(user.id), "email": user.email})
        
        # Return user data and token
        return JSONResponse(
            content={
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "avatar_url": user.avatar_url,
                    "is_active": user.is_active
                },
                "access_token": jwt_token,
                "token_type": "bearer"
            }
        )
        
    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")

@router.get("/me")
async def get_current_user(
    db: AsyncSession = Depends(get_async_session),
    user_service: UserService = Depends(get_user_service)
):
    """Get current user profile (requires authentication)"""
    # This endpoint would normally require JWT authentication
    # For now, it's a placeholder for testing
    return {"message": "This endpoint requires authentication"}

@router.post("/logout")
async def logout():
    """Logout user"""
    return {"message": "Logged out successfully"}

# Health check endpoint
@router.get("/health")
async def auth_health():
    """Health check for auth service"""
    return {
        "status": "healthy",
        "google_oauth_configured": bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)
    }
