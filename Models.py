from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import declarative_base
from utils import custom_datetime
from sqlalchemy import Column, Integer, Float, DateTime


Base = declarative_base()


class Coil(Base):
    __tablename__ = "coils"
    id = Column(Integer, primary_key=True, index=True)
    length = Column(Float)
    weight = Column(Float)
    date_added = Column(DateTime, default=custom_datetime)
    date_removed = Column(DateTime, default=None)


class CoilCreate(BaseModel):
    length: float
    weight: float


class CoilFilter(BaseModel):
    id_min: Optional[int] = None
    id_max: Optional[int] = None
    weight_min: Optional[float] = None
    weight_max: Optional[float] = None
    length_min: Optional[float] = None
    length_max: Optional[float] = None
    date_removed_start: Optional[datetime] = None
    date_removed_end: Optional[datetime] = None
    date_added_start: Optional[datetime] = None
    date_added_end: Optional[datetime] = None
