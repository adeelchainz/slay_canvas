from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from starlette.requests import Request
from app.core.config import settings
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

try:
    from authlib.integrations.starlette_client import OAuth  # type: ignore
    from app.services import auth_service

    oauth = OAuth()
    oauth.register(
        name='google',
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'},
    )


    @router.get('/google/login')
    async def google_login(request: Request):
        redirect_uri = settings.FRONTEND_ORIGIN + '/auth/callback'
        return await oauth.google.authorize_redirect(request, redirect_uri)


    @router.get('/google/callback')
    async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
        token = await oauth.google.authorize_access_token(request)
        userinfo = await oauth.google.parse_id_token(request, token)
        if not userinfo:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid Google token')

        # Create or get local user and return JWT
        jwt_token = await auth_service.login_or_create_google_user(userinfo, db)
        # Redirect to frontend with token (you may want to use HTTPOnly cookie in production)
        redirect = RedirectResponse(url=f"{settings.FRONTEND_ORIGIN}/auth/success?token={jwt_token}")
        return redirect

except Exception:
    # authlib is not available or registration failed — provide stubs so imports don't crash
    @router.get('/google/login')
    async def google_login_unavailable():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Google OAuth unavailable: install "authlib" and configure GOOGLE_CLIENT_ID/SECRET')

    @router.get('/google/callback')
    async def google_callback_unavailable():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Google OAuth unavailable: install "authlib" and configure GOOGLE_CLIENT_ID/SECRET')

