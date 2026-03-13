from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.core.database import Base


class MilestoneStatus(str, enum.Enum):
    PENDING = "PENDING"
    FUNDED = "FUNDED"
    COMPLETED = "COMPLETED"
    APPROVED = "APPROVED"
    DISPUTED = "DISPUTED"


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    description = Column(String, nullable=True)

    amount = Column(Numeric(12, 2), nullable=False)

    status = Column(Enum(MilestoneStatus), default=MilestoneStatus.PENDING)

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated_by = Column(String, nullable=True) # clerk_id of last modifier

    # Relationships
    project = relationship("Project", back_populates="milestones")
    transactions = relationship("Transaction", back_populates="milestone")
    disputes = relationship("Dispute", back_populates="milestone")
