from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db import Base


class BorrowRequest(Base):
    __tablename__ = 'borrow_requests'

    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    status = Column(String, default='pending')  # pending, approved, rejected, cancelled
    message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    requester = relationship('User', foreign_keys=[requester_id])
    owner = relationship('User', foreign_keys=[owner_id])