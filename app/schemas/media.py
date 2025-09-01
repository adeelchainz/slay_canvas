from pydantic import BaseModel
from typing import Optional


class MediaCreate(BaseModel):
    filename: str
    media_type: str


class MediaRead(BaseModel):
    id: int
    filename: str
    path: str
    media_type: str

    class Config:
        orm_mode = True
