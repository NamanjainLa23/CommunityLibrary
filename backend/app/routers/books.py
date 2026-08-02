from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.db import get_db
from app.schemas import book as book_schemas
from app.core.security import get_current_user
from app.models.book import Book as BookModel
from app.models.user import User as UserModel
from app.models.borrow import BorrowRequest as BorrowModel

router = APIRouter(prefix="/api/books", tags=["books"])

@router.post("/", response_model=book_schemas.BookOut, status_code=status.HTTP_201_CREATED)
def create_book(payload: book_schemas.BookCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    book = BookModel(
        owner_id=current_user.id,
        title=payload.title,
        author=payload.author,
        isbn=payload.isbn,
        quantity=payload.quantity or 1,
        is_public=payload.is_public if payload.is_public is not None else True,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

@router.get("/me", response_model=List[book_schemas.BookOut])
def list_my_books(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(BookModel).filter(BookModel.owner_id == current_user.id).all()

@router.get("/public", response_model=List[book_schemas.BookOut])
def list_public_books(owner_id: Optional[int] = None, owner_username: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(BookModel).filter(BookModel.is_public == True)
    if owner_id:
        q = q.filter(BookModel.owner_id == owner_id)
    elif owner_username:
        # try to resolve username or mobile to user id
        user = db.query(UserModel).filter((UserModel.username == owner_username) | (UserModel.mobile == owner_username)).first()
        if not user:
            return []
        q = q.filter(BookModel.owner_id == user.id)
    return q.all()


@router.get("/search", response_model=List[book_schemas.BookOut])
def search_books(query: str, db: Session = Depends(get_db)):
    """Server-side search across title, author, isbn and owner username/mobile.

    Returns only public books matching the query.
    """
    qstr = f"%{query}%"
    # join with users to allow searching by username/mobile
    q = db.query(BookModel).join(UserModel, BookModel.owner_id == UserModel.id).filter(BookModel.is_public == True)
    filters = (
        BookModel.title.ilike(qstr),
        BookModel.author.ilike(qstr),
        BookModel.isbn.ilike(qstr),
        UserModel.username.ilike(qstr),
        UserModel.mobile.ilike(qstr),
    )
    q = q.filter(or_(*filters))
    return q.all()


@router.get('/borrowed', response_model=List[book_schemas.BookOut])
def list_borrowed_books(status: Optional[str] = None, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Return books borrowed by the current user. By default returns approved borrows.

    Optional query param `status` can filter by borrow request status (e.g. pending, approved).
    """
    st = status or 'approved'
    q = db.query(BookModel).join(BorrowModel, BorrowModel.book_id == BookModel.id).filter(BorrowModel.requester_id == current_user.id, BorrowModel.status == st)
    return q.all()

@router.get("/{book_id}", response_model=book_schemas.BookOut)
def get_book(book_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    # If book is private and not owner, forbid
    if not book.is_public and book.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this book")
    return book

@router.put("/{book_id}", response_model=book_schemas.BookOut)
def update_book(book_id: int, payload: book_schemas.BookUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(book, field, value)
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(book)
    db.commit()
    return None