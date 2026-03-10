from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class ProjectStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    description = Column(String, nullable=True)

    client_id = Column(String, nullable=False, index=True)
    freelancer_id = Column(String, nullable=True, index=True)

    status = Column(Enum(ProjectStatus), default=ProjectStatus.pending)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    milestones = relationship("Milestone", back_populates="project")
