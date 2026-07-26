from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.schemas import book as book_schemas
from app.schemas.book import BookFromISBN
from app.core.security import get_current_user
from app.models.book import Book as BookModel
from app.core.isbn import fetch_book_by_isbn

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

@router.post("/by-isbn", response_model=book_schemas.BookOut, status_code=status.HTTP_201_CREATED)
def create_book_from_isbn(payload: BookFromISBN, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    existing = None
    if payload.isbn:
        exisiting = db.query(BookModel).filter(BookModel.isbn == payload.isbn).first()
    
    if exisiting:
        title = exisiting.title
        author = exisiting.author
        description = exisiting.description
        image_url = exisiting.image_url
        isbn_val = exisiting.isbn or payload.isbn

    else:
        meta = fetch_book_by_isbn(payload.isbn)
        if not meta:
            raise HTTPException(status_code=404, detail="Book metadata not found for given ISBN")
        title = meta.get("title") or f"Unknown title ({payload.isbn})"
        author = meta.get("author")
        description = meta.description
        image_url = meta.image_url
        isbn_val = meta.isbn or payload.isbn

    
    book = BookModel(
        owner_id = current_user.id,
        title = title,
        author = author,
        isbn = isbn_val,
        is_public = payload.is_public if payload.is_public is not None else True,
        description = description,
        image_url = image_url
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