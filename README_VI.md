# Hướng dẫn Kiểm thử API Nhà hàng

## Chuẩn bị

1. Đảm bảo đã cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

2. Khởi tạo cơ sở dữ liệu và dữ liệu mẫu:

```bash
python init_db.py
```

3. Khởi động tất cả các service:

```bash
python run_services.py
```

## Chạy Kiểm thử

Để chạy toàn bộ bộ kiểm thử bằng tiếng Việt:

```bash
python test_api_vi.py
```

## Các kịch bản kiểm thử

Script sẽ thực hiện kiểm tra các chức năng sau:

1. Kiểm tra trạng thái hoạt động của tất cả các service

    - Health check
    - Kết nối database

2. Kiểm tra chức năng đăng nhập

    - Đăng nhập với tài khoản admin mặc định

3. Kiểm tra quản lý bàn

    - Lấy danh sách bàn
    - Xem thông tin chi tiết bàn

4. Kiểm tra quản lý thực đơn

    - Lấy danh sách danh mục
    - Lấy danh sách món ăn
    - Lấy món ăn theo danh mục

5. Kiểm tra quy trình đặt món hoàn chỉnh

    - Tạo đơn hàng mới
    - Kiểm tra đơn hàng trong bếp
    - Cập nhật trạng thái món ăn
    - Thanh toán

6. Kiểm tra báo cáo doanh thu
    - Xem báo cáo doanh thu theo ngày

## Kết quả kiểm thử

Kết quả sẽ được hiển thị trực tiếp trong terminal với các chỉ báo:

-   ✅ : Kiểm thử thành công
-   ❌ : Kiểm thử thất bại

Mỗi bước kiểm thử sẽ hiển thị kết quả chi tiết dưới dạng JSON để dễ dàng kiểm tra.
