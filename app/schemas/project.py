from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime

from app.core.database import Base


class Dispute(Base):
    __tablename__ = "disputes"

    id = Column(Integer, primary_key=True, index=True)

    milestone_id = Column(Integer, ForeignKey("milestones.id"), nullable=False)

    raised_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    reason = Column(String, nullable=False)

    status = Column(String, default="open")
    # open / under_review / resolved / rejected

    resolution_note = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
