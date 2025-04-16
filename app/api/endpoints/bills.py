from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.orders import Order

router = APIRouter()


class Bill(BaseModel):
    id: int
    order_id: int
    total_amount: float
    status: str


@router.post("/bills", tags=["Bills"])
def create_bill(order_id: int, total_amount: float, db: Session = Depends(get_db)):
    """Tạo hóa đơn mới."""
    bill = Order(order_id=order_id, total_amount=total_amount, status="unpaid")
    db.add(bill)
    db.commit()
    return bill


@router.put("/bills/{bill_id}/pay", tags=["Bills"])
def pay_bill(bill_id: int, db: Session = Depends(get_db)):
    """Thanh toán hóa đơn."""
    bill = db.query(Order).filter(Order.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found.")
    if bill.status == "paid":
        raise HTTPException(status_code=400, detail="Bill is already paid.")
    bill.status = "paid"
    db.commit()
    return {"message": "Bill paid successfully."}
