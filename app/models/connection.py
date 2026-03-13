from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.core.database import Base

class ConnectionStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    DECLINED = "DECLINED"

class Connection(Base):
    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, index=True)
    
    # clerk_id of the person who initiated the connection
    sender_id = Column(String, nullable=False, index=True)
    
    # clerk_id of the recipient
    recipient_id = Column(String, nullable=False, index=True)

    # Specific roles to make querying easier if needed
    client_id = Column(String, nullable=False, index=True)
    freelancer_id = Column(String, nullable=False, index=True)

    status = Column(Enum(ConnectionStatus), default=ConnectionStatus.PENDING)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], primaryjoin="Connection.sender_id == User.clerk_id")
    recipient = relationship("User", foreign_keys=[recipient_id], primaryjoin="Connection.recipient_id == User.clerk_id")
