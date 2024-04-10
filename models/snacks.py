import enum
from datetime import datetime

from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from . import Base


class SnacksAppliedAt(enum.Enum):
    SNACKS = enum.auto()


class SnacksIntake(Base):
    __tablename__ = "snacks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date = Column(Date, default=datetime.now())

    snacks = Column(String, nullable=True, default=None)
    snacks_applied_at = Column(Enum(SnacksAppliedAt), nullable=False)

    user = relationship(
        "User",
        back_populates="snacks",
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id", "date", "snacks_applied_at", name="_unique_daily_snacks"
        ),
    )
