from datetime import datetime

from sqlalchemy import Column, Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from . import Base


class WaterIntake(Base):
    __tablename__ = "water"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date = Column(Date, default=datetime.now())

    water = Column(String, nullable=True, default=None)

    user = relationship(
        "User",
        back_populates="water",
    )

    __table_args__ = (UniqueConstraint("user_id", "date", name="_unique_daily_water"),)
