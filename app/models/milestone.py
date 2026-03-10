from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.core.database import Base


class MilestoneStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    approved = "approved"
    rejected = "rejected"


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    description = Column(String, nullable=True)

    amount = Column(Float, nullable=False)

    status = Column(Enum(MilestoneStatus), default=MilestoneStatus.pending)

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="milestones")
    transactions = relationship("Transaction", back_populates="milestone")
    disputes = relationship("Dispute", back_populates="milestone")
