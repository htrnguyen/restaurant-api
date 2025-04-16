from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# Mock database for inventory
inventory_db = [
    {"id": 1, "name": "Tomato", "quantity": 100},
    {"id": 2, "name": "Cheese", "quantity": 50},
    {"id": 3, "name": "Pasta", "quantity": 200},
]


class InventoryItem(BaseModel):
    id: int
    name: str
    quantity: int


@router.get("/inventory", response_model=List[InventoryItem], tags=["Inventory"])
def get_inventory():
    """Lấy danh sách nguyên liệu."""
    return inventory_db


@router.put("/inventory/{item_id}/update", tags=["Inventory"])
def update_inventory_item(item_id: int, quantity: int):
    """Cập nhật số lượng nguyên liệu."""
    for item in inventory_db:
        if item["id"] == item_id:
            item["quantity"] = quantity
            return {"message": "Inventory item updated successfully."}
    raise HTTPException(status_code=404, detail="Inventory item not found.")
