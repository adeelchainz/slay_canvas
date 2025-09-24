from sqlalchemy import Column, Integer, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import relationship
from app.db.session import Base

class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    source_asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    target_asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)

    node_metadata = Column(JSON, default={})

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    workspace = relationship("Workspace", back_populates="nodes")
    source_asset = relationship("Asset", foreign_keys=[source_asset_id])
    target_asset = relationship("Asset", foreign_keys=[target_asset_id])

    def __repr__(self):
        return f"<Node(id={self.id}, src={self.source_asset_id}, tgt={self.target_asset_id})>"
