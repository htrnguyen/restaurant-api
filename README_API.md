# API Documentation

## Base URLs:

-   User Service: http://localhost:8001
-   Table Service: http://localhost:8002
-   Menu Service: http://localhost:8003
-   Order Service: http://localhost:8004
-   Kitchen Service: http://localhost:8005
-   Payment Service: http://localhost:8006

## Authentication

Tất cả các API yêu cầu xác thực trừ API đăng nhập. Sử dụng thông tin đăng nhập mẫu:

```
{
    "username": "admin",
    "password": "test123"
}
```

## 1. User Service (8001)

### 1.1. Đăng nhập

```http
POST /users/login
```

Request body:

```json
{
    "username": "admin",
    "password": "test123"
}
```

Response:

```json
{
    "id": 1,
    "username": "admin",
    "full_name": "Admin",
    "role": "admin",
    "status": "active"
}
```

### 1.2. Tạo người dùng mới

```http
POST /users
```

Request body:

```json
{
    "username": "test_user",
    "password": "test123",
    "full_name": "Nhân viên test",
    "role": "staff",
    "status": "active"
}
```

### 1.3. Lấy thông tin người dùng

```http
GET /users/{user_id}
```

### 1.4. Cập nhật người dùng

```http
PUT /users/{user_id}
```

Request body:

```json
{
    "full_name": "Tên mới",
    "role": "staff",
    "status": "active"
}
```

### 1.5. Vô hiệu hóa người dùng

```http
DELETE /users/{user_id}
```

## 2. Table Service (8002)

### 2.1. Tạo bàn mới

```http
POST /tables
```

Request body:

```json
{
    "number": 5,
    "status": "available"
}
```

### 2.2. Lấy thông tin bàn

```http
GET /tables/{table_id}
```

### 2.3. Cập nhật trạng thái bàn

```http
PUT /tables/{table_id}
```

Request body:

```json
{
    "status": "occupied"
}
```

### 2.4. Vô hiệu hóa bàn

```http
DELETE /tables/{table_id}
```

## 3. Menu Service (8003)

### 3.1. Tạo món ăn mới

```http
POST /menu-items
```

Request body:

```json
{
    "name": "Món ăn test",
    "description": "Mô tả món ăn",
    "price": 150000,
    "category_id": 1,
    "status": "available"
}
```

### 3.2. Lấy thông tin món ăn

```http
GET /menu-items/{item_id}
```

### 3.3. Cập nhật món ăn

```http
PUT /menu-items/{item_id}
```

Request body:

```json
{
    "price": 180000,
    "status": "available"
}
```

### 3.4. Vô hiệu hóa món ăn

```http
DELETE /menu-items/{item_id}
```

## 4. Kitchen Service (8005)

### 4.1. Tạo nguyên liệu mới

```http
POST /kitchen/ingredients
```

Request body:

```json
{
    "name": "Gia vị test",
    "quantity": 10,
    "unit": "kg",
    "uom": "kg"
}
```

### 4.2. Lấy danh sách nguyên liệu

```http
GET /kitchen/ingredients
```

### 4.3. Cập nhật số lượng nguyên liệu

```http
PUT /kitchen/ingredients/{ingredient_id}
```

Request body:

```json
{
    "quantity": 120
}
```

### 4.4. Lấy báo cáo tồn kho

```http
GET /kitchen/ingredients/report
```

### 4.5. Cập nhật trạng thái món ăn trong đơn hàng

```http
PUT /kitchen/order-items/{item_id}/status
```

Query params:

-   status: completed

## 5. Order Service (8004)

### 5.1. Tạo đơn hàng mới

```http
POST /orders
```

Request body:

```json
{
    "table_id": 1,
    "items": [
        {
            "item_id": 1,
            "quantity": 1
        },
        {
            "item_id": 2,
            "quantity": 1
        }
    ],
    "user_id": 2
}
```

### 5.2. Lấy thông tin đơn hàng

```http
GET /orders/{order_id}
```

### 5.3. Cập nhật trạng thái đơn hàng

```http
PUT /orders/{order_id}/status
```

Request body:

```json
{
    "status": "preparing"
}
```

## 6. Payment Service (8006)

### 6.1. Tạo hóa đơn

```http
POST /payments/bills
```

Request body:

```json
{
    "order_id": 1,
    "payment_method": "cash",
    "created_by": 2
}
```

### 6.2. Xem báo cáo doanh thu theo ngày

```http
GET /payments/reports/daily
```

Query params:

-   date: YYYY-MM-DD

## Testing

Bạn có thể sử dụng các công cụ như Postman hoặc chạy file test có sẵn:

```bash
python test_api_vi.py
```

## Quy trình test đầy đủ:

1. Đăng nhập để lấy thông tin user
2. Tạo và quản lý người dùng (CRUD)
3. Tạo và quản lý món ăn (CRUD)
4. Tạo và quản lý bàn (CRUD)
5. Tạo và quản lý nguyên liệu
6. Quy trình đặt món và thanh toán:
    - Tạo đơn hàng mới
    - Cập nhật trạng thái đơn hàng
    - Cập nhật trạng thái các món
    - Tạo hóa đơn
7. Xem các báo cáo:
    - Báo cáo doanh thu
    - Báo cáo tồn kho

## Dữ liệu mẫu

Để khởi tạo dữ liệu mẫu cho database:

```bash
python init_db.py
```

## Response Status Codes

-   200: Thành công
-   400: Lỗi dữ liệu đầu vào
-   401: Chưa xác thực
-   403: Không có quyền
-   404: Không tìm thấy
-   422: Lỗi validate dữ liệu
-   500: Lỗi server
