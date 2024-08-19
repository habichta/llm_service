from database import Base
from sqlalchemy import Column, DateTime, Integer, String, Text, func


class Context(Base):
    __tablename__ = "contexts"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class Results(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, index=True)
    context_id = Column(Integer, nullable=False)  # TODO Foreign key
    model_name = Column(String, nullable=False)
    model_version = Column(Integer, nullable=False)
    state = Column(String, index=True)
    result = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
