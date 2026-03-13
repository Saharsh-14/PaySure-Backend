from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
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

    status = Column(Enum(ConnectionStatus), default=ConnectionStatus.ACTIVE) # Simulating auto-accept for now as per "invite" requirements
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
