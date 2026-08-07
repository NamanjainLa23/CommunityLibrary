from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.models.community import Community as CommunityModel, user_communities
from app.models.user import User as UserModel
from app.schemas.community import CommunityCreate, CommunityOut
from app.core.security import get_current_user

router = APIRouter(prefix="/api/communities", tags=["communities"])


@router.post("", response_model=CommunityOut)
def create_community(payload: CommunityCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    existing = db.query(CommunityModel).filter(CommunityModel.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Community already exists")
    c = CommunityModel(name=payload.name)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.get("", response_model=List[CommunityOut])
def list_communities(db: Session = Depends(get_db)):
    return db.query(CommunityModel).all()


@router.post("/{community_id}/join")
def join_community(community_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    c = db.query(CommunityModel).filter(CommunityModel.id == community_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Community not found")
    # attach user
    if current_user not in c.members:
        c.members.append(current_user)
        db.add(c)
        db.commit()
    return {"status": "joined"}


@router.post("/{community_id}/leave")
def leave_community(community_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    c = db.query(CommunityModel).filter(CommunityModel.id == community_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Community not found")
    if current_user in c.members:
        c.members.remove(current_user)
        db.add(c)
        db.commit()
    return {"status": "left"}


@router.get("/me", response_model=List[CommunityOut])
def my_communities(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        return current_user.communities
    except Exception:
        return []
