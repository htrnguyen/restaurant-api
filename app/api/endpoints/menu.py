from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.menu import MenuItem
from app.schemas.menu import MenuItemSchema

router = APIRouter()


@router.get("/menu", response_model=List[MenuItemSchema], tags=["Menu"])
def get_menu(db: Session = Depends(get_db)):
    """Lấy danh sách thực đơn từ database."""
    return db.query(MenuItem).all()


@router.put("/menu/{item_id}/availability", tags=["Menu"])
def update_menu_item_availability(
    item_id: int, available: bool, db: Session = Depends(get_db)
):
    """Cập nhật trạng thái sẵn có của món ăn."""
    menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found.")
    menu_item.available = available
    db.commit()
    return {"message": "Menu item availability updated successfully."}
