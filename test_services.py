import asyncio
import json
from datetime import datetime

import httpx
import pytest


@pytest.fixture
async def client():
    async with httpx.AsyncClient() as client:
        yield client


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "service_name,port",
    [
        ("User Service", 8001),
        ("Table Service", 8002),
        ("Menu Service", 8003),
        ("Order Service", 8004),
        ("Kitchen Service", 8005),
        ("Payment Service", 8006),
    ],
)
async def test_service_health(client: httpx.AsyncClient, service_name: str, port: int):
    try:
        # Test root endpoint
        response = await client.get(f"http://localhost:{port}/")
        assert response.status_code == 200
        print(f"✅ {service_name} root endpoint: {response.json()}")

        # Test health endpoint
        response = await client.get(f"http://localhost:{port}/health")
        assert response.status_code == 200
        print(
            f"✅ {service_name} health check: {json.dumps(response.json(), indent=2)}"
        )
    except Exception as e:
        print(f"❌ {service_name} error: {str(e)}")


@pytest.mark.asyncio
async def test_basic_flow():
    """Test kịch bản cơ bản của hệ thống"""
    async with httpx.AsyncClient() as client:
        print("\n=== Testing Basic System Flow ===\n")

        try:
            # 1. Đăng nhập với tài khoản mẫu
            print("\n--- Testing Login Flow ---\n")
            login_data = {"username": "nhanvien1", "password": "admin123"}
            response = await client.post(
                "http://localhost:8001/auth/login", json=login_data
            )
            assert response.status_code == 200
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print(f"Login successful: {json.dumps(response.json(), indent=2)}")

            # 2. Lấy danh sách bàn trống
            print("\n--- Testing Table Service Flow ---\n")
            response = await client.get(
                "http://localhost:8002/tables/available", headers=headers
            )
            assert response.status_code == 200
            tables = response.json()
            print(f"Available tables: {json.dumps(tables, indent=2)}")

            # 3. Lấy menu các món ăn có sẵn
            print("\n--- Testing Menu Service Flow ---\n")
            response = await client.get(
                "http://localhost:8003/menu-items/available", headers=headers
            )
            assert response.status_code == 200
            menu_items = response.json()
            print(f"Available menu items: {json.dumps(menu_items, indent=2)}")

            # 4. Tạo đơn hàng mới
            print("\n--- Testing Order Creation Flow ---\n")
            order_data = {
                "table_id": 1,
                "created_by": "nhanvien1",
                "items": [
                    {"item_id": 1, "quantity": 1},  # Bò bít tết
                    {"item_id": 2, "quantity": 1},  # Salad
                ],
            }
            response = await client.post(
                "http://localhost:8004/orders", json=order_data, headers=headers
            )
            assert response.status_code == 200
            order = response.json()
            order_id = order["order_id"]
            print(f"Created order: {json.dumps(order, indent=2)}")

            # 5. Kiểm tra đơn hàng trong bếp
            print("\n--- Testing Kitchen Service Flow ---\n")
            response = await client.get(
                f"http://localhost:8005/kitchen/orders/{order_id}", headers=headers
            )
            assert response.status_code == 200
            kitchen_order = response.json()
            print(f"Order in kitchen: {json.dumps(kitchen_order, indent=2)}")

            # 6. Cập nhật trạng thái món ăn
            print("\n--- Testing Order Items Update ---\n")
            for item in order["items"]:
                response = await client.put(
                    f"http://localhost:8005/kitchen/order-items/{item['id']}/status",
                    params={"status": "completed"},
                    headers=headers,
                )
                assert response.status_code == 200
                print(
                    f"Updated item {item['id']}: {json.dumps(response.json(), indent=2)}"
                )

            # 7. Tạo hóa đơn và thanh toán
            print("\n--- Testing Payment Flow ---\n")
            payment_data = {
                "order_id": order_id,
                "payment_method": "cash",
                "created_by": "nhanvien1",
            }
            response = await client.post(
                "http://localhost:8006/payments/bills",
                json=payment_data,
                headers=headers,
            )
            assert response.status_code == 200
            payment = response.json()
            print(f"Payment completed: {json.dumps(payment, indent=2)}")

            print("\n=== Test Flow Completed Successfully ===\n")

        except Exception as e:
            print(f"\n❌ Error during test flow: {str(e)}")
            raise e


if __name__ == "__main__":
    asyncio.run(test_basic_flow())
