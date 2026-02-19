from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    description = Column(String, nullable=True)

    amount = Column(Float, nullable=False)

    status = Column(String, default="pending")
    # pending / completed / approved / rejected

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship back to project
    project = relationship("Project", back_populates="milestones")
