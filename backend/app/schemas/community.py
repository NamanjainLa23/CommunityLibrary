from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

from app.schemas.user import UserOut
from app.schemas.book import BookOut


class CommunityCreate(BaseModel):
    name: str


class CommunityOut(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True

class CommunityDetail(CommunityOut):
    members: List[UserOut] = []
    
    class Config:
        orm_mode = True

class OwnerBooks(BaseModel):
    owner: UserOut
    books: List[BookOut]

    class Config:
        orm_mode = True

class JoinRequestUpdate(BaseModel):
    status: str  # "approved" | "rejected"

    
class JoinRequestOut(BaseModel):
    id: int
    user_id: UUID
    community_id: UUID
    community_name: Optional[str] = None
    status: str
    username: Optional[str] = None
    email: Optional[str] = None
    class Config:
        orm_mode = True