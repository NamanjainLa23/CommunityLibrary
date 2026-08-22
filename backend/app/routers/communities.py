from re import L
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.models.community import Community as CommunityModel, user_communities, CommunityJoinRequest, CommunityMembership
from app.models.user import User as UserModel
from app.models.book import Book as BookModel
from app.schemas.community import CommunityCreate, CommunityOut, CommunityDetail, OwnerBooks, JoinRequestUpdate, JoinRequestOut
from app.schemas.book import BookOut
from app.core.security import get_current_user, require_admin
from uuid import UUID

router = APIRouter(prefix="/api/communities", tags=["communities"])

#create helper functios for reusable code
# def is_community_admin(db, user, community_id) -> bool:
#     if user.is_admin:
#         return True
#     m = db.query(CommunityMembership).filter_by(
#         user_id=user.id, community_id=community_id, role="admin"
#     ).first()
#     return m is not None


@router.post("", response_model=CommunityOut)
def create_community(payload: CommunityCreate, db: Session = Depends(get_db), current_user = Depends(require_admin)):
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
    

@router.get("/join-requests", response_model=List[JoinRequestOut])
def all_join_requests(db: Session = Depends(get_db), current_user=Depends(require_admin)):
    rows = db.query(CommunityJoinRequest).filter(CommunityJoinRequest.status == "pending").all()
    result = []

    for req in rows:
        user = db.query(UserModel).filter(UserModel.id == req.user_id).first()
        community = db.query(CommunityModel).filter(CommunityModel.id == req.community_id).first()
        result.append({
            "id": req.id,
            "user_id": req.user_id,
            "community_id": req.community_id,
            "community_name": community.name if community else None,
            "status": req.status,
            "username": user.username if user else None,
            "email": user.email if user else None,
        })
    return result


@router.get("/{community_id}", response_model=CommunityDetail)
def get_community(community_id: UUID, db: Session = Depends(get_db)):
    c = db.query(CommunityModel).filter(CommunityModel.id == community_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Community not found")

    return c

@router.post("/{community_id}/join")
def join_community(community_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    c = db.query(CommunityModel).filter(CommunityModel.id == community_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Community not found")
    # already member -> 400
    if current_user in c.members:
        raise HTTPException(status_code=400, detail="Already a member")
    # existing pending request -> 400
    existing_request = db.query(CommunityJoinRequest).filter(CommunityJoinRequest.user_id == current_user.id, CommunityJoinRequest.community_id == c.id, CommunityJoinRequest.status == "pending").first()
    if existing_request:
        raise HTTPException(status_code=400, detail="Already a pending request")
    # create request
    db.add(CommunityJoinRequest(user_id=current_user.id, community_id=c.id, status="pending"))
    db.commit()
    return {"status": "pending"}


@router.get("/{community_id}/join-requests", response_model=List[JoinRequestOut])
def list_join_requests(community_id: UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # 403 unless membership.role == 'admin' or current_user.is_admin
    c = db.query(CommunityModel).filter(CommunityModel.id == community_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Community not found")
    if current_user not in c.members and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    pending_requests = db.query(CommunityJoinRequest).filter(CommunityJoinRequest.community_id == c.id, CommunityJoinRequest.status == "pending").all()
    
    result = []
    for req in pending_requests:
        user = db.query(UserModel).filter(UserModel.id == req.user_id).first()
        result.append({
            "id": req.id,
            "user_id": req.user_id,
            "community_id": req.community_id,
            "status": req.status,
            "username": user.username if user else None,
            "email": user.email if user else None,
        })
    
    return result

@router.patch("/{community_id}/join-requests/{req_id}")
def decide_join(community_id: UUID, req_id: int, payload: JoinRequestUpdate, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    # only community admin
    c = db.query(CommunityModel).filter(CommunityModel.id == community_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Community not found")
    if current_user not in c.members and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    req = db.query(CommunityJoinRequest).filter(CommunityJoinRequest.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Join request not found")

    if payload.status == "approved":
        db.add(CommunityMembership(user_id=req.user_id, community_id=c.id, role="member"))
        req.status = "approved"
        db.add(req)
        
    elif payload.status == "rejected":
        req.status = "rejected"
        db.add(req)
    else:
        raise HTTPException(status_code=400, detail="Invalid status")
    db.commit()
    return {"status": payload.status}


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


# @router.post("/{community_id}/join")
# def join_community(community_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
#     c = db.query(CommunityModel).filter(CommunityModel.id == community_id).first()
#     if not c:
#         raise HTTPException(status_code=404, detail="Community not found")
#     # attach user
#     if current_user not in c.members:
#         c.members.append(current_user)
#         db.add(c)
#         db.commit()
#     return {"status": "joined"}


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