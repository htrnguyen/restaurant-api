import json
import os
from datetime import datetime
from typing import Optional

import bcrypt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from supabase import Client, create_client

# Load environment variables
load_dotenv()

# Get environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception(
        "Missing required environment variables: SUPABASE_URL and SUPABASE_KEY must be set"
    )

app = FastAPI(
    title="User Service API",
    description="APIs for user management including authentication and authorization",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
)

# Add CORS middleware
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

# Initialize Supabase client
try:
    supabase: Client = create_client(
        supabase_url=SUPABASE_URL, supabase_key=SUPABASE_KEY
    )
except Exception as e:
    print(f"Failed to initialize Supabase client: {str(e)}")
    raise


class UserBase(BaseModel):
    username: str
    full_name: str
    role: str
    status: str = "active"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


@app.get("/")
async def root():
    return {"message": "User Service is running"}


@app.get("/users")
async def get_users(role: Optional[str] = None, status: Optional[str] = None):
    """Lấy danh sách người dùng với tùy chọn lọc theo role và status"""
    try:
        query = supabase.table("users").select("id,username,full_name,role,status")

        if role:
            query = query.eq("role", role)
        if status:
            query = query.eq("status", status)

        response = query.execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    try:
        # Kiểm tra kết nối database bằng cách thực hiện một truy vấn đơn giản
        start_time = datetime.now()
        response = supabase.table("users").select("count").limit(1).execute()
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000

        return {
            "status": "healthy",
            "database": "connected",
            "response_time_ms": round(response_time, 2),
            "timestamp": datetime.now().isoformat(),
            "service": "user-service",
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "service": "user-service",
            },
        )


@app.post("/users")
async def create_user(user: UserCreate):
    try:
        # Check if username already exists
        existing_user = (
            supabase.table("users").select("id").eq("username", user.username).execute()
        )
        if existing_user.data:
            raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại")

        # Hash password
        hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())

        # Create user data
        user_data = {
            "username": user.username,
            "password": hashed.decode(),
            "full_name": user.full_name,
            "role": user.role,
            "status": user.status,
        }

        # Insert into database
        response = supabase.table("users").insert(user_data).execute()

        if len(response.data) > 0:
            created_user = response.data[0]
            # Remove password from response
            created_user.pop("password", None)
            return created_user
        else:
            raise HTTPException(status_code=400, detail="Không thể tạo người dùng")
    except HTTPException:
        raise
    except Exception as e:
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại")
        raise HTTPException(status_code=400, detail=f"Lỗi tạo người dùng: {str(e)}")


@app.get("/users/{user_id}")
async def get_user(user_id: str):
    try:
        user_id_int = int(user_id)
        response = (
            supabase.table("users")
            .select("id,username,full_name,role,status")
            .eq("id", user_id_int)
            .execute()
        )

        if len(response.data) > 0:
            return response.data[0]
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    except ValueError:
        raise HTTPException(status_code=400, detail="ID người dùng không hợp lệ")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/users/{user_id}")
async def update_user(user_id: str, user: UserUpdate):
    try:
        user_id_int = int(user_id)
        # Get only non-None values for update
        update_data = {k: v for k, v in user.dict().items() if v is not None}

        if not update_data:
            raise HTTPException(status_code=400, detail="Không có dữ liệu cập nhật")

        response = (
            supabase.table("users").update(update_data).eq("id", user_id_int).execute()
        )

        if len(response.data) > 0:
            return response.data[0]
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    except ValueError:
        raise HTTPException(status_code=400, detail="ID người dùng không hợp lệ")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    try:
        user_id_int = int(user_id)
        # Soft delete by updating status to 'inactive'
        response = (
            supabase.table("users")
            .update({"status": "inactive"})
            .eq("id", user_id_int)
            .execute()
        )

        if len(response.data) > 0:
            return {"message": "Đã vô hiệu hóa người dùng thành công"}
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    except ValueError:
        raise HTTPException(status_code=400, detail="ID người dùng không hợp lệ")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/users/login")
async def login(request: LoginRequest):
    try:
        response = (
            supabase.table("users")
            .select("*")
            .eq("username", request.username)
            .execute()
        )

        if len(response.data) == 0:
            raise HTTPException(
                status_code=401, detail="Sai tên đăng nhập hoặc mật khẩu"
            )

        user = response.data[0]

        if not bcrypt.checkpw(request.password.encode(), user["password"].encode()):
            raise HTTPException(
                status_code=401, detail="Sai tên đăng nhập hoặc mật khẩu"
            )

        # Remove password from response
        user.pop("password", None)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="User Service API Documentation",
        swagger_favicon_url="",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
