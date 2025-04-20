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
    title="Payment Service API",
    description="APIs for managing payments and bills, including payment processing and revenue reports",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
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


class BillCreate(BaseModel):
    order_id: int
    payment_method: str
    created_by: int  # Changed from created_by_user_id to match database field


@app.get("/")
async def root():
    return {"message": "Payment Service is running"}


@app.get("/health")
async def health_check():
    try:
        start_time = datetime.now()
        response = supabase.table("bills").select("count").limit(1).execute()
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000

        return {
            "status": "healthy",
            "database": "connected",
            "response_time_ms": round(response_time, 2),
            "timestamp": datetime.now().isoformat(),
            "service": "payment-service",
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "service": "payment-service",
            },
        )


@app.post("/payments/bills")
async def create_bill(bill: BillCreate):
    try:
        # Get order details first to calculate total amount
        order = (
            supabase.table("orders")
            .select("*")
            .eq("id", bill.order_id)
            .single()
            .execute()
        )
        if not order.data:
            raise HTTPException(status_code=404, detail="Order not found")

        # Create bill record
        bill_data = {
            "order_id": bill.order_id,
            "total_amount": order.data["total_amount"],
            "payment_method": bill.payment_method,
            "user_id": bill.created_by,  # Use user_id instead of created_by
            "created_at": datetime.now().isoformat(),
        }

        response = supabase.table("bills").insert(bill_data).execute()

        # Update order status to "completed"
        supabase.table("orders").update({"status": "completed"}).eq(
            "id", bill.order_id
        ).execute()

        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/payments/bills/{bill_id}")
async def get_bill(bill_id: int):
    try:
        response = (
            supabase.table("bills").select("*").eq("id", bill_id).single().execute()
        )
        if not response.data:
            raise HTTPException(status_code=404, detail="Bill not found")
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/payments/history")
async def get_payment_history(
    start_date: Optional[str] = None, end_date: Optional[str] = None
):
    try:
        query = supabase.table("bills").select("*")

        if start_date:
            query = query.gte("created_at", start_date)
        if end_date:
            query = query.lte("created_at", end_date)

        response = query.execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reports/revenue/summary")
async def get_revenue_summary(
    start_date: Optional[str] = None, end_date: Optional[str] = None
):
    try:
        query = supabase.table("bills").select("*")

        if start_date:
            query = query.gte("created_at", start_date)
        if end_date:
            query = query.lte("created_at", end_date)

        bills = query.execute()

        total_revenue = sum(bill["total_amount"] for bill in bills.data)

        # Group by payment method
        payment_methods = {}
        for bill in bills.data:
            method = bill["payment_method"]
            if method not in payment_methods:
                payment_methods[method] = 0
            payment_methods[method] += bill["total_amount"]

        return {
            "total_revenue": total_revenue,
            "details": {
                "by_payment_method": payment_methods,
                "total_bills": len(bills.data),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/payments/reports/daily")
async def get_daily_revenue(date: str):
    try:
        # Chuyển đổi ngày thành định dạng timestamp
        start_date = f"{date}T00:00:00Z"
        end_date = f"{date}T23:59:59Z"

        # Query bills trong khoảng thời gian
        response = (
            supabase.table("bills")
            .select("*")
            .gte("created_at", start_date)
            .lte("created_at", end_date)
            .execute()
        )
        bills = response.data

        total_revenue = sum(bill["total_amount"] for bill in bills)
        payment_methods = {}
        for bill in bills:
            method = bill["payment_method"]
            payment_methods[method] = (
                payment_methods.get(method, 0) + bill["total_amount"]
            )

        return {
            "date": date,
            "total_revenue": total_revenue,
            "total_bills": len(bills),
            "payment_methods": payment_methods,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Payment Service API Documentation",
        swagger_favicon_url="",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8006)
