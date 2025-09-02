"""
Simplified auth router - works without database for OAuth testing
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
import httpx
from urllib.parse import urlencode
import secrets

from app.core.config import settings

router = APIRouter()

# In-memory storage for demo (use Redis/database in production)
oauth_states = {}

@router.get("/google/login")
async def google_login():
    """Initiate Google OAuth login"""
    # Generate a random state for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = True  # Store state temporarily
    
    # Google OAuth parameters
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "response_type": "code",
        "state": state,
        "access_type": "offline",
        "prompt": "consent"
    }
    
    # Build authorization URL
    google_auth_url = "https://accounts.google.com/o/oauth2/auth?" + urlencode(params)
    
    return RedirectResponse(url=google_auth_url)


@router.get("/google/callback")
async def google_callback(
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None)
):
    """Handle Google OAuth callback"""
    
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state parameter")
    
    # Verify state (CSRF protection)
    if state not in oauth_states:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # Remove used state
    del oauth_states[state]
    
    try:
        # Exchange code for access token
        token_data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        }
        
        async with httpx.AsyncClient() as client:
            # Get access token
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data=token_data
            )
            token_response.raise_for_status()
            tokens = token_response.json()
            
            # Get user info
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {tokens['access_token']}"}
            )
            user_response.raise_for_status()
            user_info = user_response.json()
        
        # For demo, return user info
        return {
            "message": "🎉 Google OAuth login successful!",
            "user": {
                "id": user_info.get("id"),
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "picture": user_info.get("picture")
            },
            "tokens": {
                "access_token": tokens.get("access_token"),
                "token_type": tokens.get("token_type"),
                "expires_in": tokens.get("expires_in")
            },
            "note": "✅ OAuth is working! In production, you would receive a JWT token here"
        }
        
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Failed to exchange code: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth callback error: {str(e)}")


@router.get("/test")
async def test_oauth():
    """Test endpoint to verify OAuth configuration"""
    return {
        "client_id": f"{settings.GOOGLE_CLIENT_ID[:20]}...",
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "login_url": "/api/auth/google/login",
        "status": "✅ OAuth is configured and ready"
    }

# Database-dependent routes will be added once PostgreSQL is set up:
# - POST /register (email/password registration)
# - POST /login (email/password login)  
# - POST /refresh (refresh JWT tokens)
# - GET /me (get current user profile)
# - PUT /me (update user profile)