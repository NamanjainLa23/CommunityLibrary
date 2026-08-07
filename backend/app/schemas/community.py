from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class CommunityCreate(BaseModel):
    name: str


class CommunityOut(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True