import enum
from datetime import datetime

from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from . import Base


class AppliedAt(enum.Enum):
    MORNING = enum.auto()
    EVENING = enum.auto()


class SkincareCosmetics(Base):
    __tablename__ = "skincare"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date = Column(Date, default=datetime.now())

    skincare = Column(String, nullable=True, default=None)
    applied_at = Column(Enum(AppliedAt), nullable=False)

    user = relationship(
        "User",
        back_populates="skincare",
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id", "date", "applied_at", name="_unique_daily_skincare"
        ),
    )
