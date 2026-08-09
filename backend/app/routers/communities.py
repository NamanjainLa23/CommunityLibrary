from re import L
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.models.community import Community as CommunityModel, user_communities
from app.models.user import User as UserModel
from app.models.book import Book as BookModel
from app.schemas.community import CommunityCreate, CommunityOut, CommunityDetail, OwnerBooks
from app.schemas.book import BookOut
from app.core.security import get_current_user
from uuid import UUID

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


@router.get("/me", response_model=List[CommunityOut])
def my_communities(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        return current_user.communities
    except Exception:
        return []


@router.get("/available", response_model=List[CommunityOut])
def available_communities(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    my_ids = [c.id for c in current_user.communities]
    q = db.query(CommunityModel)
    if my_ids:
        q = q.filter(~CommunityModel.id.in_(my_ids))

    return q.all()
    

@router.get("/{community_id}", response_model=CommunityDetail)
def get_community(community_id: UUID, db: Session = Depends(get_db)):
    c = db.query(CommunityModel).filter(CommunityModel.id == community_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Community not found")

    return c


@router.get("/{community_id}/books", response_model=List[OwnerBooks])
def community_books(community_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    c = db.query(CommunityModel).filter(CommunityModel.id == community_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Community not found")

    result = []
    for member in c.members:
        if current_user and member.id == current_user.id:
            continue

        books = db.query(BookModel).filter(BookModel.owner_id == member.id, BookModel.is_public == True).all()
        if books:
            for b in books:
                try:
                    b.owner_username = member.username
                except Exception:
                    pass
            
            result.append({"owner": member, "books": books})

    return result


@router.post("/{community_id}/join")
def join_community(community_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
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
def leave_community(community_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    c = db.query(CommunityModel).filter(CommunityModel.id == community_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Community not found")
    if current_user in c.members:
        c.members.remove(current_user)
        db.add(c)
        db.commit()
    return {"status": "left"}