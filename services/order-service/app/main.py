import json
import os
from datetime import datetime
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from supabase import Client, create_client

load_dotenv()


# Define request model
class OrderItem(BaseModel):
    item_id: int
    quantity: int
    note: Optional[str] = None
    price: Optional[float] = None  # Make price optional


class OrderCreate(BaseModel):
    table_id: int
    items: List[OrderItem]
    user_id: Optional[int] = None


class OrderStatusUpdate(BaseModel):
    status: str


class OrderItemAdjust(BaseModel):
    item_id: int
    quantity: int
    action: str  # 'add', 'modify', 'remove'
    note: Optional[str] = None


app = FastAPI(
    title="Order Service API",
    description="APIs for managing restaurant orders including order creation, status updates, and order details",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Order Service API Documentation",
        swagger_favicon_url="",
    )


# Thêm CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Tùy chỉnh JSONResponse để xử lý Unicode
class UnicodeJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


# Override default JSONResponse
app.router.default_response_class = UnicodeJSONResponse

supabase: Client = create_client(
    supabase_url=os.getenv("SUPABASE_URL"), supabase_key=os.getenv("SUPABASE_KEY")
)


@app.get("/")
async def root():
    return {"message": "Order Service is running"}


@app.get("/health")
async def health_check():
    try:
        start_time = datetime.now()
        response = supabase.table("orders").select("count").limit(1).execute()
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000

        # Kiểm tra thêm bảng order_items
        supabase.table("order_items").select("count").limit(1).execute()

        return {
            "status": "healthy",
            "database": "connected",
            "response_time_ms": round(response_time, 2),
            "timestamp": datetime.now().isoformat(),
            "service": "order-service",
            "tables_checked": ["orders", "order_items"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "service": "order-service",
            },
        )


@app.post("/orders")
async def create_order(order: OrderCreate):
    try:
        # Fetch menu items to get prices
        menu_items = {}
        for item in order.items:
            response = (
                supabase.table("menu_items")
                .select("price")
                .eq("id", item.item_id)
                .single()
                .execute()
            )
            if not response.data:
                raise HTTPException(
                    status_code=404, detail=f"Menu item {item.item_id} not found"
                )
            menu_items[item.item_id] = response.data["price"]

        # Tạo đơn hàng mới
        order_data = {
            "table_id": order.table_id,
            "user_id": order.user_id,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "total_amount": sum(
                menu_items[item.item_id] * item.quantity for item in order.items
            ),
        }

        order_response = supabase.table("orders").insert(order_data).execute()

        if not order_response.data:
            raise HTTPException(status_code=500, detail="Failed to create order")

        order_id = order_response.data[0]["id"]

        # Tạo chi tiết đơn hàng
        order_items = [
            {
                "order_id": order_id,
                "item_id": item.item_id,
                "quantity": item.quantity,
                "price": menu_items[item.item_id],
                "note": item.note,
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
            }
            for item in order.items
        ]

        items_response = supabase.table("order_items").insert(order_items).execute()

        return {
            "order_id": order_id,
            "message": "Order created successfully",
            "items": items_response.data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/orders")
async def get_orders(
    table_id: Optional[int] = None,
    status: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
):
    try:
        query = supabase.table("orders").select("*")

        if table_id:
            query = query.eq("table_id", table_id)
        if status:
            query = query.eq("status", status)
        if from_date:
            query = query.gte("created_at", from_date)
        if to_date:
            query = query.lte("created_at", to_date)

        response = query.execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    try:
        response = (
            supabase.table("orders").select("*").eq("id", order_id).single().execute()
        )
        if not response.data:
            raise HTTPException(status_code=404, detail="Order not found")

        # Lấy thêm chi tiết đơn hàng
        items = (
            supabase.table("order_items").select("*").eq("order_id", order_id).execute()
        )
        response.data["items"] = items.data
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


VALID_STATUS_TRANSITIONS = {
    "pending": ["preparing", "cancelled"],
    "preparing": ["ready", "cancelled"],
    "ready": ["completed", "cancelled"],
    "completed": [],  # No further transitions allowed
    "cancelled": [],  # No further transitions allowed
}


@app.put("/orders/{order_id}/status")
async def update_order_status(order_id: int, status_update: OrderStatusUpdate):
    try:
        # Get current order status
        order_response = (
            supabase.table("orders")
            .select("status")
            .eq("id", order_id)
            .single()
            .execute()
        )
        if not order_response.data:
            raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")

        current_status = order_response.data["status"]
        new_status = status_update.status

        # Validate status transition
        if new_status not in VALID_STATUS_TRANSITIONS[current_status]:
            valid_transitions = ", ".join(VALID_STATUS_TRANSITIONS[current_status])
            raise HTTPException(
                status_code=400,
                detail=f"Không thể chuyển trạng thái từ '{current_status}' sang '{new_status}'. Chỉ cho phép chuyển sang: {valid_transitions}",
            )

        # Update order status
        response = (
            supabase.table("orders")
            .update({"status": new_status})
            .eq("id", order_id)
            .execute()
        )
        if not response.data:
            raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")

        # Update all order items status
        supabase.table("order_items").update({"status": new_status}).eq(
            "order_id", order_id
        ).execute()

        return {
            "message": f"Cập nhật trạng thái đơn hàng thành '{new_status}'",
            "order_id": order_id,
            "status": new_status,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Lỗi cập nhật trạng thái đơn hàng: {str(e)}"
        )


@app.put("/orders/{order_id}/adjust")
async def adjust_order(order_id: int, items: List[OrderItemAdjust]):
    try:
        # Verify order exists and is in adjustable state
        order = (
            supabase.table("orders").select("*").eq("id", order_id).single().execute()
        )
        if not order.data:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.data["status"] not in ["pending", "preparing"]:
            raise HTTPException(
                status_code=400, detail="Order cannot be adjusted in current state"
            )

        for item in items:
            if item.action == "add":
                # Add new item to order
                new_item = {
                    "order_id": order_id,
                    "item_id": item.item_id,
                    "quantity": item.quantity,
                    "status": "pending",
                    "note": item.note,
                    "created_at": datetime.utcnow().isoformat(),
                }
                supabase.table("order_items").insert(new_item).execute()

            elif item.action == "modify":
                # Modify existing item quantity
                supabase.table("order_items").update(
                    {"quantity": item.quantity, "note": item.note}
                ).eq("order_id", order_id).eq("item_id", item.item_id).execute()

            elif item.action == "remove":
                # Remove item from order
                supabase.table("order_items").delete().eq("order_id", order_id).eq(
                    "item_id", item.item_id
                ).execute()

        # Recalculate total amount
        items_response = (
            supabase.table("order_items").select("*").eq("order_id", order_id).execute()
        )
        total_amount = sum(
            item["price"] * item["quantity"] for item in items_response.data
        )

        # Update order total
        supabase.table("orders").update({"total_amount": total_amount}).eq(
            "id", order_id
        ).execute()

        return {"message": "Order adjusted successfully", "order_id": order_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/orders/{order_id}/items/{item_id}")
async def delete_order_item(order_id: int, item_id: int):
    try:
        # Verify order exists and is in cancellable state
        order = (
            supabase.table("orders").select("*").eq("id", order_id).single().execute()
        )
        if not order.data:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.data["status"] not in ["pending", "preparing"]:
            raise HTTPException(
                status_code=400,
                detail="Order items cannot be cancelled in current state",
            )

        # Delete the order item
        response = (
            supabase.table("order_items")
            .delete()
            .eq("order_id", order_id)
            .eq("item_id", item_id)
            .execute()
        )
        if not response.data:
            raise HTTPException(status_code=404, detail="Order item not found")

        # Recalculate total amount
        items_response = (
            supabase.table("order_items").select("*").eq("order_id", order_id).execute()
        )
        total_amount = sum(
            item["price"] * item["quantity"] for item in items_response.data
        )

        # Update order total
        supabase.table("orders").update({"total_amount": total_amount}).eq(
            "id", order_id
        ).execute()

        return {"message": "Order item cancelled successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8004)
