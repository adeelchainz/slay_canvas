from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.asset import Asset as AssetModel
from app.models.workspace import Workspace as WorkspaceModel
from app.schemas.asset import AssetCreate, AssetUpdate
from google.cloud import storage
import uuid
import os

class AssetService:
    async def create_asset(
        self,
        db: AsyncSession,
        workspace_id: int,
        user_id: int,
        asset_type: str,
        request: AssetCreate,
    ) -> AssetModel:
        """Create an asset of a given type inside a workspace."""
        workspace = await db.get(WorkspaceModel, workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")

        file_url = None
        content = None

        if asset_type in ["images", "voices", "files"] and hasattr(request, "file") and request.file:
            # Initialize Google Cloud Storage client
            storage_client = storage.Client()
            bucket_name = os.getenv("GCS_BUCKET_NAME")  # keep bucket configurable
            bucket = storage_client.bucket(bucket_name)

            # Generate unique key: workspace/{uuid}/{original_filename}
            unique_id = str(uuid.uuid4())
            original_name = request.file.filename  # file name from frontend
            key = f"workspace/{workspace_id}/{unique_id}/{original_name}"

            # Upload file
            blob = bucket.blob(key)
            request.file.file.seek(0)
            blob.upload_from_file(request.file.file, content_type=request.file.content_type)

            # Make public or generate signed URL
            blob.make_public()
            file_url = blob.public_url
        elif asset_type == "texts":
            # fallback: maybe it's a link, not a file
            content = request.content
        else:
            # fallback: maybe it's a link, not a file
            file_url = str(request.url) if request.url else None

        if not file_url and not content:
            raise ValueError("Either file, url, or content must be provided")

        # Create asset entry in DB
        new_asset = AssetModel(
            type=asset_type,
            url=file_url,
            content=content,
            asset_metadata=request.asset_metadata or {},
            workspace_id=workspace_id,
            user_id=user_id,
        )

        db.add(new_asset)
        await db.commit()
        await db.refresh(new_asset)
        return new_asset

    async def list_assets(
        self, db: AsyncSession, workspace_id: int, asset_type: str
    ) -> List[AssetModel]:
        """List all assets of a given type in a workspace."""
        workspace = await db.get(WorkspaceModel, workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")

        result = await db.execute(
            select(AssetModel).where(
                AssetModel.workspace_id == workspace_id,
                AssetModel.type == asset_type,
            )
        )
        return result.scalars().all()

    async def get_asset(
        self, db: AsyncSession, workspace_id: int, asset_id: int, asset_type: str
    ) -> Optional[AssetModel]:
        """Get a specific asset by ID and type."""
        asset = await db.get(AssetModel, asset_id)
        if not asset or asset.workspace_id != workspace_id or asset.type != asset_type:
            return None
        return asset

    async def update_asset(
        self,
        db: AsyncSession,
        workspace_id: int,
        asset_id: int,
        asset_type: str,
        request: AssetUpdate,
    ) -> Optional[AssetModel]:
        asset = await self.get_asset(db, workspace_id, asset_id, asset_type)
        if not asset:
            return None

        asset.url = str(request.url) if request.url else asset.url
        asset.asset_metadata = request.asset_metadata or asset.asset_metadata
        asset.content = request.content or asset.content
        await db.commit()
        await db.refresh(asset)
        return asset

    async def delete_asset(
        self, db: AsyncSession, workspace_id: int, asset_id: int, asset_type: str
    ) -> bool:
        asset = await self.get_asset(db, workspace_id, asset_id, asset_type)
        if not asset:
            return False

        await db.delete(asset)
        await db.commit()
        return True