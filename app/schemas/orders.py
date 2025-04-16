from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class OrderItemBase(BaseModel):
    menu_item_id: int
    quantity: int
    special_request: Optional[str] = None


class OrderItemCreate(OrderItemBase):
    pass


class OrderItem(OrderItemBase):
    id: int
    order_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class OrderBase(BaseModel):
    table_id: int
    created_by: str


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class Order(OrderBase):
    id: int
    created_at: datetime
    items: List[OrderItem] = []

    class Config:
        orm_mode = True


class OrderOut(Order):
    """Schema cho output của Order, kế thừa từ Order."""

    pass
