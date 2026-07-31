from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models.user import User as UserModel
from app.schemas.user import UserOut
from app.core.security import get_current_user
from app.db import get_db

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("", response_model=List[UserOut])
@router.get("/", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(UserModel).all()


@router.get("/me", response_model=UserOut)
def get_me(current_user = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return current_user