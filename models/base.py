from enum import Enum

import sqlalchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    type_annotation_map = {Enum: sqlalchemy.Enum(Enum)}
