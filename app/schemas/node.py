# app/schemas/node.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class NodeBase(BaseModel):
    source_asset_id: int
    target_asset_id: int
    node_metadata: Optional[Dict[str, Any]] = {}

class NodeCreate(NodeBase):
    pass  # no "name" required

class NodeUpdate(BaseModel):
    node_metadata: Optional[Dict[str, Any]] = None

class NodeInDBBase(NodeBase):
    id: int
    workspace_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NodeOut(NodeInDBBase):
    pass
