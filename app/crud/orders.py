from sqlalchemy.orm import Session

from app.models.orders import Order, OrderItem
from app.schemas.orders import OrderCreate, OrderItemCreate


def create_order(db: Session, order: OrderCreate):
    db_order = Order(table_id=order.table_id, created_by=order.created_by)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    for item in order.items:
        db_item = OrderItem(order_id=db_order.id, **item.dict())
        db.add(db_item)

    db.commit()
    return db_order


def get_order(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()


def get_orders(db: Session):
    return db.query(Order).all()
