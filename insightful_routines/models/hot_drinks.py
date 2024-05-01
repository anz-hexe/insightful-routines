from datetime import datetime

from sqlalchemy import Column, Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from . import Base


class HotDrinksIntake(Base):
    __tablename__ = "hot_drinks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date = Column(Date, default=datetime.now())

    hot_drinks = Column(String, nullable=True, default=None)
    user = relationship("User", back_populates="hot_drinks")

    __table_args__ = (UniqueConstraint("user_id", "date", name="_unique_hot_drinks"),)
