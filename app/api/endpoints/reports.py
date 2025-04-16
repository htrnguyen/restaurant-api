from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.reports import Report
from app.schemas.reports import ReportSchema

router = APIRouter()


@router.get("/reports", response_model=List[ReportSchema], tags=["Reports"])
def get_reports(db: Session = Depends(get_db)):
    """Lấy danh sách báo cáo từ database."""
    return db.query(Report).all()


@router.get("/reports/{report_id}", response_model=ReportSchema, tags=["Reports"])
def get_report_by_id(report_id: int, db: Session = Depends(get_db)):
    """Lấy chi tiết báo cáo theo ID từ database."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    return report
