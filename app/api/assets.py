from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.asset import AssetCreate, AssetRead, AssetUpdate
from app.utils.auth import get_current_user_id
from app.services.assets_service import AssetService

router = APIRouter(prefix="/workspaces/{workspace_id}/assets", tags=["assets"])
security = HTTPBearer()
service = AssetService()


# -------------------------
# Social Endpoints
# -------------------------

@router.post("/social/", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
async def create_social_asset(
    workspace_id: int,
    request: AssetCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    user_id: int = get_current_user_id(credentials)
    try:
        return await service.create_asset(db, workspace_id, user_id, "social", request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/social/", response_model=List[AssetRead])
async def list_social_assets(
    workspace_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await service.list_assets(db, workspace_id, "social")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/social/{asset_id}", response_model=AssetRead)
async def get_social_asset(
    workspace_id: int,
    asset_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    asset = await service.get_asset(db, workspace_id, asset_id, "social")
    if not asset:
        raise HTTPException(status_code=404, detail="Social asset not found")
    return asset

@router.put("/social/{asset_id}", response_model=AssetRead)
async def update_social_asset(
    workspace_id: int,
    asset_id: int,
    request: AssetUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    updated = await service.update_asset(db, workspace_id, asset_id, "social", request)
    if not updated:
        raise HTTPException(status_code=404, detail="Social asset not found")
    return updated


@router.delete("/social/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_social_asset(
    workspace_id: int,
    asset_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    success = await service.delete_asset(db, workspace_id, asset_id, "social")
    if not success:
        raise HTTPException(status_code=404, detail="Social asset not found")
    return None

# -------------------------
# Weblink Endpoints
# -------------------------

@router.post("/weblink/", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
async def create_weblink_asset(
    workspace_id: int,
    request: AssetCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    user_id: int = get_current_user_id(credentials)
    try:
        return await service.create_asset(db, workspace_id, user_id, "weblink", request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/weblink/", response_model=List[AssetRead])
async def list_weblink_assets(
    workspace_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await service.list_assets(db, workspace_id, "weblink")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/weblink/{asset_id}", response_model=AssetRead)
async def get_weblink_asset(
    workspace_id: int,
    asset_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    asset = await service.get_asset(db, workspace_id, asset_id, "weblink")
    if not asset:
        raise HTTPException(status_code=404, detail="Weblink asset not found")
    return asset

@router.put("/weblink/{asset_id}", response_model=AssetRead)
async def update_weblink_asset(
    workspace_id: int,
    asset_id: int,
    request: AssetUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    updated = await service.update_asset(db, workspace_id, asset_id, "weblink", request)
    if not updated:
        raise HTTPException(status_code=404, detail="Weblink asset not found")
    return updated


@router.delete("/weblink/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_weblink_asset(
    workspace_id: int,
    asset_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    success = await service.delete_asset(db, workspace_id, asset_id, "weblink")
    if not success:
        raise HTTPException(status_code=404, detail="Weblink asset not found")
    return None

# -------------------------
# Images Endpoints
# -------------------------

@router.post("/images/", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
async def create_images_asset(
    workspace_id: int,
    file: UploadFile = File(None),                          # file upload
    asset_metadata: Optional[str] = Form(None),             # metadata as JSON string
    url: Optional[str] = Form(None),                        # fallback: external link
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    user_id: int = get_current_user_id(credentials)

    # Convert metadata string into dict
    import json
    metadata_dict = json.loads(asset_metadata) if asset_metadata else {}

    # Build request-like object
    request = AssetCreate(url=url, asset_metadata=metadata_dict)

    # attach file dynamically
    request.file = file  

    try:
        return await service.create_asset(db, workspace_id, user_id, "images", request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/images/", response_model=List[AssetRead])
async def list_images_assets(
    workspace_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await service.list_assets(db, workspace_id, "images")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/images/{asset_id}", response_model=AssetRead)
async def get_images_asset(
    workspace_id: int,
    asset_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    asset = await service.get_asset(db, workspace_id, asset_id, "images")
    if not asset:
        raise HTTPException(status_code=404, detail="Images asset not found")
    return asset

@router.put("/images/{asset_id}", response_model=AssetRead)
async def update_images_asset(
    workspace_id: int,
    asset_id: int,
    request: AssetUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    updated = await service.update_asset(db, workspace_id, asset_id, "images", request)
    if not updated:
        raise HTTPException(status_code=404, detail="Images asset not found")
    return updated


@router.delete("/images/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_images_asset(
    workspace_id: int,
    asset_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    success = await service.delete_asset(db, workspace_id, asset_id, "images")
    if not success:
        raise HTTPException(status_code=404, detail="Images asset not found")
    return None

# -------------------------
# Voices Notes Endpoints
# -------------------------

@router.post("/voices/", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
async def create_voices_asset(
    workspace_id: int,
    file: UploadFile = File(None),                          # file upload
    asset_metadata: Optional[str] = Form(None),             # metadata as JSON string
    url: Optional[str] = Form(None),                        # fallback: external link
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    user_id: int = get_current_user_id(credentials)

    # Convert metadata string into dict
    import json
    metadata_dict = json.loads(asset_metadata) if asset_metadata else {}

    # Build request-like object
    request = AssetCreate(url=url, asset_metadata=metadata_dict)

    # attach file dynamically
    request.file = file  

    try:
        return await service.create_asset(db, workspace_id, user_id, "voices", request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/voices/", response_model=List[AssetRead])
async def list_voices_assets(
    workspace_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await service.list_assets(db, workspace_id, "voices")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/voices/{asset_id}", response_model=AssetRead)
async def get_voices_asset(
    workspace_id: int,
    asset_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    asset = await service.get_asset(db, workspace_id, asset_id, "voices")
    if not asset:
        raise HTTPException(status_code=404, detail="Voices asset not found")
    return asset

@router.put("/voices/{asset_id}", response_model=AssetRead)
async def update_voices_asset(
    workspace_id: int,
    asset_id: int,
    request: AssetUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    updated = await service.update_asset(db, workspace_id, asset_id, "voices", request)
    if not updated:
        raise HTTPException(status_code=404, detail="Voices asset not found")
    return updated


@router.delete("/voices/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_voices_asset(
    workspace_id: int,
    asset_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    success = await service.delete_asset(db, workspace_id, asset_id, "voices")
    if not success:
        raise HTTPException(status_code=404, detail="Voices asset not found")
    return None

# -------------------------
# Files Endpoints
# -------------------------

@router.post("/files/", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
async def create_files_asset(
    workspace_id: int,
    file: UploadFile = File(None),                          # file upload
    asset_metadata: Optional[str] = Form(None),             # metadata as JSON string
    url: Optional[str] = Form(None),                        # fallback: external link
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    user_id: int = get_current_user_id(credentials)

    # Convert metadata string into dict
    import json
    metadata_dict = json.loads(asset_metadata) if asset_metadata else {}

    # Build request-like object
    request = AssetCreate(url=url, asset_metadata=metadata_dict)

    # attach file dynamically
    request.file = file  

    try:
        return await service.create_asset(db, workspace_id, user_id, "files", request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/files/", response_model=List[AssetRead])
async def list_files_assets(
    workspace_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await service.list_assets(db, workspace_id, "files")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/files/{asset_id}", response_model=AssetRead)
async def get_files_asset(
    workspace_id: int,
    asset_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    asset = await service.get_asset(db, workspace_id, asset_id, "files")
    if not asset:
        raise HTTPException(status_code=404, detail="Files asset not found")
    return asset

@router.put("/files/{asset_id}", response_model=AssetRead)
async def update_files_asset(
    workspace_id: int,
    asset_id: int,
    request: AssetUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    updated = await service.update_asset(db, workspace_id, asset_id, "files", request)
    if not updated:
        raise HTTPException(status_code=404, detail="Files asset not found")
    return updated


@router.delete("/files/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_files_asset(
    workspace_id: int,
    asset_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    success = await service.delete_asset(db, workspace_id, asset_id, "files")
    if not success:
        raise HTTPException(status_code=404, detail="Files asset not found")
    return None

# -------------------------
# Text Endpoints
# -------------------------

@router.post("/texts/", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
async def create_texts_asset(
    workspace_id: int,
    request: AssetCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    user_id: int = get_current_user_id(credentials)
    try:
        return await service.create_asset(db, workspace_id, user_id, "texts", request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/texts/", response_model=List[AssetRead])
async def list_texts_assets(
    workspace_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await service.list_assets(db, workspace_id, "texts")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/texts/{asset_id}", response_model=AssetRead)
async def get_texts_asset(
    workspace_id: int,
    asset_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    asset = await service.get_asset(db, workspace_id, asset_id, "texts")
    if not asset:
        raise HTTPException(status_code=404, detail="Text asset not found")
    return asset

@router.put("/texts/{asset_id}", response_model=AssetRead)
async def update_texts_asset(
    workspace_id: int,
    asset_id: int,
    request: AssetUpdate, 
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    updated = await service.update_asset(db, workspace_id, asset_id, "texts", request)
    if not updated:
        raise HTTPException(status_code=404, detail="Text asset not found")
    return updated


@router.delete("/texts/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_texts_asset(
    workspace_id: int,
    asset_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    success = await service.delete_asset(db, workspace_id, asset_id, "texts")
    if not success:
        raise HTTPException(status_code=404, detail="Text asset not found")
    return None
