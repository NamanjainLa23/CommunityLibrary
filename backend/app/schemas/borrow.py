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

    class Config:
        orm_mode = True