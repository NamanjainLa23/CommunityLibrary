from sqlalchemy import Column, String, Table, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db import Base
import uuid
from sqlalchemy import MetaData

user_communities = Table(
    "user_communities",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("community_id", UUID(as_uuid=True), ForeignKey("communities.id", ondelete="CASCADE"), primary_key=True),
)


class Community(Base):
    __tablename__ = "communities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), unique=True, nullable=False)
    members = relationship("User", secondary=user_communities, back_populates="communities")

    def __repr__(self):
        return f"<Community {self.name}>"