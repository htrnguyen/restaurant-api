import json
import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
from supabase import Client, create_client

load_dotenv()

app = FastAPI(
    title="Menu Service API",
    description="APIs for managing restaurant menu items and categories",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Menu Service API Documentation",
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

# Constants
VALID_ITEM_STATUSES = ["available", "unavailable", "out_of_stock"]


# Models
class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category_id: int
    status: str = "available"
    img_url: Optional[str] = None

    @validator("status")
    def validate_status(cls, v):
        if v not in VALID_ITEM_STATUSES:
            raise ValueError(
                f"Trạng thái không hợp lệ. Chọn một trong: {', '.join(VALID_ITEM_STATUSES)}"
            )
        return v

    @validator("price")
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("Giá phải lớn hơn 0")
        return v


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    status: Optional[str] = None
    img_url: Optional[str] = None


@app.get("/")
async def root():
    return {"message": "Menu Service is running"}


@app.get("/health")
async def health_check():
    try:
        start_time = datetime.now()
        response = supabase.table("menu_items").select("count").limit(1).execute()
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000

        return {
            "status": "healthy",
            "database": "connected",
            "response_time_ms": round(response_time, 2),
            "timestamp": datetime.now().isoformat(),
            "service": "menu-service",
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "service": "menu-service",
            },
        )


@app.post("/menu-items")
async def create_menu_item(item: MenuItemCreate):
    try:
        # Check if category exists
        category = (
            supabase.table("menu_categories")
            .select("id")
            .eq("id", item.category_id)
            .execute()
        )
        if not category.data:
            raise HTTPException(
                status_code=404,
                detail=f"Danh mục với ID {item.category_id} không tồn tại",
            )

        # Convert price to decimal if it's a string
        if isinstance(item.price, str):
            try:
                item.price = float(item.price)
            except ValueError:
                raise HTTPException(
                    status_code=400, detail="Giá không hợp lệ. Vui lòng nhập số"
                )

        # Check for duplicate name
        existing = (
            supabase.table("menu_items").select("id").eq("name", item.name).execute()
        )
        if existing.data:
            raise HTTPException(
                status_code=400, detail=f"Món ăn với tên '{item.name}' đã tồn tại"
            )

        # Create the menu item
        response = supabase.table("menu_items").insert(item.dict()).execute()

        if not response.data:
            raise HTTPException(
                status_code=400,
                detail="Không thể tạo món ăn. Vui lòng kiểm tra dữ liệu đầu vào",
            )

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi máy chủ: {str(e)}")


@app.get("/menu-items/{item_id}")
async def get_menu_item(item_id: int):
    try:
        response = supabase.table("menu_items").select("*").eq("id", item_id).execute()

        if len(response.data) > 0:
            return response.data[0]
        raise HTTPException(status_code=404, detail="Không tìm thấy món ăn")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/menu-items/{item_id}")
async def update_menu_item(item_id: int, item: MenuItemUpdate):
    try:
        # Get only non-None values for update
        update_data = {k: v for k, v in item.dict().items() if v is not None}

        if not update_data:
            raise HTTPException(status_code=400, detail="Không có dữ liệu cập nhật")

        # Validate status if it's being updated
        if "status" in update_data and update_data["status"] not in VALID_ITEM_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Trạng thái không hợp lệ. Chọn một trong: {', '.join(VALID_ITEM_STATUSES)}",
            )

        # Validate category_id if it's being updated
        if "category_id" in update_data:
            category = (
                supabase.table("menu_categories")
                .select("id")
                .eq("id", update_data["category_id"])
                .execute()
            )
            if not category.data:
                raise HTTPException(status_code=404, detail="Danh mục không tồn tại")

        # Validate price if it's being updated
        if "price" in update_data and update_data["price"] <= 0:
            raise HTTPException(status_code=400, detail="Giá phải lớn hơn 0")

        response = (
            supabase.table("menu_items").update(update_data).eq("id", item_id).execute()
        )

        if len(response.data) > 0:
            return response.data[0]
        raise HTTPException(status_code=404, detail="Không tìm thấy món ăn")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi: {str(e)}")


@app.delete("/menu-items/{item_id}")
async def delete_menu_item(item_id: int):
    try:
        # Soft delete by updating status to 'unavailable'
        response = (
            supabase.table("menu_items")
            .update({"status": "unavailable"})
            .eq("id", item_id)
            .execute()
        )

        if len(response.data) > 0:
            return {"message": "Đã vô hiệu hóa món ăn thành công"}
        raise HTTPException(status_code=404, detail="Không tìm thấy món ăn")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/menu-categories")
async def get_categories():
    try:
        response = supabase.table("menu_categories").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/menu-items")
async def get_menu_items(
    category_id: Optional[int] = None, status: Optional[str] = None
):
    try:
        query = supabase.table("menu_items").select("*")

        if category_id:
            query = query.eq("category_id", category_id)
        if status:
            query = query.eq("status", status)

        response = query.execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)
