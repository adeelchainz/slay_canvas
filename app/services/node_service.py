from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.node import Node
from app.schemas.node import NodeCreate, NodeUpdate


class NodeService:
    async def create_node(self, db: AsyncSession, workspace_id: int, node_in: NodeCreate) -> Node:
        node = Node(
            workspace_id=workspace_id,
            source_asset_id=node_in.source_asset_id,
            target_asset_id=node_in.target_asset_id,
            node_metadata=node_in.node_metadata or {},
        )
        db.add(node)
        await db.flush()
        await db.commit()
        await db.refresh(node)
        return node

    async def list_nodes(self, db: AsyncSession, workspace_id: int) -> List[Node]:
        result = await db.execute(
            select(Node).where(Node.workspace_id == workspace_id)
        )
        return result.scalars().all()

    async def get_node(self, db: AsyncSession, workspace_id: int, node_id: int) -> Optional[Node]:
        return await db.get(Node, node_id)

    async def update_node(self, db: AsyncSession, workspace_id: int, node_id: int, node_in: NodeUpdate) -> Optional[Node]:
        node = await db.get(Node, node_id)
        if not node or node.workspace_id != workspace_id:
            return None

        for field, value in node_in.dict(exclude_unset=True).items():
            setattr(node, field, value)

        await db.commit()
        await db.refresh(node)
        return node

    async def delete_node(self, db: AsyncSession, workspace_id: int, node_id: int) -> bool:
        node = await db.get(Node, node_id)
        if not node or node.workspace_id != workspace_id:
            return False

        await db.delete(node)
        await db.commit()
        return True
