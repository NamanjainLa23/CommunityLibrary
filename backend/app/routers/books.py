from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.db import get_db
from sqlalchemy.orm import joinedload
from app.schemas import book as book_schemas
from app.schemas.book import BookFromISBN
from app.core.security import get_current_user
from app.models.book import Book as BookModel
from app.models.user import User as UserModel
import jwt
from app.core.security import SECRET_KEY, ALGORITHM
from fastapi import Request
from app.core.isbn import fetch_book_by_isbn
from uuid import UUID
from app.models.borrow import BorrowRequest as BorrowModel

router = APIRouter(prefix="/api/books", tags=["books"])

@router.post("/", response_model=book_schemas.BookOut, status_code=status.HTTP_201_CREATED)
def create_book(payload: book_schemas.BookCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    book = BookModel(
        owner_id=current_user.id,
        title=payload.title,
        author=payload.author,
        isbn=payload.isbn,
        is_public=payload.is_public if payload.is_public is not None else True,
        description = payload.description,
        image_url = payload.image_url
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
        description = meta.get("description")
        image_url = meta.get("image_url")
        isbn_val = meta.get("isbn") or payload.isbn

    
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
    lent_book_ids = db.query(BorrowModel.book_id).filter(BorrowModel.owner_id == current_user.id, BorrowModel.status == "completed").subquery()
    return (db.query(BookModel).filter(BookModel.owner_id == current_user.id,~BookModel.id.in_(lent_book_ids),).all())

@router.get("/public", response_model=List[book_schemas.BookOut])
def list_public_books(request: Request, owner_id: Optional[UUID] = None, owner_username: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(BookModel).filter(BookModel.is_public == True)
    if owner_id:
        q = q.filter(BookModel.owner_id == owner_id)
    elif owner_username:
        user = db.query(UserModel).filter((UserModel.username == owner_username) | (UserModel.mobile == owner_username)).first()
        if not user:
            return []

    # if request has an Authorization header, restrict visible books to users in the same communities
    auth = request.headers.get('authorization')
    current_user = None
    if auth and auth.lower().startswith('bearer '):
        token = auth.split(None, 1)[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            mobile = payload.get('sub')
            if mobile:
                current_user = db.query(UserModel).filter(UserModel.mobile == mobile).first()
        except Exception:
            current_user = None

    books = q.options(joinedload(BookModel.owner)).all()

    if current_user:
        # build set of allowed owner ids from communities
        allowed = set()
        try:
            for c in current_user.communities:
                for m in c.members:
                    allowed.add(m.id)
        except Exception:
            allowed = set()
        books = [b for b in books if b.owner_id in allowed]

    for b in books:
        try:
            b.owner_username = b.owner.username if getattr(b, 'owner', None) else None
        except Exception:
            b.owner_username = None

    return books


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
    books = q.options(joinedload(BookModel.owner)).all()

    for b in books:
        try:
            b.owner_username = b.owner.username if getattr(b, 'owner', None) else None
        except Exception:
            b.owner_username = None

    return books


@router.get('/borrowed', response_model=List[book_schemas.BookOut])
def list_borrowed_books(status: Optional[str] = None, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Return books borrowed by the current user. By default returns approved borrows.

    Optional query param `status` can filter by borrow request status (e.g. pending, approved).
    """
    st = status or 'completed'
    q = db.query(BookModel).join(BorrowModel, BorrowModel.book_id == BookModel.id).filter(BorrowModel.requester_id == current_user.id, BorrowModel.status == st)
    books = q.options(joinedload(BookModel.owner)).all()

    for b in books:
        try:
            b.owner_username = b.owner.username if getattr(b, 'owner', None) else None
        except Exception:
            b.owner_username = None

    return books

@router.get("/{book_id}", response_model=book_schemas.BookOut)
def get_book(book_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    # If book is private and not owner, forbid
    if not book.is_public and book.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this book")
    return book

@router.put("/{book_id}", response_model=book_schemas.BookOut)
def update_book(book_id: UUID, payload: book_schemas.BookUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
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
def delete_book(book_id: UUID, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if book.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(book)
    db.commit()
    return None