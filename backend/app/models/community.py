from sqlalchemy import Column, String, Table, ForeignKey, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db import Base
import uuid

# association table
from sqlalchemy import MetaData

user_communities = Table(
    'user_communities', Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('community_id', UUID(as_uuid=True), ForeignKey('communities.id', ondelete='CASCADE'), primary_key=True),
)


class Community(Base):
    __tablename__ = 'communities'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), unique=True, nullable=False)

    members = relationship('User', secondary=user_communities, back_populates='communities')

    def __repr__(self):
        return f"<Community {self.name}>"


class CommunityMembership(Base):
    __tablename__ = "community_memberships"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    community_id = Column(UUID(as_uuid=True), ForeignKey("communities.id", ondelete="CASCADE"), primary_key=True)
    role = Column(String, nullable=False, default="member")  # admin | member


class CommunityJoinRequest(Base):
    __tablename__ = "community_join_requests"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    community_id = Column(UUID(as_uuid=True), ForeignKey("communities.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String, default="pending")  # pending | approved | rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())