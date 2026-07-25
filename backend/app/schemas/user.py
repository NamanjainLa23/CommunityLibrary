from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    mobile: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    mobile: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str