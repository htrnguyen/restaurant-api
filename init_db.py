import os
from datetime import datetime

import bcrypt
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

# Khởi tạo Supabase client
supabase: Client = create_client(
    supabase_url=os.getenv("SUPABASE_URL"), supabase_key=os.getenv("SUPABASE_KEY")
)


def init_database():
    """Khởi tạo dữ liệu mẫu"""
    try:
        print("Bắt đầu khởi tạo dữ liệu mẫu...")

        # Tạo người dùng mẫu
        print("\nTạo người dùng mẫu...")
        password = "test123"
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        users = [
            {
                "username": "admin",
                "password": hashed.decode(),
                "role": "admin",
                "full_name": "Quản trị viên",
                "status": "active",
            },
            {
                "username": "nhanvien1",
                "password": hashed.decode(),
                "role": "staff",
                "full_name": "Nhân viên 1",
                "status": "active",
            },
            {
                "username": "nhanvien2",
                "password": hashed.decode(),
                "role": "staff",
                "full_name": "Nhân viên 2",
                "status": "active",
            },
        ]
        supabase.table("users").upsert(users).execute()

        # Tạo danh mục món ăn
        print("\nTạo danh mục món ăn...")
        categories = [
            {"id": 1, "name": "Món chính"},
            {"id": 2, "name": "Khai vị"},
            {"id": 3, "name": "Tráng miệng"},
            {"id": 4, "name": "Đồ uống"},
        ]
        supabase.table("menu_categories").upsert(categories).execute()

        # Tạo các món ăn mẫu
        print("\nTạo món ăn mẫu...")
        menu_items = [
            {
                "name": "Bò bít tết",
                "description": "Bò Úc thượng hạng sốt nấm",
                "price": 250000,
                "status": "available",
                "category_id": 1,
            },
            {
                "name": "Salad Ceasar",
                "description": "Salad tươi sốt Ceasar",
                "price": 85000,
                "status": "available",
                "category_id": 2,
            },
            {
                "name": "Súp cua",
                "description": "Súp cua nguyên chất",
                "price": 65000,
                "status": "available",
                "category_id": 2,
            },
            {
                "name": "Cá hồi áp chảo",
                "description": "Cá hồi Na Uy áp chảo",
                "price": 220000,
                "status": "available",
                "category_id": 1,
            },
        ]
        supabase.table("menu_items").upsert(menu_items).execute()

        # Tạo bàn mẫu
        print("\nTạo bàn mẫu...")
        tables = [
            {"number": 1, "status": "available"},
            {"number": 2, "status": "available"},
            {"number": 3, "status": "available"},
            {"number": 4, "status": "available"},
        ]
        supabase.table("tables").upsert(tables).execute()

        # Tạo nguyên liệu mẫu
        print("\nTạo nguyên liệu mẫu...")
        ingredients = [
            {"name": "Thịt bò", "quantity": 100, "unit": "kg", "uom": "kg"},
            {"name": "Rau xà lách", "quantity": 50, "unit": "kg", "uom": "kg"},
            {"name": "Cá hồi", "quantity": 80, "unit": "kg", "uom": "kg"},
            {"name": "Nấm các loại", "quantity": 30, "unit": "kg", "uom": "kg"},
        ]
        supabase.table("ingredients").upsert(ingredients).execute()

        # Lấy ID của các món ăn và nguyên liệu
        menu_items_resp = supabase.table("menu_items").select("id,name").execute()
        ingredients_resp = supabase.table("ingredients").select("id,name").execute()

        menu_items_map = {item["name"]: item["id"] for item in menu_items_resp.data}
        ingredients_map = {ing["name"]: ing["id"] for ing in ingredients_resp.data}

        # Tạo quan hệ món ăn - nguyên liệu
        print("\nTạo quan hệ món ăn - nguyên liệu...")
        item_ingredients = [
            {
                "item_id": menu_items_map["Bò bít tết"],
                "ingredient_id": ingredients_map["Thịt bò"],
                "quantity": 0.3,
            },
            {
                "item_id": menu_items_map["Salad Ceasar"],
                "ingredient_id": ingredients_map["Rau xà lách"],
                "quantity": 0.2,
            },
            {
                "item_id": menu_items_map["Cá hồi áp chảo"],
                "ingredient_id": ingredients_map["Cá hồi"],
                "quantity": 0.25,
            },
            {
                "item_id": menu_items_map["Bò bít tết"],
                "ingredient_id": ingredients_map["Nấm các loại"],
                "quantity": 0.05,
            },
        ]
        supabase.table("item_ingredients").upsert(item_ingredients).execute()

        print("\nKhởi tạo dữ liệu mẫu thành công!")

    except Exception as e:
        print(f"Lỗi: {str(e)}")
        raise e


if __name__ == "__main__":
    init_database()
