import enum
from datetime import datetime

from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from . import Base


class DrinksAppliedAt(enum.Enum):
    DRINKS_HOT = enum.auto()
    DRINKS_OTHER = enum.auto()
    DRINKS_MILK = enum.auto()


class DrinksIntake(Base):
    __tablename__ = "drinks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date = Column(Date, default=datetime.now())

    drinks = Column(String, nullable=True, default=None)
    drinks_applied_at = Column(Enum(DrinksAppliedAt), nullable=False)

    user = relationship("User", back_populates="drinks")

    __table_args__ = (
        UniqueConstraint(
            "user_id", "date", "drinks_applied_at", name="_unique_daily_drinks"
        ),
    )
