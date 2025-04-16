from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.orders import OrderItem
from app.schemas.orders import OrderItem as OrderItemSchema

router = APIRouter()


class KitchenOrder(BaseModel):
    id: int
    order_item_id: int
    status: str


@router.get("/kitchen/orders", response_model=List[OrderItemSchema], tags=["Kitchen"])
def get_kitchen_orders(db: Session = Depends(get_db)):
    """Lấy danh sách món cần nấu từ database."""
    return (
        db.query(OrderItem).filter(OrderItem.status.in_(["waiting", "cooking"])).all()
    )


@router.put("/kitchen/orders/{order_item_id}/status", tags=["Kitchen"])
def update_kitchen_order_status(
    order_item_id: int, status: str, db: Session = Depends(get_db)
):
    """Cập nhật trạng thái món ăn trong bếp."""
    order_item = db.query(OrderItem).filter(OrderItem.id == order_item_id).first()
    if not order_item:
        raise HTTPException(status_code=404, detail="Order item not found.")
    order_item.status = status
    db.commit()
    return {"message": "Kitchen order status updated successfully."}
