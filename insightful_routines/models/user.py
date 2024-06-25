from datetime import datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from insightful_routines.types import AgeGroup, Allergies, SkinType

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
    morning_skincare = relationship(
        "MorningSkincare",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )
    evening_skincare = relationship(
        "EveningSkincare",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )
    breakfast = relationship(
        "BreakfastIntake",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )
    dinner = relationship(
        "DinnerIntake",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )
    lunch = relationship(
        "LunchIntake",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )
    hot_drinks = relationship(
        "HotDrinksIntake",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )
    milk_drinks = relationship(
        "MilkDrinksIntake",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )
    other_drinks = relationship(
        "OtherDrinksIntake",
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
    date = Column(Date, default=datetime.now())
    question_old = Column(Enum(*AgeGroup.as_list()))
    question_allergen = Column(Enum(*Allergies.as_list()))
    question_medicines = Column(Enum("yes", "no"))
    question_skin_type = Column(Enum(*SkinType.as_list()))
    user = relationship(
        "User",
        back_populates="answers",
    )

    __table_args__ = (UniqueConstraint("user_id"),)
