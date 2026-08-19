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

    # check if requester has already a pending request for this book
    existing_request = db.query(BorrowModel).filter(BorrowModel.requester_id == current_user.id, BorrowModel.book_id == book.id, BorrowModel.status == 'pending').first()
    if existing_request:
        raise HTTPException(status_code=400, detail="You already have a pending request for this book")

    db.add(br)
    db.commit()
    db.refresh(br)

    # send email to owner (best-effort)
    subject = f"Borrow request: {book.title}"
    body = f"User {current_user.first_name} {current_user.last_name} requests to borrow your book '{book.title}'.\n\nMessage:\n{payload.message or ''}\n\nVisit the app to respond."
    send_email(owner.email or owner.mobile or '',subject, body)

    # attach extra fields for response
    try:
        br.requester_username = current_user.username
        br.owner_username = owner.username
        br.book_title = book.title
        br.book_image_url = getattr(book, 'image_url', None)
    except Exception:
        pass
    return br


@router.get("/me", response_model=List[borrow_schemas.BorrowRequestOut])
def my_requests(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    items = db.query(BorrowModel).filter(BorrowModel.requester_id == current_user.id).all()
    for it in items:
        try:
            it.requester_username = it.requester.username if getattr(it, 'requester', None) else None
            it.owner_username = it.owner.username if getattr(it, 'owner', None) else None
            it.book_title = it.book.title if getattr(it, 'book', None) else None
            it.book_image_url = getattr(it.book, 'image_url', None) if getattr(it, 'book', None) else None
        except Exception:
            pass
    return items


@router.get("/received", response_model=List[borrow_schemas.BorrowRequestOut])
def received_requests(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    items = db.query(BorrowModel).filter(BorrowModel.owner_id == current_user.id).filter(BorrowModel.status.in_(["pending", "approved"])).all()
    for it in items:
        try:
            it.requester_username = it.requester.username if getattr(it, 'requester', None) else None
            it.owner_username = it.owner.username if getattr(it, 'owner', None) else None
            it.book_title = it.book.title if getattr(it, 'book', None) else None
            it.book_image_url = getattr(it.book, 'image_url', None) if getattr(it, 'book', None) else None
        except Exception:
            pass
    return items


@router.get('/lent', response_model=List[borrow_schemas.BorrowRequestOut])
def lent_items(status: str | None = None, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # books lent out by current user (owner)
    q = db.query(BorrowModel).filter(BorrowModel.owner_id == current_user.id)
    if status:
        q = q.filter(BorrowModel.status == status)
    else:
        q = q.filter(BorrowModel.status.in_(["completed", "returned"]))
    items = q.all()
    for it in items:
        try:
            it.requester_username = it.requester.username if getattr(it, 'requester', None) else None
            it.owner_username = it.owner.username if getattr(it, 'owner', None) else None
            it.book_title = it.book.title if getattr(it, 'book', None) else None
            it.book_image_url = getattr(it.book, 'image_url', None) if getattr(it, 'book', None) else None
        except Exception:
            pass
    return items


@router.patch('/{req_id}/status', response_model=borrow_schemas.BorrowRequestOut)
def update_request_status(req_id: int, payload: borrow_schemas.BorrowRequestUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    br = db.query(BorrowModel).filter(BorrowModel.id == req_id).first()
    if not br:
        raise HTTPException(status_code=404, detail='Borrow request not found')
    # only owner can change status
    if br.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail='Only owner can change request status')

    transitions = {
        'pending': {'approved', 'rejected'},
        # allow owner to mark approved borrows as completed or as received back
        'approved': {'completed', 'rejected', 'received'},
        'completed': {"returned"},
        'rejected': set(),
        'received': set(),
    }

    allowed_next = transitions.get(br.status, set())

    if payload.status not in allowed_next:
        raise HTTPException(status_code=400, detail=f"cannot transition from {br.status} to {payload.status}")
        
    br.status = payload.status

    # if owner marks the book as received back, restore book visibility/ownership as needed
    if payload.status == 'returned':
        try:
            book = br.book
            if book:
                # ensure owner remains the owner and make the book public again
                book.owner_id = br.owner_id
                book.is_public = True
                db.add(book)
        except Exception:
            pass

    db.add(br)
    db.commit()
    db.refresh(br)
    try:
        br.requester_username = br.requester.username if getattr(br, 'requester', None) else None
        br.owner_username = br.owner.username if getattr(br, 'owner', None) else None
        br.book_title = br.book.title if getattr(br, 'book', None) else None
        br.book_image_url = getattr(br.book, 'image_url', None) if getattr(br, 'book', None) else None
    except Exception:
        pass

    # notify requester on approve/complete/reject
    try:
        if payload.status == 'approved':
            subject = f"Your borrow request approved: {br.book.title if getattr(br,'book',None) else ''}"
            body = f"Your request to borrow '{br.book.title}' was approved by {br.owner.username if getattr(br,'owner',None) else ''}."
            send_email(br.requester.email or '', subject, body)
        elif payload.status in ('rejected', 'cancelled'):
            subject = f"Your borrow request {payload.status}: {br.book.title if getattr(br,'book',None) else ''}"
            body = f"Your request to borrow '{br.book.title}' was {payload.status} by {br.owner.username if getattr(br,'owner',None) else ''}."
            send_email(br.requester.email or '', subject, body)
        elif payload.status == 'completed':
            subject = f"Borrow completed: {br.book.title if getattr(br,'book',None) else ''}"
            body = f"The borrow for '{br.book.title}' was marked completed by {br.owner.username if getattr(br,'owner',None) else ''}."
            send_email(br.requester.email or '', subject, body)
        elif payload.status == 'received':
            subject = f"Book received back: {br.book.title if getattr(br,'book',None) else ''}"
            body = f"{br.owner.username if getattr(br,'owner',None) else ''} marked the book '{br.book.title}' as received back."
            send_email(br.requester.email or '', subject, body)
    except Exception:
        pass

    return br
