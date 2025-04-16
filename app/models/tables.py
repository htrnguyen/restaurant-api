from sqlalchemy import Column, Integer, String

from app.core.database import Base


class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, nullable=False)
