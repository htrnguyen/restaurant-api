from sqlalchemy.orm import Session

from app.core.database import Base, SessionLocal, engine
from app.models.menu import MenuItem
from app.models.orders import Order, OrderItem
from app.models.tables import Table


def init_db():
    # Xóa toàn bộ database và tạo lại từ đầu
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Thêm dữ liệu mẫu
    db: Session = SessionLocal()

    try:
        # Dữ liệu mẫu cho menu (tiếng Việt)
        menu_items = [
            MenuItem(name="Bánh mì Việt Nam", price=1.5, available=True),
            MenuItem(name="Phở bò", price=3.0, available=True),
            MenuItem(name="Cà phê sữa đá", price=1.0, available=True),
            MenuItem(name="Chè ba màu", price=1.2, available=False),
        ]
        db.add_all(menu_items)

        # Dữ liệu mẫu cho bàn (tiếng Việt)
        tables = [
            Table(id=1, status="Trống"),
            Table(id=2, status="Đang sử dụng"),
            Table(id=3, status="Đã đặt trước"),
        ]
        db.add_all(tables)

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized and sample data added.")
