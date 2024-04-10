import enum
from datetime import datetime

from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from . import Base


class FoodAppliedAt(enum.Enum):
    BREAKFAST = enum.auto()
    LUNCH = enum.auto()
    DINNER = enum.auto()


class FoodIntake(Base):
    __tablename__ = "food"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date = Column(Date, default=datetime.now())

    food = Column(String, nullable=True, default=None)
    food_applied_at = Column(Enum(FoodAppliedAt), nullable=False)

    user = relationship(
        "User",
        back_populates="food",
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id", "date", "food_applied_at", name="_unique_daily_food"
        ),
    )
