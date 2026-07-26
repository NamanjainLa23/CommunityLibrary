from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.schemas import book as book_schemas
from app.core.security import get_current_user
from app.models.book import Book as BookModel

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
def list_public_books(owner_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(BookModel).filter(BookModel.is_public == True)
    if owner_id:
        q = q.filter(BookModel.owner_id == owner_id)
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