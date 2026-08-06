from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db import Base
import uuid
from app.models.community import user_communities

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    mobile = Column(String, unique=True, nullable=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    books = relationship("Book", back_populates="owner")
    borrow_requests = relationship("BorrowRequest", back_populates="requester", foreign_keys="BorrowRequest.requester_id")
    owned_borrow_requests = relationship("BorrowRequest", back_populates="owner", foreign_keys="BorrowRequest.owner_id")
    communities = relationship("Community", secondary=user_communities, back_populates="members")