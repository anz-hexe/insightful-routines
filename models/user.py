from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from . import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    chat_id = Column(Integer, unique=True)
    date_created = Column(DateTime, server_default=func.now())
    answers = relationship(
        "UserAnswer",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )

    skincare = relationship(
        "SkincareCosmetics",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )
    food = relationship(
        "FoodIntake",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )
    drinks = relationship(
        "DrinksIntake",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )
    snacks = relationship(
        "SnacksIntake",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )
    stress_level = relationship(
        "StressLevel",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )
    supplements = relationship(
        "Supplements",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )
    workouts = relationship(
        "Workouts",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )
    water = relationship(
        "WaterIntake",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )
    pimples = relationship(
        "Pimples",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )
    face_photo = relationship(
        "FacePhoto",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )


class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    question_old = Column(Enum("up to 25", "25 - 30", "30 - 45", "45+"))
    question_allergen = Column(Enum("yes", "no"))
    question_medicines = Column(Enum("yes", "no"))
    question_skin_type = Column(
        Enum("normal", "dry", "oily", "combination", "sensitive")
    )
    user = relationship(
        "User",
        back_populates="answers",
    )

    __table_args__ = (UniqueConstraint("user_id"),)
