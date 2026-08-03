from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.schemas import borrow as borrow_schemas
from app.core.security import get_current_user
from app.models.borrow import BorrowRequest as BorrowModel
from app.models.book import Book as BookModel
from app.models.user import User as UserModel
from app.core.email import send_email

router = APIRouter(prefix="/api/borrow_requests", tags=["borrow_requests"])

@router.post("", response_model=borrow_schemas.BorrowRequestOut, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=borrow_schemas.BorrowRequestOut, status_code=status.HTTP_201_CREATED)
def create_request(payload: borrow_schemas.BorrowRequestCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # validate book
    book = db.query(BookModel).filter(BookModel.id == payload.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot request your own book")

    owner = db.query(UserModel).filter(UserModel.id == book.owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")

    br = BorrowModel(
        requester_id=current_user.id,
        owner_id=owner.id,
        book_id=book.id,
        status='pending',
        message=payload.message,
    )
    db.add(br)
    db.commit()
    db.refresh(br)

    # send email to owner (best-effort)
    subject = f"Borrow request: {book.title}"
    body = f"User {current_user.username or current_user.mobile} (id={current_user.id}) requests to borrow your book '{book.title}'.\n\nMessage:\n{payload.message or ''}\n\nVisit the app to respond."
    send_email(owner.email or owner.mobile or '','Borrow request', body)

    return br


@router.get("/me", response_model=List[borrow_schemas.BorrowRequestOut])
def my_requests(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(BorrowModel).filter(BorrowModel.requester_id == current_user.id).all()


@router.get("/received", response_model=List[borrow_schemas.BorrowRequestOut])
def received_requests(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(BorrowModel).filter(BorrowModel.owner_id == current_user.id).all()
