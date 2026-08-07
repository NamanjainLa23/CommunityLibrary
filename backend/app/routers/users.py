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
def list_users(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # return users who share at least one community with current_user (exclude self)
    allowed = set()
    try:
        for c in current_user.communities:
            for m in c.members:
                if m.id != current_user.id:
                    allowed.add(m.id)
    except Exception:
        allowed = set()

    if not allowed:
        return []

    return db.query(UserModel).filter(UserModel.id.in_(list(allowed))).all()


@router.get("/me", response_model=UserOut)
def get_me(current_user = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return current_user