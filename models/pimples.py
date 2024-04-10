from datetime import datetime

from sqlalchemy import Column, Date, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from . import Base


class Pimples(Base):
    __tablename__ = "pimples"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date = Column(Date, default=datetime.now())

    pimples = Column(Integer, nullable=True, default=None)

    user = relationship(
        "User",
        back_populates="pimples",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="_unique_daily_pimples"),
    )
