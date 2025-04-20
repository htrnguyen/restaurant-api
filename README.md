# Restaurant API

This is a RESTful API for managing a restaurant's operations, including tables, menu, orders, kitchen, and more. The API is built using FastAPI and is ready for deployment on Vercel.

## Features

-   Manage tables, menu items, and orders.
-   Track kitchen orders and inventory.
-   Generate reports and handle bills.
-   Health check and database status endpoints.

## Requirements

-   Python 3.9+
-   PostgreSQL database

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/restaurant-api.git
    cd restaurant-api
    ```

2. Create a virtual environment and activate it:

    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up the database:

    - Create a PostgreSQL database.
    - Update the database connection string in `app/core/config.py`.
    - Initialize the database:
        ```bash
        python init_db.py
        ```

5. Run the application locally:

    ```bash
    uvicorn app.main:app --reload
    ```

6. Access the API documentation at `http://127.0.0.1:8000/docs`.

## Deployment

This project is configured for deployment on Vercel. To deploy:

1. Install the Vercel CLI:

    ```bash
    npm install -g vercel
    ```

2. Deploy the project:
    ```bash
    vercel
    ```

## File Structure

```
restaurant-api/
├── app/
│   ├── api/                # API endpoints
│   ├── core/               # Core configurations and database setup
│   ├── crud/               # CRUD operations
│   ├── models/             # Database models
│   ├── schemas/            # Pydantic schemas
│   ├── main.py             # Application entry point
├── database.sql            # SQL script for database setup
├── init_db.py              # Script to initialize the database
├── requirements.txt        # Python dependencies
├── vercel.json             # Vercel configuration
└── README.md               # Project documentation
```

## License

This project is licensed under the MIT License.

## Hướng Dẫn Test API Nhà Hàng

## Yêu Cầu

1. Đảm bảo các service đang chạy:
```bash
docker-compose ps
```

2. Các service cần chạy:
- Service Người Dùng: http://localhost:8001
- Service Bàn: http://localhost:8002
- Service Thực Đơn: http://localhost:8003
- Service Đơn Hàng: http://localhost:8004
- Service Bếp: http://localhost:8005
- Service Thanh Toán: http://localhost:8006

## Quy Trình Test

### 1. Đăng Nhập Hệ Thống

```http
POST http://localhost:8001/auth/login
Content-Type: application/json

{
    "username": "admin",
    "password": "test123"
}
```

Lưu token nhận được và sử dụng cho các request tiếp theo:
```http
Authorization: Bearer <your_token>
```

### 2. Kiểm Tra và Đặt Bàn

```http
GET http://localhost:8002/tables?status=trống
Authorization: Bearer <your_token>
```

```http
POST http://localhost:8002/tables/1/reserve
Content-Type: application/json
Authorization: Bearer <your_token>

{
    "customer_name": "Nguyễn Văn A",
    "phone": "0123456789",
    "time": "2025-04-20T11:30:00+07:00",
    "number_of_guests": 4
}
```

### 3. Order Món Ăn

a. Xem danh mục:
```http
GET http://localhost:8003/categories
Authorization: Bearer <your_token>
```

b. Xem món ăn:
```http
GET http://localhost:8003/items?category_id=1
Authorization: Bearer <your_token>
```

c. Tạo đơn hàng:
```http
POST http://localhost:8004/orders
Content-Type: application/json
Authorization: Bearer <your_token>

{
    "table_id": 1,
    "customer_name": "Nguyễn Văn A",
    "items": [
        {
            "item_id": 1,
            "quantity": 2,
            "note": "Ít cay"
        },
        {
            "item_id": 3,
            "quantity": 1,
            "note": "Không hành"
        }
    ]
}
```

### 4. Xử Lý Đơn Hàng trong Bếp

a. Bắt đầu chuẩn bị:
```http
PUT http://localhost:8005/kitchen/orders/1/items/1/status
Content-Type: application/json
Authorization: Bearer <your_token>

{
    "status": "đang_chuẩn_bị",
    "staff_id": 5
}
```

b. Hoàn thành món:
```http
PUT http://localhost:8005/kitchen/orders/1/items/1/status
Content-Type: application/json
Authorization: Bearer <your_token>

{
    "status": "hoàn_thành",
    "note": "Đã chuẩn bị xong"
}
```

### 5. Thanh Toán và Đóng Bàn

a. Tạo hóa đơn:
```http
POST http://localhost:8006/bills
Content-Type: application/json
Authorization: Bearer <your_token>

{
    "order_id": 1,
    "payment_method": "tiền_mặt"
}
```

b. Xử lý thanh toán:
```http
POST http://localhost:8006/bills/1/process
Content-Type: application/json
Authorization: Bearer <your_token>

{
    "payment_method": "tiền_mặt",
    "amount": 235000
}
```

c. Cập nhật trạng thái bàn:
```http
PUT http://localhost:8002/tables/1/status
Content-Type: application/json
Authorization: Bearer <your_token>

{
    "status": "trống"
}
```

## Lưu ý Quan Trọng

1. Đảm bảo thêm header `Authorization` với token đăng nhập cho mọi request
2. Thay thế các ID (table_id, item_id, order_id, ...) phù hợp với dữ liệu thực tế
3. Kiểm tra response code và nội dung trả về sau mỗi request
4. Có thể xem chi tiết request/response schema trong Swagger UI của từng service

## Test bằng Swagger UI

Bạn có thể sử dụng Swagger UI để test API trực quan hơn:

1. Truy cập Swagger UI của từng service:
   - Service Người Dùng: http://localhost:8001/docs
   - Service Bàn: http://localhost:8002/docs
   - Service Thực Đơn: http://localhost:8003/docs
   - Service Đơn Hàng: http://localhost:8004/docs
   - Service Bếp: http://localhost:8005/docs
   - Service Thanh Toán: http://localhost:8006/docs

2. Click vào nút "Authorize" và nhập token đăng nhập
3. Mở endpoint cần test và click "Try it out"
4. Copy request body mẫu tương ứng, dán vào và chỉnh sửa nếu cần
5. Click "Execute" để gửi request

## Kiểm Tra Lỗi

Nếu gặp lỗi, hãy kiểm tra:

1. Tất cả service đã chạy:
```bash
docker-compose ps
```

2. Log của service gặp lỗi:
```bash
docker-compose logs <service_name>
```

3. Token đăng nhập còn hạn và được thêm vào header
4. Request body đúng định dạng và có đầy đủ các trường bắt buộc
