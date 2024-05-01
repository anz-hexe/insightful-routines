from datetime import datetime

from sqlalchemy import Column, Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from . import Base


class Workouts(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date = Column(Date, default=datetime.now())

    workouts = Column(String, nullable=True, default=None)

    user = relationship(
        "User",
        back_populates="workouts",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="_unique_daily_workouts"),
    )
