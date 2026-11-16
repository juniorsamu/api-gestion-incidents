from sqlalchemy import Column, Integer, String, Text

from app.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(120), nullable=False)
    service = Column(String(80), nullable=False)
    priorite = Column(String(20), nullable=False)
    status = Column(String(30), nullable=False)
    description = Column(Text, nullable=False)