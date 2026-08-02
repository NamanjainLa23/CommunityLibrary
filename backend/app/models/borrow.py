from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


class BorrowRequest(Base):
    __tablename__ = 'borrow_requests'

    id = Column(Integer, primary_key=True, index=True)

    requester_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    book_id = Column(
        UUID(as_uuid=True),
        ForeignKey("books.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(String, default='pending')  # pending, approved, rejected, cancelled
    message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    requester = relationship(
    "User",
    back_populates="borrow_requests",
    foreign_keys=[requester_id],
    )
    
    owner = relationship(
    "User",
    back_populates="owned_borrow_requests",  # not "borrow_requests"
    foreign_keys=[owner_id],
    )
    
    book = relationship(
        "Book",
        back_populates="borrow_requests",
        foreign_keys=[book_id],
    )