from datetime import date

from pydantic import BaseModel


class ReportSchema(BaseModel):
    id: int
    type: str  # daily, monthly, etc.
    date: date
    total_revenue: float

    class Config:
        orm_mode = True
