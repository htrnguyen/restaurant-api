# Quản Lý Đơn Hàng (Order Service)

## Tổng Quan

Service Quản lý đơn hàng xử lý tất cả các khía cạnh của quy trình đặt món trong hệ thống nhà hàng. Service này quản lý việc tạo đơn hàng, chỉnh sửa, cập nhật trạng thái và quản lý các món trong đơn.

## URL Cơ Sở

```
http://localhost:8004
```

## Tài Liệu API
- [Swagger UI](http://localhost:8004/docs)
- [OpenAPI JSON](http://localhost:8004/openapi.json)

## Các Endpoint API

### Kiểm Tra Sức Khỏe

```http
GET /health
```

Kiểm tra trạng thái hoạt động của service và kết nối database.

### Tạo Đơn Hàng

```http
POST /orders
```

Tạo đơn hàng mới với các món ăn.

**Request Body:**
```json
{
    "table_id": 1,
    "items": [
        {
            "item_id": 1,
            "quantity": 2,
            "note": "Thêm ớt"
        }
    ],
    "user_id": 1
}
```

### Lấy Danh Sách Đơn Hàng

```http
GET /orders
```

Lấy danh sách đơn hàng với các bộ lọc tùy chọn.

**Tham Số Query:**
- `table_id` (tùy chọn): Lọc theo bàn
- `status` (tùy chọn): Lọc theo trạng thái
- `from_date` (tùy chọn): Lọc theo ngày bắt đầu
- `to_date` (tùy chọn): Lọc theo ngày kết thúc

### Xem Chi Tiết Đơn Hàng

```http
GET /orders/{order_id}
```

Xem thông tin chi tiết của một đơn hàng cụ thể.

### Cập Nhật Trạng Thái Đơn Hàng

```http
PUT /orders/{order_id}/status
```

Cập nhật trạng thái của đơn hàng.

**Request Body:**
```json
{
    "status": "preparing"
}
```

**Các Trạng Thái Hợp Lệ:**
```
chờ xử lý (pending) -> đang chuẩn bị (preparing) -> sẵn sàng (ready) -> hoàn thành (completed)
                   \-> đã hủy (cancelled)
```

### Điều Chỉnh Đơn Hàng

```http
PUT /orders/{order_id}/adjust
```

Chỉnh sửa món trong đơn hàng hiện có.

**Request Body:**
```json
[
    {
        "item_id": 1,
        "quantity": 3,
        "action": "modify",
        "note": "Ít cay"
    }
]
```

### Xóa Món Khỏi Đơn Hàng

```http
DELETE /orders/{order_id}/items/{item_id}
```

Xóa một món cụ thể khỏi đơn hàng.

## Luồng Trạng Thái Đơn Hàng

```mermaid
stateDiagram-v2
    [*] --> pending: Tạo đơn
    pending --> preparing: Bắt đầu chuẩn bị
    pending --> cancelled: Hủy đơn
    preparing --> ready: Món ăn sẵn sàng
    preparing --> cancelled: Hủy đơn
    ready --> completed: Hoàn thành
    ready --> cancelled: Hủy đơn
    completed --> [*]
    cancelled --> [*]

    state pending {
        description: Chờ xử lý
    }
    state preparing {
        description: Đang chuẩn bị
    }
    state ready {
        description: Sẵn sàng
    }
    state completed {
        description: Hoàn thành
    }
    state cancelled {
        description: Đã hủy
    }
```

## Mã Lỗi

| Mã Lỗi | Mô Tả |
|-------------|-------------|
| 400 | Yêu cầu không hợp lệ - Dữ liệu đầu vào sai |
| 404 | Không tìm thấy - Đơn hàng/Món không tồn tại |
| 500 | Lỗi hệ thống |
