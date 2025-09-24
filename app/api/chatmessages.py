from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from app.db.session import get_db
from app.models.chatmessage import ChatMessage
from app.schemas.chatmessage import ChatMessageCreate, ChatMessageUpdate, ChatMessageOut
from typing import List

router = APIRouter(prefix="/workspaces/{workspace_id}/chat", tags=["Chat"])

# POST /chat → send message
@router.post("", response_model=ChatMessageOut)
async def send_message(workspace_id: int, body: ChatMessageCreate, db: AsyncSession = Depends(get_db)):
    msg = ChatMessage(workspace_id=workspace_id, role="user", content=body.content)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)

    # 🔮 here you’d hook in Poppy AI (LLM call, embeddings, RAG, etc.)
    # Save assistant response as another ChatMessage with role="assistant"

    return msg


# GET /chat/history → get all
@router.get("/history", response_model=List[ChatMessageOut])
async def get_chat_history(workspace_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.workspace_id == workspace_id).order_by(ChatMessage.created_at)
    )
    return result.scalars().all()


# GET /chat/history/{messageId} → get one
@router.get("/history/{message_id}", response_model=ChatMessageOut)
async def get_message(workspace_id: int, message_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.id == message_id, ChatMessage.workspace_id == workspace_id)
    )
    msg = result.scalar_one_or_none()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    return msg


# PUT /chat/history/{messageId} → edit message
@router.put("/history/{message_id}", response_model=ChatMessageOut)
async def update_message(workspace_id: int, message_id: int, body: ChatMessageUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.id == message_id, ChatMessage.workspace_id == workspace_id)
    )
    msg = result.scalar_one_or_none()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")

    msg.content = body.content
    await db.commit()
    await db.refresh(msg)
    return msg


# DELETE /chat/history/{messageId} → delete one
@router.delete("/history/{message_id}")
async def delete_message(workspace_id: int, message_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.id == message_id, ChatMessage.workspace_id == workspace_id)
    )
    msg = result.scalar_one_or_none()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")

    await db.delete(msg)
    await db.commit()
    return {"message": "Deleted successfully"}


# DELETE /chat/history → clear all messages
@router.delete("/history")
async def clear_history(workspace_id: int, db: AsyncSession = Depends(get_db)):
    await db.execute(
        text("DELETE FROM chat_messages WHERE workspace_id = :workspace_id"),
        {"workspace_id": workspace_id}
    )
    await db.commit()
    return {"message": "Chat history cleared"}
