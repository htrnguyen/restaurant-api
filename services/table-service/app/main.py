import json
import os
from datetime import datetime
from enum import Enum
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
    title="Table Service API",
    description="APIs for table management in the restaurant",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Table Service API Documentation",
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


class TableStatus(str, Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"


class TableBase(BaseModel):
    status: TableStatus

    @validator("status")
    def validate_status(cls, v):
        if v not in [status.value for status in TableStatus]:
            raise ValueError(
                f"Trạng thái không hợp lệ. Chọn một trong: {', '.join([status.value for status in TableStatus])}"
            )
        return v


class TableOpen(BaseModel):
    table_id: int
    user_id: int


class TableClose(BaseModel):
    table_id: int
    user_id: int


class TableCreate(BaseModel):
    number: int
    status: TableStatus = TableStatus.AVAILABLE


@app.get("/")
async def root():
    return {"message": "Table Service is running"}


@app.get("/health")
async def health_check():
    try:
        start_time = datetime.now()
        response = supabase.table("tables").select("count").limit(1).execute()
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000

        return {
            "status": "healthy",
            "database": "connected",
            "response_time_ms": round(response_time, 2),
            "timestamp": datetime.now().isoformat(),
            "service": "table-service",
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "service": "table-service",
            },
        )


@app.get("/tables")
async def get_tables():
    try:
        response = supabase.table("tables").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tables/{table_id}")
async def get_table(table_id: int):
    try:
        response = (
            supabase.table("tables").select("*").eq("id", table_id).single().execute()
        )
        if not response.data:
            raise HTTPException(status_code=404, detail="Table not found")
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tables/open")
async def open_table(table_open: TableOpen):
    try:
        # Check table exists and is available
        table = (
            supabase.table("tables")
            .select("*")
            .eq("id", table_open.table_id)
            .single()
            .execute()
        )

        if not table.data:
            raise HTTPException(status_code=404, detail="Không tìm thấy bàn")

        if table.data["status"] == TableStatus.OCCUPIED:
            # Check if there's an active opening for this table
            active_openings = (
                supabase.table("opening_table")
                .select("*")
                .eq("table_id", table_open.table_id)
                .eq("status", "open")
                .execute()
            )

            if active_openings.data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Bàn đang được sử dụng bởi người dùng khác từ {active_openings.data[0]['opened_at']}",
                )

        # Update table status and create opening record
        response = (
            supabase.table("tables")
            .update({"status": TableStatus.OCCUPIED})
            .eq("id", table_open.table_id)
            .execute()
        )

        opening = (
            supabase.table("opening_table")
            .insert(
                {
                    "table_id": table_open.table_id,
                    "opened_by": table_open.user_id,
                    "status": "open",
                }
            )
            .execute()
        )

        return {
            "status": "success",
            "message": "Đã mở bàn thành công",
            "opening_id": opening.data[0]["id"] if opening.data else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")


@app.post("/tables/close")
async def close_table(table_close: TableClose):
    try:
        # Check table exists and is occupied
        table = (
            supabase.table("tables")
            .select("*")
            .eq("id", table_close.table_id)
            .single()
            .execute()
        )

        if not table.data:
            raise HTTPException(status_code=404, detail="Không tìm thấy bàn")

        if table.data["status"] == TableStatus.AVAILABLE:
            raise HTTPException(status_code=400, detail="Bàn đã được đóng trước đó")

        # Check if this user opened the table
        opening = (
            supabase.table("opening_table")
            .select("*")
            .eq("table_id", table_close.table_id)
            .eq("opened_by", table_close.user_id)
            .eq("status", "open")
            .single()
            .execute()
        )

        if not opening.data:
            raise HTTPException(
                status_code=403, detail="Bạn không có quyền đóng bàn này"
            )

        # Update table status and close the opening record
        supabase.table("tables").update({"status": TableStatus.AVAILABLE}).eq(
            "id", table_close.table_id
        ).execute()

        # Update the opening record
        supabase.table("opening_table").update(
            {
                "closed_at": datetime.now().isoformat(),
                "closed_by": table_close.user_id,
                "status": "closed",
            }
        ).eq("id", opening.data["id"]).execute()

        return {
            "status": "success",
            "message": "Đã đóng bàn thành công",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")


@app.get("/tables/status")
async def get_tables_status():
    try:
        response = supabase.table("tables").select("id,number,status").execute()
        return {"tables": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/tables/{table_id}")
async def update_table_status(table_id: int, table: TableBase):
    try:
        # Kiểm tra bàn có tồn tại không
        existing_table = (
            supabase.table("tables").select("*").eq("id", table_id).single().execute()
        )
        if not existing_table.data:
            raise HTTPException(status_code=404, detail="Không tìm thấy bàn")

        # Cập nhật trạng thái bàn
        response = (
            supabase.table("tables")
            .update({"status": table.status})
            .eq("id", table_id)
            .execute()
        )

        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tables")
async def create_table(table: TableCreate):
    try:
        # Check if table number already exists
        existing = (
            supabase.table("tables").select("*").eq("number", table.number).execute()
        )
        if existing.data:
            raise HTTPException(
                status_code=400, detail=f"Bàn số {table.number} đã tồn tại"
            )

        response = (
            supabase.table("tables")
            .insert({"number": table.number, "status": table.status})
            .execute()
        )
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/tables/{table_id}")
async def delete_table(table_id: int):
    try:
        # Check if table exists
        existing = (
            supabase.table("tables").select("*").eq("id", table_id).single().execute()
        )
        if not existing.data:
            raise HTTPException(status_code=404, detail="Không tìm thấy bàn")

        # Check if table is in use
        response = (
            supabase.table("tables")
            .update({"status": "inactive"})
            .eq("id", table_id)
            .execute()
        )
        return {"message": "Đã vô hiệu hóa bàn thành công"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
