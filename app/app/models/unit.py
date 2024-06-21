from sqlalchemy import Column, Integer, String
from app.models.base import Base


class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    unit_name = Column(String, unique=True, index=True)
