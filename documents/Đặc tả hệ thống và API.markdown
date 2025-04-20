Dựa trên yêu cầu tập trung vào hệ thống trực tiếp (phục vụ tại nhà hàng, không bao gồm các chức năng trực tuyến), tôi sẽ chốt lại đặc tả hệ thống và danh sách API cần thiết cho hệ thống quản lý đơn hàng thực khách theo kiến trúc microservice với FastAPI. Đặc tả sẽ tập trung vào các chức năng phục vụ tại nhà hàng, loại bỏ các tính năng liên quan đến đặt hàng trực tuyến hoặc các chức năng không cần thiết.

---

### **Đặc tả hệ thống**

#### **1. Mục tiêu**
Hệ thống quản lý đơn hàng thực khách nhằm tự động hóa quy trình phục vụ tại nhà hàng, giúp thực khách, nhân viên phục vụ, nhân viên bếp và quản lý tương tác hiệu quả, giảm sai sót và cải thiện trải nghiệm dùng bữa. Hệ thống tập trung vào việc gọi món trực tiếp tại bàn, quản lý đơn hàng, chế biến món, và xử lý thanh toán.

#### **2. Lợi ích dự kiến**
- **Đối với thực khách**: Chủ động gọi món qua tablet tại bàn, kiểm soát món đã gọi và hóa đơn.
- **Đối với nhân viên phục vụ**: Giảm thao tác thủ công, đảm bảo đơn hàng chính xác.
- **Đối với nhân viên bếp**: Kiểm soát món ăn, nguyên liệu, và tiến trình chế biến.
- **Đối với quản lý**: Giám sát hoạt động, tổng hợp doanh thu, và xem lịch sử thanh toán.

#### **3. Đối tượng sử dụng hệ thống**
- **Thực khách**: Gọi món qua tablet tại bàn, xem menu, yêu cầu thanh toán.
- **Nhân viên phục vụ**: Mở/đóng bàn, hỗ trợ gọi món, xác nhận thanh toán.
- **Nhân viên bếp**: Tiếp nhận đơn, chế biến món, kiểm soát nguyên liệu.
- **Quản lý**: Giám sát, tổng hợp doanh thu, xem lịch sử thanh toán.

#### **4. Phạm vi dự án**
- Hệ thống phục vụ trực tiếp tại nhà hàng, không hỗ trợ đặt hàng trực tuyến.
- Hệ thống hoạt động độc lập, tập trung vào quy trình gọi món, chế biến và thanh toán tại chỗ.
- Hỗ trợ các loại menu à-la-carte hoặc buffet.

#### **5. Chức năng cốt lõi**
- **Quản lý bàn ăn**: Mở/đóng bàn, theo dõi trạng thái bàn (trống, đang phục vụ).
- **Gọi món tại bàn**: Thực khách đặt món qua tablet, nhân viên phục vụ hỗ trợ.
- **Quản lý thực đơn**: Kiểm tra trạng thái món ăn, cập nhật thông tin món.
- **Chế biến món ăn**: Tiếp nhận đơn, chuẩn bị món, đánh dấu hoàn thành.
- **Quản lý nguyên liệu**: Theo dõi tồn kho, thông báo hết nguyên liệu, tắt món nếu cần.
- **Thanh toán tại bàn**: Tính toán hóa đơn, hỗ trợ thanh toán (tiền mặt, quét mã).
- **Báo cáo**: Tổng hợp doanh thu, xem lịch sử thanh toán theo thời gian.

---

### **Đặc tả dữ liệu hệ thống (ERD)**

#### **Thực thể**
- **Table (Bàn ăn)**:
  - `id` (integer, PK)
  - `number` (integer)
  - `status` (ENUM: 'available', 'occupied')

- **Opening_Table (Mở bàn)**:
  - `table_id` (integer, FK)
  - `user_id` (integer, FK)
  - `time` (datetime)

- **Closing_Table (Đóng bàn)**:
  - `table_id` (integer, FK)
  - `user_id` (integer, FK)
  - `time` (datetime)

- **User (Người dùng)**:
  - `id` (integer, PK)
  - `full_name` (varchar)
  - `username` (varchar)
  - `password` (varchar)
  - `status` (varchar)
  - `role_id` (integer, FK)
  - `shift_id` (integer, FK)

- **Role (Vai trò)**:
  - `id` (integer, PK)
  - `name` (varchar)

- **Shift (Ca làm việc)**:
  - `id` (integer, PK)
  - `startedTime` (datetime)
  - `endedTime` (datetime)

- **Menu_Category (Danh mục thực đơn)**:
  - `id` (integer, PK)
  - `name` (varchar)

- **Menu_Item (Món ăn)**:
  - `id` (integer, PK)
  - `name` (varchar)
  - `description` (text)
  - `price` (decimal(10,2))
  - `status` (ENUM: 'available', 'unavailable')
  - `img_url` (varchar)
  - `category_id` (integer, FK)

- **Ingredient (Nguyên liệu)**:
  - `id` (integer, PK)
  - `name` (varchar)
  - `quantity` (integer)
  - `UOM` (varchar)

- **Item_Ingredient (Nguyên liệu món ăn)**:
  - `item_id` (integer, FK)
  - `ingredient_id` (integer, FK)
  - `quantity` (float)

- **Order (Đơn hàng)**:
  - `id` (integer, PK)
  - `status` (ENUM: 'pending', 'processing', 'completed', 'canceled')
  - `total_amount` (decimal(10,2))
  - `created_at` (datetime)
  - `updated_at` (datetime)
  - `creating_user_id` (integer, FK)
  - `table_id` (integer, FK)

- **Order_Status_History (Lịch sử trạng thái đơn hàng)**:
  - `id` (integer, PK)
  - `order_id` (integer, FK)
  - `old_status` (varchar)
  - `new_status` (varchar)
  - `changed_at` (datetime)
  - `changed_by` (integer, FK)

- **Order_Item (Chi tiết đơn hàng)**:
  - `id` (integer, PK)
  - `quantity` (integer)
  - `note` (text)
  - `status` (ENUM: 'pending', 'processing', 'completed', 'canceled')
  - `created_at` (datetime)
  - `updated_at` (datetime)
  - `order_id` (integer, FK)
  - `item_id` (integer, FK)
  - `observation_cooking_user_id` (integer, FK)
  - `price` (decimal(10,2))

- **Order_Item_Status_History (Lịch sử trạng thái món ăn)**:
  - `id` (integer, PK)
  - `order_item_id` (integer, FK)
  - `old_status` (varchar)
  - `new_status` (varchar)
  - `changed_at` (datetime)
  - `changed_by` (integer, FK)

- **Bill (Hóa đơn)**:
  - `id` (integer, PK)
  - `created_at` (datetime)
  - `total_amount` (decimal(10,2))
  - `payment_method` (varchar)
  - `order_id` (integer, FK)
  - `created_by` (integer, FK)

#### **Mối quan hệ**
- `Table` **has** `Opening_Table`, `Closing_Table`, `Order`.
- `User` **has** `Opening_Table`, `Closing_Table`, `Order`, `Order_Item`, `Bill`.
- `User` **has** `Shift`.
- `Role` **has** `User`.
- `Menu_Category` **has** `Menu_Item`.
- `Menu_Item` **has** `Order_Item`, `Item_Ingredient`.
- `Ingredient` **has** `Item_Ingredient`.
- `Order` **has** `Order_Status_History`, `Bill`.
- `Order` **contains** `Order_Item`.
- `Order_Item` **has** `Order_Item_Status_History`.

---

### **Danh sách API cần thiết (Microservice với FastAPI)**

Hệ thống được thiết kế theo kiến trúc microservice, tập trung vào các chức năng phục vụ trực tiếp tại nhà hàng, bao gồm 6 dịch vụ con:

#### **1. Dịch vụ Quản lý Người dùng (User Service)**
- **POST /users/login**  
  - Mô tả: Đăng nhập người dùng.  
  - Input: `username` (string), `password` (string).  
  - Output: `token` (JWT), `user_id` (int), `role` (string).  

- **GET /users/{user_id}/permissions**  
  - Mô tả: Lấy danh sách quyền của người dùng.  
  - Input: `user_id` (path parameter).  
  - Output: Danh sách quyền (`permissions`: array of strings).  

#### **2. Dịch vụ Quản lý Bàn ăn (Table Service)**
- **POST /tables/open**  
  - Mô tả: Mở bàn để phục vụ khách.  
  - Input: `table_id`, `user_id`, `open_time`.  
  - Output: `status`, `message`.  

- **POST /tables/close**  
  - Mô tả: Đóng bàn sau khi khách rời đi.  
  - Input: `table_id`, `user_id`, `close_time`.  
  - Output: `status`, `message`.  

- **GET /tables/status**  
  - Mô tả: Xem trạng thái của tất cả các bàn.  
  - Output: Danh sách bàn (`tables`: array of objects).  

#### **3. Dịch vụ Quản lý Menu và Món ăn (Menu Service)**
- **GET /menu**  
  - Mô tả: Lấy danh sách món ăn để hiển thị trên tablet.  
  - Output: Danh sách món (`items`: array of objects).  

- **PUT /menu/items/{item_id}**  
  - Mô tả: Cập nhật trạng thái món ăn (tắt/bật món).  
  - Input: `item_id` (path parameter), `status` ("available", "unavailable").  
  - Output: `message`.  

#### **4. Dịch vụ Quản lý Đơn hàng (Order Service)**
- **POST /orders**  
  - Mô tả: Tạo đơn hàng mới (do nhân viên phục vụ hoặc khách hàng qua tablet).  
  - Input: `table_id`, `user_id`, `items` (array: `item_id`, `quantity`).  
  - Output: `order_id`, `total_amount`, `status`.  

- **PUT /orders/{order_id}/adjust**  
  - Mô tả: Điều chỉnh đơn hàng (thêm, sửa, xóa món).  
  - Input: `order_id` (path parameter), `items` (array: `item_id`, `quantity`, `action`).  
  - Output: `order_id`, `updated_items`, `message`.  

- **DELETE /orders/{order_id}/items/{item_id}**  
  - Mô tả: Hủy món trong đơn hàng.  
  - Input: `order_id`, `item_id` (path parameters).  
  - Output: `message`.  

- **GET /orders/{order_id}**  
  - Mô tả: Xem chi tiết đơn hàng.  
  - Input: `order_id` (path parameter).  
  - Output: Thông tin đơn hàng (`order_id`, `table_id`, `items`, `total_amount`, `status`).  

#### **5. Dịch vụ Quản lý Chế biến (Kitchen Service)**
- **GET /kitchen/orders/pending**  
  - Mô tả: Lấy danh sách đơn hàng chờ xử lý.  
  - Output: Danh sách đơn hàng (`orders`: array of objects).  

- **PUT /kitchen/orders/{order_id}/items/{item_id}/status**  
  - Mô tả: Cập nhật trạng thái chế biến của món ăn.  
  - Input: `order_id`, `item_id` (path parameters), `status` ("pending", "in_progress", "completed").  
  - Output: `order_id`, `item_id`, `status`, `message`.  

- **POST /ingredients/check**  
  - Mô tả: Kiểm tra nguyên liệu cho món ăn.  
  - Input: `item_id`.  
  - Output: `ingredient_status` ("available", "unavailable"), `remaining_quantity`.  

#### **6. Dịch vụ Quản lý Thanh toán và Báo cáo (Payment Service)**
- **POST /payments/bill**  
  - Mô tả: Tạo hóa đơn cho đơn hàng.  
  - Input: `order_id`, `payment_method`, `created_by_user_id`.  
  - Output: `bill_id`, `total_amount`, `status`.  

- **GET /payments/bills/{bill_id}**  
  - Mô tả: Xem chi tiết hóa đơn.  
  - Input: `bill_id` (path parameter).  
  - Output: Thông tin hóa đơn (`bill_id`, `order_id`, `total_amount`, `payment_method`, `bill_time`).  

- **GET /payments/history**  
  - Mô tả: Xem lịch sử hóa đơn.  
  - Input: `start_date`, `end_date` (query parameters).  
  - Output: Danh sách hóa đơn (`bills`: array of objects).  

- **GET /reports/revenue/summary**  
  - Mô tả: Tổng hợp doanh thu trong khoảng thời gian.  
  - Input: `start_date`, `end_date` (query parameters).  
  - Output: `total_revenue`, `details` (array of objects).  

---

### **Quy trình nghiệp vụ chính**

#### **1. Quy trình phục vụ khách hàng**
1. Nhân viên phục vụ mở bàn khi khách đến
2. Khách hàng xem menu và gọi món qua tablet
3. Đơn hàng được gửi đến bếp
4. Bếp chế biến và cập nhật trạng thái món ăn
5. Nhân viên phục vụ mang món ăn ra bàn
6. Khách yêu cầu thanh toán
7. Nhân viên tạo hóa đơn và xử lý thanh toán
8. Nhân viên đóng bàn sau khi khách rời đi

#### **2. Quy trình quản lý bếp**
1. Bếp nhận đơn hàng mới
2. Kiểm tra nguyên liệu cho món ăn
3. Cập nhật trạng thái món ăn (đang chế biến)
4. Hoàn thành món ăn và cập nhật trạng thái
5. Thông báo cho nhân viên phục vụ mang món ra

#### **3. Quy trình quản lý kho**
1. Kiểm tra tồn kho nguyên liệu định kỳ
2. Cập nhật số lượng nguyên liệu khi nhập hàng
3. Hệ thống tự động giảm số lượng khi món được chế biến
4. Cảnh báo khi nguyên liệu sắp hết
5. Tắt món khi hết nguyên liệu

### **Yêu cầu phi chức năng**

#### **1. Hiệu suất**
- Thời gian phản hồi API < 500ms
- Hỗ trợ đồng thời ít nhất 50 người dùng
- Xử lý tối thiểu 100 đơn hàng/giờ

#### **2. Bảo mật**
- Xác thực người dùng bằng JWT
- Mã hóa mật khẩu với bcrypt
- Phân quyền chi tiết theo vai trò
- Lưu trữ token an toàn

#### **3. Khả năng mở rộng**
- Kiến trúc microservice cho phép mở rộng từng dịch vụ độc lập
- Hỗ trợ thêm nhiều nhà hàng trong tương lai
- Dễ dàng thêm tính năng mới

#### **4. Độ tin cậy**
- Uptime > 99.9%
- Sao lưu dữ liệu hàng ngày
- Cơ chế khôi phục khi gặp sự cố

### **Kế hoạch triển khai**

#### **Giai đoạn 1: Phát triển cơ bản**
- Xây dựng database và models
- Phát triển các API cơ bản
- Tích hợp xác thực và phân quyền

#### **Giai đoạn 2: Phát triển giao diện**
- Xây dựng giao diện tablet cho khách hàng
- Xây dựng giao diện cho nhân viên phục vụ
- Xây dựng giao diện cho bếp

#### **Giai đoạn 3: Tích hợp và kiểm thử**
- Tích hợp các dịch vụ
- Kiểm thử toàn diện
- Tối ưu hiệu suất

#### **Giai đoạn 4: Triển khai và đào tạo**
- Triển khai hệ thống
- Đào tạo nhân viên
- Theo dõi và hỗ trợ

---

### **Kết luận**
Đặc tả hệ thống và danh sách API đã được chốt lại, tập trung vào các chức năng phục vụ trực tiếp tại nhà hàng. Hệ thống được thiết kế theo kiến trúc microservice với 6 dịch vụ con, sử dụng FastAPI, đảm bảo tính độc lập và hiệu quả trong quản lý đơn hàng thực khách. Các API hỗ trợ đầy đủ quy trình từ mở bàn, gọi món, chế biến, đến thanh toán và báo cáo. Nếu bạn cần thêm thông tin, hãy cho tôi biết!