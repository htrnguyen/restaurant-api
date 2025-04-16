from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, get_db
from app.crud.orders import create_order, get_order, get_orders
from app.schemas.orders import Order, OrderCreate, OrderOut

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/orders", response_model=Order, tags=["Orders"])
def create_new_order(order: OrderCreate, db: Session = Depends(get_db)):
    return create_order(db, order)


@router.get("/orders/{id}", response_model=Order, tags=["Orders"])
def read_order(id: int, db: Session = Depends(get_db)):
    db_order = get_order(db, id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order


@router.get("/", response_model=list[OrderOut])
def read_orders(db: Session = Depends(get_db)):
    return get_orders(db)
