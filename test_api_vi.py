import asyncio
import json
import logging
from datetime import datetime

import httpx

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_user_crud():
    """Test CRUD operations cho người dùng"""
    print("\n=== Test CRUD người dùng ===")
    async with httpx.AsyncClient() as client:
        # Login trước để lấy token
        login_data = {"username": "admin", "password": "test123"}
        response = await client.post(
            "http://localhost:8001/users/login", json=login_data
        )
        if response.status_code == 200:
            user_data = response.json()
            # Không có access_token trong response, tạm thời bỏ qua auth header
            headers = {}
        else:
            print(f"[LOGIN] Lỗi đăng nhập: {json.dumps(response.json(), indent=2)}")
            return

        # Tạo người dùng mới
        user_data = {
            "username": "test_user",
            "password": "test123",
            "role": "staff",
            "full_name": "Nhân viên test",
            "status": "active",
        }
        response = await client.post(
            "http://localhost:8001/users", json=user_data, headers=headers
        )
        logger.info(
            f'HTTP Request: POST http://localhost:8001/users "{response.status_code} {response.reason_phrase}"'
        )
        print(f"[POST] Tạo người dùng: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            user_id = response.json().get("id")
            # Lấy thông tin người dùng
            response = await client.get(
                f"http://localhost:8001/users/{user_id}", headers=headers
            )
            logger.info(
                f'HTTP Request: GET http://localhost:8001/users/{user_id} "{response.status_code} {response.reason_phrase}"'
            )
            print(
                f"[GET] Thông tin người dùng: {json.dumps(response.json(), indent=2)}"
            )

            # Cập nhật người dùng
            update_data = {"full_name": "Nhân viên test đã cập nhật"}
            response = await client.put(
                f"http://localhost:8001/users/{user_id}",
                json=update_data,
                headers=headers,
            )
            logger.info(
                f'HTTP Request: PUT http://localhost:8001/users/{user_id} "{response.status_code} {response.reason_phrase}"'
            )
            print(f"[PUT] Cập nhật người dùng: {json.dumps(response.json(), indent=2)}")

            # Xóa người dùng
            response = await client.delete(
                f"http://localhost:8001/users/{user_id}", headers=headers
            )
            logger.info(
                f'HTTP Request: DELETE http://localhost:8001/users/{user_id} "{response.status_code} {response.reason_phrase}"'
            )
            print(f"[DELETE] Xóa người dùng: {json.dumps(response.json(), indent=2)}")


async def test_menu_crud():
    """Test CRUD operations cho món ăn"""
    print("\n=== Test CRUD món ăn ===")
    async with httpx.AsyncClient() as client:
        # Login để lấy token
        login_data = {"username": "admin", "password": "test123"}
        response = await client.post(
            "http://localhost:8001/users/login", json=login_data
        )
        if response.status_code == 200:
            user_data = response.json()
            # Không có access_token trong response, tạm thời bỏ qua auth header
            headers = {}
        else:
            print(f"[LOGIN] Lỗi đăng nhập: {json.dumps(response.json(), indent=2)}")
            return

        # Tạo món ăn mới
        menu_data = {
            "name": "Món ăn test",
            "description": "Món ăn để kiểm thử",
            "price": 150000,
            "category_id": 1,
            "status": "available",
        }
        response = await client.post(
            "http://localhost:8003/menu-items", json=menu_data, headers=headers
        )
        logger.info(
            f'HTTP Request: POST http://localhost:8003/menu-items "{response.status_code} {response.reason_phrase}"'
        )
        print(f"[POST] Tạo món ăn: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            item_id = response.json().get("id")
            # Lấy thông tin món ăn
            response = await client.get(
                f"http://localhost:8003/menu-items/{item_id}", headers=headers
            )
            logger.info(
                f'HTTP Request: GET http://localhost:8003/menu-items/{item_id} "{response.status_code} {response.reason_phrase}"'
            )
            print(f"[GET] Thông tin món ăn: {json.dumps(response.json(), indent=2)}")

            # Cập nhật món ăn
            update_data = {"price": 180000}
            response = await client.put(
                f"http://localhost:8003/menu-items/{item_id}",
                json=update_data,
                headers=headers,
            )
            logger.info(
                f'HTTP Request: PUT http://localhost:8003/menu-items/{item_id} "{response.status_code} {response.reason_phrase}"'
            )
            print(f"[PUT] Cập nhật món ăn: {json.dumps(response.json(), indent=2)}")

            # Xóa món ăn
            response = await client.delete(
                f"http://localhost:8003/menu-items/{item_id}", headers=headers
            )
            logger.info(
                f'HTTP Request: DELETE http://localhost:8003/menu-items/{item_id} "{response.status_code} {response.reason_phrase}"'
            )
            print(f"[DELETE] Xóa món ăn: {json.dumps(response.json(), indent=2)}")


async def test_table_crud():
    """Test CRUD operations cho bàn"""
    print("\n=== Test CRUD bàn ăn ===")
    async with httpx.AsyncClient() as client:
        # Login để lấy token
        login_data = {"username": "admin", "password": "test123"}
        response = await client.post(
            "http://localhost:8001/users/login", json=login_data
        )
        if response.status_code == 200:
            user_data = response.json()
            # Không có access_token trong response, tạm thời bỏ qua auth header
            headers = {}
        else:
            print(f"[LOGIN] Lỗi đăng nhập: {json.dumps(response.json(), indent=2)}")
            return

        # Tạo bàn mới
        table_data = {
            "number": 5,  # Số bàn mới vì đã có 4 bàn trong dữ liệu mẫu
            "status": "available",
        }
        response = await client.post(
            "http://localhost:8002/tables", json=table_data, headers=headers
        )
        logger.info(
            f'HTTP Request: POST http://localhost:8002/tables "{response.status_code} {response.reason_phrase}"'
        )
        print(f"[POST] Tạo bàn: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            table_id = response.json().get("id")
            # Lấy thông tin bàn
            response = await client.get(
                f"http://localhost:8002/tables/{table_id}", headers=headers
            )
            logger.info(
                f'HTTP Request: GET http://localhost:8002/tables/{table_id} "{response.status_code} {response.reason_phrase}"'
            )
            print(f"[GET] Thông tin bàn: {json.dumps(response.json(), indent=2)}")

            # Cập nhật trạng thái bàn
            update_data = {"status": "occupied"}
            response = await client.put(
                f"http://localhost:8002/tables/{table_id}",
                json=update_data,
                headers=headers,
            )
            logger.info(
                f'HTTP Request: PUT http://localhost:8002/tables/{table_id} "{response.status_code} {response.reason_phrase}"'
            )
            print(f"[PUT] Cập nhật bàn: {json.dumps(response.json(), indent=2)}")

            # Xóa bàn
            response = await client.delete(
                f"http://localhost:8002/tables/{table_id}", headers=headers
            )
            logger.info(
                f'HTTP Request: DELETE http://localhost:8002/tables/{table_id} "{response.status_code} {response.reason_phrase}"'
            )
            print(f"[DELETE] Xóa bàn: {json.dumps(response.json(), indent=2)}")


async def test_kitchen_ingredients():
    """Test operations cho nguyên liệu"""
    print("\n=== Test quản lý nguyên liệu ===")
    async with httpx.AsyncClient() as client:
        # Login để lấy token
        login_data = {"username": "admin", "password": "test123"}
        response = await client.post(
            "http://localhost:8001/users/login", json=login_data
        )
        if response.status_code == 200:
            user_data = response.json()
            headers = {}
        else:
            print(f"[LOGIN] Lỗi đăng nhập: {json.dumps(response.json(), indent=2)}")
            return

        # Tạo nguyên liệu mới
        ingredient_data = {
            "name": "Gia vị test",
            "quantity": 10,
            "unit": "kg",
            "uom": "kg",  # Thêm trường uom
        }
        response = await client.post(
            "http://localhost:8005/kitchen/ingredients",
            json=ingredient_data,
            headers=headers,
        )
        logger.info(
            f'HTTP Request: POST http://localhost:8005/kitchen/ingredients "{response.status_code} {response.reason_phrase}"'
        )
        print(f"[POST] Tạo nguyên liệu: {json.dumps(response.json(), indent=2)}")

        # Lấy danh sách nguyên liệu
        response = await client.get(
            "http://localhost:8005/kitchen/ingredients", headers=headers
        )
        logger.info(
            f'HTTP Request: GET http://localhost:8005/kitchen/ingredients "{response.status_code} {response.reason_phrase}"'
        )
        print(f"[GET] Danh sách nguyên liệu: {json.dumps(response.json(), indent=2)}")

        # Cập nhật số lượng nguyên liệu "Thịt bò"
        update_data = {"quantity": 120}
        response = await client.put(
            "http://localhost:8005/kitchen/ingredients/1",
            json=update_data,
            headers=headers,
        )
        logger.info(
            f'HTTP Request: PUT http://localhost:8005/kitchen/ingredients/1 "{response.status_code} {response.reason_phrase}"'
        )
        print(f"[PUT] Cập nhật nguyên liệu: {json.dumps(response.json(), indent=2)}")


async def test_order_flow():
    """Test quy trình đặt món"""
    print("\n=== Test quy trình đặt món ===")
    async with httpx.AsyncClient() as client:
        # Login để lấy token
        login_data = {"username": "nhanvien1", "password": "test123"}
        response = await client.post(
            "http://localhost:8001/users/login", json=login_data
        )
        if response.status_code == 200:
            user_data = response.json()
            user_id = user_data.get("id")  # Get user ID from login response
            headers = {}
        else:
            print(f"[LOGIN] Lỗi đăng nhập: {json.dumps(response.json(), indent=2)}")
            return

        # Tạo đơn hàng mới
        order_data = {
            "table_id": 1,
            "items": [
                {"item_id": 1, "quantity": 1},  # Bò bít tết
                {"item_id": 2, "quantity": 1},  # Salad
            ],
            "user_id": user_id,
        }
        response = await client.post(
            "http://localhost:8004/orders", json=order_data, headers=headers
        )
        logger.info(
            f'HTTP Request: POST http://localhost:8004/orders "{response.status_code} {response.reason_phrase}"'
        )
        print(f"[POST] Tạo đơn hàng: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            order_id = response.json()["order_id"]

            # Lấy thông tin đơn hàng
            response = await client.get(
                f"http://localhost:8004/orders/{order_id}", headers=headers
            )
            logger.info(
                f'HTTP Request: GET http://localhost:8004/orders/{order_id} "{response.status_code} {response.reason_phrase}"'
            )
            print(f"[GET] Thông tin đơn hàng: {json.dumps(response.json(), indent=2)}")

            # Cập nhật trạng thái đơn hàng sang preparing
            update_data = {"status": "preparing"}
            response = await client.put(
                f"http://localhost:8004/orders/{order_id}/status",
                json=update_data,
                headers=headers,
            )
            logger.info(
                f'HTTP Request: PUT http://localhost:8004/orders/{order_id}/status "{response.status_code} {response.reason_phrase}"'
            )
            print(
                f"[PUT] Cập nhật trạng thái đơn hàng: {json.dumps(response.json(), indent=2)}"
            )

            # Cập nhật món ăn đã hoàn thành
            for item in order_data["items"]:
                response = await client.put(
                    f"http://localhost:8005/kitchen/order-items/{item['item_id']}/status",
                    params={"status": "completed"},
                    headers=headers,
                )
                logger.info(
                    f'HTTP Request: PUT http://localhost:8005/kitchen/order-items/{item["item_id"]}/status "{response.status_code} {response.reason_phrase}"'
                )
                print(
                    f"[PUT] Cập nhật trạng thái món: {json.dumps(response.json(), indent=2)}"
                )

            # Tạo hóa đơn
            bill_data = {
                "order_id": order_id,
                "payment_method": "cash",
                "created_by": user_id,  # Use created_by instead of user_id
            }
            response = await client.post(
                "http://localhost:8006/payments/bills", json=bill_data, headers=headers
            )
            logger.info(
                f'HTTP Request: POST http://localhost:8006/payments/bills "{response.status_code} {response.reason_phrase}"'
            )
            print(f"[POST] Tạo hóa đơn: {json.dumps(response.json(), indent=2)}")


async def test_reports():
    """Test API báo cáo"""
    print("\n=== Test API báo cáo ===")
    async with httpx.AsyncClient() as client:
        # Login để lấy token
        login_data = {"username": "admin", "password": "test123"}
        response = await client.post(
            "http://localhost:8001/users/login", json=login_data
        )
        if response.status_code == 200:
            user_data = response.json()
            # Không có access_token trong response, tạm thời bỏ qua auth header
            headers = {}
        else:
            print(f"[LOGIN] Lỗi đăng nhập: {json.dumps(response.json(), indent=2)}")
            return

        # Báo cáo doanh thu theo ngày
        today = datetime.now().strftime("%Y-%m-%d")
        response = await client.get(
            f"http://localhost:8006/payments/reports/daily?date={today}",
            headers=headers,
        )
        logger.info(
            f'HTTP Request: GET http://localhost:8006/payments/reports/daily?date={today} "{response.status_code} {response.reason_phrase}"'
        )
        print(
            f"[GET] Báo cáo doanh thu ngày {today}: {json.dumps(response.json(), indent=2)}"
        )

        # Báo cáo tồn kho
        response = await client.get(
            "http://localhost:8005/kitchen/ingredients/report", headers=headers
        )
        logger.info(
            f'HTTP Request: GET http://localhost:8005/kitchen/ingredients/report "{response.status_code} {response.reason_phrase}"'
        )
        print(f"[GET] Báo cáo tồn kho: {json.dumps(response.json(), indent=2)}")


async def main():
    """Chạy toàn bộ test case"""
    print("Bắt đầu chạy kiểm thử...\n")

    try:
        await test_user_crud()
        await test_menu_crud()
        await test_table_crud()
        await test_kitchen_ingredients()
        await test_order_flow()
        await test_reports()
    except Exception as e:
        print(f"\nLỗi trong quá trình test: {str(e)}")

    print("\n=== KẾT THÚC KIỂM THỬ ===\n")


if __name__ == "__main__":
    asyncio.run(main())
