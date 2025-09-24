from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ChatMessageBase(BaseModel):
    content: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageUpdate(BaseModel):
    content: str

class ChatMessageOut(ChatMessageBase):
    id: int
    role: str
    created_at: datetime

    class Config:
        orm_mode = True
