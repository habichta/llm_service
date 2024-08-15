from sqlalchemy import Column, Integer, String, Text

from app.database import Base


class Context(Base):
    __tablename__ = "contexts"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)


class Models(Base):
    __tablename__ = "models"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
