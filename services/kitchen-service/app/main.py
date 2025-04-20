import json
import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from supabase import Client, create_client

load_dotenv()

app = FastAPI(
    title="Kitchen Service API",
    description="APIs for kitchen operations including ingredient management and order processing",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Kitchen Service API Documentation",
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


class IngredientBase(BaseModel):
    name: str
    quantity: int  # Chuyển từ float sang int
    unit: str
    uom: str  # Thêm trường uom theo database


class IngredientCheckRequest(BaseModel):
    item_id: int


class IngredientUpdate(BaseModel):
    quantity: int


@app.get("/")
async def root():
    return {"message": "Kitchen Service is running"}


@app.get("/health")
async def health_check():
    try:
        start_time = datetime.now()
        # Kiểm tra các bảng cần thiết
        supabase.table("order_items").select("count").limit(1).execute()
        supabase.table("ingredients").select("count").limit(1).execute()
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000

        return {
            "status": "healthy",
            "database": "connected",
            "response_time_ms": round(response_time, 2),
            "timestamp": datetime.now().isoformat(),
            "service": "kitchen-service",
            "tables_checked": ["order_items", "ingredients"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "service": "kitchen-service",
            },
        )


@app.get("/kitchen/pending-orders")
async def get_pending_orders():
    try:
        # Lấy các đơn hàng đang chờ xử lý
        response = (
            supabase.table("orders").select("*").eq("status", "pending").execute()
        )
        orders = response.data

        # Lấy chi tiết các món ăn cho mỗi đơn hàng
        for order in orders:
            items = (
                supabase.table("order_items")
                .select("*")
                .eq("order_id", order["id"])
                .execute()
            )
            order["items"] = items.data

        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/kitchen/order-items/{item_id}/status")
async def update_order_item_status(item_id: int, status: str):
    try:
        # Cập nhật trạng thái món ăn
        response = (
            supabase.table("order_items")
            .update({"status": status, "updated_at": datetime.utcnow().isoformat()})
            .eq("id", item_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Order item not found")

        # Kiểm tra và cập nhật trạng thái đơn hàng nếu cần
        order_id = response.data[0]["order_id"]
        items = (
            supabase.table("order_items").select("*").eq("order_id", order_id).execute()
        )

        all_completed = all(item["status"] == "completed" for item in items.data)
        if all_completed:
            supabase.table("orders").update({"status": "completed"}).eq(
                "id", order_id
            ).execute()

        return {"message": f"Order item status updated to {status}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/kitchen/ingredients")
async def get_ingredients():
    try:
        response = supabase.table("ingredients").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/kitchen/ingredients/{ingredient_id}")
async def update_ingredient_quantity(ingredient_id: int, update: IngredientUpdate):
    try:
        # Update the ingredient quantity by ID
        response = (
            supabase.table("ingredients")  # Fixed table name
            .update({"quantity": update.quantity})
            .eq("id", ingredient_id)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="Ingredient not found")

        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/kitchen/ingredients/report")
async def get_ingredients_report():
    try:
        # Get all ingredients
        response = supabase.table("ingredients").select("*").execute()

        if response.data is None:
            print("Debug: No data returned from ingredients table")
            raise HTTPException(
                status_code=500, detail="Could not fetch ingredients data"
            )

        ingredients = response.data
        if not ingredients:
            return {
                "total_ingredients": 0,
                "low_stock_ingredients": [],
                "normal_stock_ingredients": [],
                "report_date": datetime.now().isoformat(),
            }

        # Categorize ingredients
        low_stock = []
        normal_stock = []

        for ingredient in ingredients:
            try:
                qty = float(ingredient.get("quantity", 0))
                min_qty = float(ingredient.get("min_quantity", 0))

                status = "Cần nhập thêm" if qty <= min_qty else "Đủ dùng"
                item = {
                    "id": ingredient.get("id"),
                    "name": ingredient.get("name", "Unknown"),
                    "current_quantity": qty,
                    "min_quantity": min_qty,
                    "unit": ingredient.get("unit", "N/A"),
                    "status": status,
                }

                if qty <= min_qty:
                    low_stock.append(item)
                else:
                    normal_stock.append(item)
            except (TypeError, ValueError) as e:
                print(
                    f"Debug: Error processing ingredient {ingredient.get('id')}: {str(e)}"
                )
                continue

        return {
            "total_ingredients": len(ingredients),
            "low_stock_count": len(low_stock),
            "normal_stock_count": len(normal_stock),
            "low_stock_ingredients": low_stock,
            "normal_stock_ingredients": normal_stock,
            "report_date": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"Debug: Exception in get_ingredients_report: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error generating ingredients report: {str(e)}"
        )


@app.post("/ingredients/check")
async def check_ingredients_availability(request: IngredientCheckRequest):
    try:
        # Lấy thông tin về nguyên liệu cần thiết cho món ăn
        ingredients_needed = (
            supabase.table("item_ingredient")
            .select("*,ingredient_id(*)")
            .eq("item_id", request.item_id)
            .execute()
        )

        if not ingredients_needed.data:
            return {
                "ingredient_status": "available",
                "message": "Không có thông tin về nguyên liệu cho món này",
            }

        # Kiểm tra số lượng của từng nguyên liệu
        unavailable_ingredients = []
        for item in ingredients_needed.data:
            ingredient = item["ingredient_id"]
            if ingredient["quantity"] < item["quantity"]:
                unavailable_ingredients.append(
                    {
                        "name": ingredient["name"],
                        "required": item["quantity"],
                        "available": ingredient["quantity"],
                        "unit": ingredient["unit"],
                    }
                )

        if unavailable_ingredients:
            return {
                "ingredient_status": "unavailable",
                "missing_ingredients": unavailable_ingredients,
                "message": "Thiếu nguyên liệu cho món này",
            }

        return {
            "ingredient_status": "available",
            "message": "Đủ nguyên liệu cho món này",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/kitchen/ingredients")
async def create_ingredient(ingredient: IngredientBase):
    try:
        response = (
            supabase.table("ingredients")
            .insert(
                {
                    "name": ingredient.name,
                    "quantity": ingredient.quantity,
                    "unit": ingredient.unit,
                    "uom": ingredient.uom,  # Thêm trường uom
                }
            )
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create ingredient")

        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8005)
