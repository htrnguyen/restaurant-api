-- Xóa các bảng nếu tồn tại
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS menu_items CASCADE;
DROP TABLE IF EXISTS tables CASCADE;

-- Tạo bảng `tables`
CREATE TABLE tables (
    id SERIAL PRIMARY KEY,
    status VARCHAR(50) NOT NULL
);

-- Tạo bảng `menu_items`
CREATE TABLE menu_items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    available BOOLEAN DEFAULT TRUE
);

-- Tạo bảng `orders`
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    table_id INT NOT NULL REFERENCES tables(id),
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tạo bảng `order_items`
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(id),
    menu_item_id INT NOT NULL REFERENCES menu_items(id),
    quantity INT NOT NULL,
    special_request TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'waiting'
);

-- Thêm dữ liệu mẫu vào bảng `tables`
INSERT INTO tables (status) VALUES
('còn trống'),
('đang sử dụng'),
('đã đặt trước');

-- Thêm dữ liệu mẫu vào bảng `menu_items`
INSERT INTO menu_items (name, price, available) VALUES
('Bánh mì', 15.00, TRUE),
('Phở bò', 40.00, TRUE),
('Cơm tấm', 35.00, TRUE);

-- Thêm dữ liệu mẫu vào bảng `orders`
INSERT INTO orders (table_id, created_by) VALUES
(1, 'Nguyễn Văn A'),
(2, 'Trần Thị B');

-- Thêm dữ liệu mẫu vào bảng `order_items`
INSERT INTO order_items (order_id, menu_item_id, quantity, special_request, status) VALUES
(1, 1, 2, 'Thêm pate', 'waiting'),
(1, 2, 1, NULL, 'cooking'),
(2, 3, 3, 'Không hành', 'waiting');