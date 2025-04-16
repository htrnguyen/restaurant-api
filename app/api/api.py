from fastapi import APIRouter

from app.api.endpoints import (
    auth,
    bills,
    db_check,
    health,
    inventory,
    kitchen,
    menu,
    orders,
    reports,
    tables,
)

router = APIRouter()
router.include_router(health.router, prefix="/health", tags=["Health"])
router.include_router(db_check.router, prefix="/db-check", tags=["Database"])
router.include_router(orders.router, prefix="/orders", tags=["Orders"])
router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(tables.router, prefix="/tables", tags=["Tables"])
router.include_router(kitchen.router, prefix="/kitchen", tags=["Kitchen"])
router.include_router(bills.router, prefix="/bills", tags=["Bills"])
router.include_router(menu.router, prefix="/menu", tags=["Menu"])
router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
router.include_router(reports.router, prefix="/reports", tags=["Reports"])


@router.get("/status", tags=["System"])
def get_status():
    """Kiểm tra trạng thái hệ thống."""
    return {"status": "System is running smoothly."}


@router.get("/version", tags=["System"])
def get_version():
    """Lấy thông tin phiên bản API."""
    return {"version": "1.0.0", "release_date": "2025-04-16"}
