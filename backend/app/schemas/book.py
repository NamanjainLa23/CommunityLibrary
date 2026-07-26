from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BookBase(BaseModel):
    title: str
    author: Optional[str] = None
    isbn: Optional[str] = None
    is_public: Optional[bool] = True
    description: Optional[str] = None
    image_url: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookFromISBN(BaseModel):
    isbn: str
    is_public: Optional[bool] = True

class BookUpdate(BookBase):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    is_public: Optional[bool] = True
    description: Optional[str] = None
    image_url: Optional[str] = None

class BookOut(BookBase):
    id: int
    owner_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True