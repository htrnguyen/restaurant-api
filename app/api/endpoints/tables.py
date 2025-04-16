from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.tables import Table
from app.schemas.tables import TableSchema

router = APIRouter()

# Mock database for tables
tables_db = [
    {"id": 1, "status": "available"},
    {"id": 2, "status": "occupied"},
    {"id": 3, "status": "reserved"},
]


@router.get("/tables", response_model=List[TableSchema], tags=["Tables"])
def get_tables(db: Session = Depends(get_db)):
    """Lấy danh sách bàn từ database."""
    return db.query(Table).all()


@router.put("/tables/{table_id}/status", tags=["Tables"])
def update_table_status(table_id: int, status: str, db: Session = Depends(get_db)):
    """Cập nhật trạng thái của bàn."""
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found.")
    table.status = status
    db.commit()
    return {"message": "Table status updated successfully."}
