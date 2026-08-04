from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class BorrowRequestCreate(BaseModel):
    book_id: UUID
    message: Optional[str] = None


class BorrowRequestOut(BaseModel):
    id: int
    requester_id: UUID
    owner_id: UUID
    book_id: UUID
    status: str
    message: Optional[str]
    created_at: Optional[datetime]
    requester_username: Optional[str] = None
    owner_username: Optional[str] = None
    book_title: Optional[str] = None
    book_image_url: Optional[str] = None

    class Config:
        orm_mode = True


class BorrowRequestUpdate(BaseModel):
    status: str