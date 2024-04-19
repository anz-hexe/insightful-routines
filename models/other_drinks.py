from datetime import datetime

from sqlalchemy import Column, Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from . import Base


class OtherDrinksIntake(Base):
    __tablename__ = "other_drinks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date = Column(Date, default=datetime.now())

    other_drinks = Column(String, nullable=True, default=None)
    user = relationship("User", back_populates="other_drinks")

    __table_args__ = (UniqueConstraint("user_id", "date", name="_unique_other_drinks"),)
