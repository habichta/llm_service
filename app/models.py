from database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Text


class Context(Base):
    __tablename__ = "contexts"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)


class Models(Base):
    __tablename__ = "models"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)


class Results(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, index=True)
    context_id = Column(Integer, nullable=False)  # TODO Foreign key
    model_id = Column(Integer, nullable=False)  # TODO Foreign key
    state = Column(String, index=True)
    result = Column(Text, nullable=True)
