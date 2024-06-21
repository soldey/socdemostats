from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    pass


metadata = MetaData()

# Import all the models to ensure they are registered with SQLAlchemy
# from app.models.indicator import Indicator
# from app.models.unit import Unit
# from app.models.population import Population
