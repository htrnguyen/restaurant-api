from sqlalchemy import Column, Date, Float, Integer, String

from app.core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # daily, monthly, etc.
    date = Column(Date, nullable=False)
    total_revenue = Column(Float, nullable=False)
