from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BorrowRequestCreate(BaseModel):
    book_id: int
    message: Optional[str] = None


class BorrowRequestOut(BaseModel):
    id: int
    requester_id: int
    owner_id: int
    book_id: int
    status: str
    message: Optional[str]
    created_at: Optional[datetime]

    class Config:
        orm_mode = True