from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    mobile: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: UUID
    is_active: bool
    created_at: Optional[datetime]
    is_admin: bool = False

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    mobile: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str