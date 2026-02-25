from sqlalchemy import Column, Integer, String, Text
from db import Base


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Integer)
    car = Column(String(100))
