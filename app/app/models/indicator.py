from sqlalchemy import Table, Column, Integer, String, ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from .base import metadata, Base
from app.crud.unit import get_unit

class Indicator(Base):
    __tablename__ = "indicators"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    unit_id = Column(Integer, ForeignKey("units.id"))
    unit = relationship("Unit")
    __table_args__ = (UniqueConstraint('name', 'unit_id', name='_name_unit_uc'),)
    

class AggregatedIndicatorValue(Base):
    __tablename__ = "aggregated_indicator_values"
    id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(Integer, ForeignKey("indicators.id"), index=True, unique=False)
    territory_id = Column(Integer, nullable=False, index=True, unique=False)
    year = Column(Integer, nullable=False, index=True, unique=False)
    value = Column(Float, nullable=False)
    source = Column(String, nullable=False)
    indicator = relationship("Indicator")

class DetailedIndicatorValue(Base):
    __tablename__ = "detailed_indicator_values"
    id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(Integer, ForeignKey("indicators.id"), index=True, unique=False)
    territory_id = Column(Integer, nullable=False, index=True, unique=False)
    year = Column(Integer, nullable=False, index=True, unique=False)
    age_start = Column(Integer, nullable=False)
    age_end = Column(Integer, nullable=False)
    gender = Column(String, nullable=True)
    source = Column(String, nullable=False)
    indicator = relationship("Indicator")