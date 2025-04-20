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


async def test_full_order_process():
    """Test toàn bộ quy trình từ đặt món đến thanh toán"""
    print("\n=== BẮT ĐẦU QUY TRÌNH ĐẶT MÓN ===\n")

    async with httpx.AsyncClient() as client:
        try:
            # 1. Đăng nhập
            print("1. ĐĂNG NHẬP HỆ THỐNG")
            login_data = {"username": "nhanvien1", "password": "test123"}
            response = await client.post(
                "http://localhost:8001/users/login", json=login_data
            )
            print(f"Request URL: http://localhost:8001/users/login")
            print(
                f"Request data: {json.dumps(login_data, indent=2, ensure_ascii=False)}"
            )

            if response.status_code != 200:
                print(f"[ERROR] Lỗi đăng nhập - Status: {response.status_code}")
                print(
                    f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}"
                )
                return

            user_data = response.json()
            user_id = user_data.get("id")
            print(f"[SUCCESS] Đăng nhập thành công - Status: {response.status_code}")
            print(
                f"Response data: {json.dumps(user_data, indent=2, ensure_ascii=False)}"
            )
            print("-" * 100)

            # 2. Kiểm tra và mở bàn
            print("\n2. KIỂM TRA VÀ MỞ BÀN")
            table_id = 1  # Giả sử bàn số 1
            response = await client.get(f"http://localhost:8002/tables/{table_id}")
            print(f"Request URL: http://localhost:8002/tables/{table_id}")

            if response.status_code != 200:
                print(f"[ERROR] Lỗi kiểm tra bàn - Status: {response.status_code}")
                print(
                    f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}"
                )
                return

            print(f"[SUCCESS] Thông tin bàn - Status: {response.status_code}")
            print(
                f"Response data: {json.dumps(response.json(), indent=2, ensure_ascii=False)}"
            )
            print("-" * 100)

            # 3. Tạo đơn hàng
            print("\n3. TẠO ĐƠN HÀNG")
            order_data = {
                "table_id": table_id,
                "items": [
                    {"item_id": 1, "quantity": 1},  # Bò bít tết
                    {"item_id": 2, "quantity": 1},  # Salad
                ],
                "user_id": user_id,
            }

            response = await client.post(
                "http://localhost:8004/orders", json=order_data
            )
            print(f"Request URL: http://localhost:8004/orders")
            print(
                f"Request data: {json.dumps(order_data, indent=2, ensure_ascii=False)}"
            )

            if response.status_code != 200:
                print(f"[ERROR] Lỗi tạo đơn hàng - Status: {response.status_code}")
                print(
                    f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}"
                )
                return

            order_response = response.json()
            order_id = order_response["order_id"]
            print(f"[SUCCESS] Tạo đơn hàng thành công - Status: {response.status_code}")
            print(
                f"Response data: {json.dumps(order_response, indent=2, ensure_ascii=False)}"
            )
            print("-" * 100)

            # 4. Cập nhật trạng thái đơn hàng (bếp nhận đơn)
            print("\n4. BẾP NHẬN ĐƠN")
            update_data = {"status": "preparing"}
            response = await client.put(
                f"http://localhost:8004/orders/{order_id}/status", json=update_data
            )
            print(f"Request URL: http://localhost:8004/orders/{order_id}/status")
            print(
                f"Request data: {json.dumps(update_data, indent=2, ensure_ascii=False)}"
            )

            if response.status_code != 200:
                print(
                    f"[ERROR] Lỗi cập nhật trạng thái đơn - Status: {response.status_code}"
                )
                print(
                    f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}"
                )
                return

            print(f"[SUCCESS] Bếp đã nhận đơn - Status: {response.status_code}")
            print(
                f"Response data: {json.dumps(response.json(), indent=2, ensure_ascii=False)}"
            )
            print("-" * 100)

            # 5. Cập nhật từng món ăn đã hoàn thành
            print("\n5. CẬP NHẬT TRẠNG THÁI MÓN ĂN")
            for item in order_data["items"]:
                response = await client.put(
                    f"http://localhost:8005/kitchen/order-items/{item['item_id']}/status",
                    params={"status": "completed"},
                )
                print(
                    f"Request URL: http://localhost:8005/kitchen/order-items/{item['item_id']}/status?status=completed"
                )

                if response.status_code != 200:
                    print(
                        f"[ERROR] Lỗi cập nhật trạng thái món {item['item_id']} - Status: {response.status_code}"
                    )
                    print(
                        f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}"
                    )
                    continue

                print(
                    f"[SUCCESS] Đã hoàn thành món {item['item_id']} - Status: {response.status_code}"
                )
                print(
                    f"Response data: {json.dumps(response.json(), indent=2, ensure_ascii=False)}"
                )
            print("-" * 100)

            # 6. Tạo hóa đơn và thanh toán
            print("\n6. THANH TOÁN")
            bill_data = {
                "order_id": order_id,
                "payment_method": "cash",
                "created_by": user_id,
            }

            response = await client.post(
                "http://localhost:8006/payments/bills", json=bill_data
            )
            print(f"Request URL: http://localhost:8006/payments/bills")
            print(
                f"Request data: {json.dumps(bill_data, indent=2, ensure_ascii=False)}"
            )

            if response.status_code != 200:
                print(f"[ERROR] Lỗi tạo hóa đơn - Status: {response.status_code}")
                print(
                    f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}"
                )
                return

            print(f"[SUCCESS] Thanh toán thành công - Status: {response.status_code}")
            print(
                f"Response data: {json.dumps(response.json(), indent=2, ensure_ascii=False)}"
            )
            print("-" * 100)

            print("\n=== HOÀN THÀNH QUY TRÌNH ===")

        except Exception as e:
            print(f"\n[ERROR] Lỗi trong quá trình thực hiện: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_full_order_process())
