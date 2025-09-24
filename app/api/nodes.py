from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.utils.auth import get_current_user_id
from app.services.node_service import NodeService
from app.schemas.node import NodeCreate, NodeOut, NodeUpdate

router = APIRouter(prefix="/workspaces/{workspace_id}/nodes", tags=["nodes"])
security = HTTPBearer()


@router.post("/", response_model=NodeOut, status_code=status.HTTP_201_CREATED)
async def create_node(
    workspace_id: int,
    request: NodeCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    _ = get_current_user_id(credentials)
    service = NodeService()
    return await service.create_node(db, workspace_id, request)


@router.get("/", response_model=List[NodeOut])
async def list_nodes(
    workspace_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    _ = get_current_user_id(credentials)
    service = NodeService()
    return await service.list_nodes(db, workspace_id)


@router.get("/{node_id}", response_model=NodeOut)
async def get_node(
    workspace_id: int,
    node_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    _ = get_current_user_id(credentials)
    service = NodeService()
    node = await service.get_node(db, workspace_id, node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


@router.put("/{node_id}", response_model=NodeOut)
async def update_node(
    workspace_id: int,
    node_id: int,
    request: NodeUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    _ = get_current_user_id(credentials)
    service = NodeService()
    node = await service.update_node(db, workspace_id, node_id, request)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node(
    workspace_id: int,
    node_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    _ = get_current_user_id(credentials)
    service = NodeService()
    deleted = await service.delete_node(db, workspace_id, node_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Node not found")
    return {"message": "Node deleted successfully"}
