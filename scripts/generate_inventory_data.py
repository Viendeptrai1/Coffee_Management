#!/usr/bin/env python3
import sys
import os

# Thêm thư mục gốc vào Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.db_config import get_db, Base, engine
from app.models.models import Inventory, MenuItem, Recipe
from app.controllers.inventory_controller import InventoryController
from app.controllers.menu_controller import MenuController
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

def create_sample_inventory():
    """Tạo dữ liệu mẫu cho bảng Inventory"""
    db = get_db()
    
    # Danh sách nguyên liệu mẫu
    sample_inventory = [
        # Cà phê
        {"name": "Cà phê hạt Arabica", "quantity": 5000, "unit": "g", "supplier": "Trung Nguyên", "min_quantity": 1000},
        {"name": "Cà phê hạt Robusta", "quantity": 4000, "unit": "g", "supplier": "Trung Nguyên", "min_quantity": 800},
        {"name": "Cà phê xay", "quantity": 3000, "unit": "g", "supplier": "Trung Nguyên", "min_quantity": 500},
        
        # Sữa và kem
        {"name": "Sữa tươi không đường", "quantity": 10000, "unit": "ml", "supplier": "Vinamilk", "min_quantity": 2000},
        {"name": "Sữa đặc", "quantity": 5000, "unit": "ml", "supplier": "Vinamilk", "min_quantity": 1000},
        {"name": "Kem sữa", "quantity": 3000, "unit": "ml", "supplier": "Anchor", "min_quantity": 500},
        {"name": "Sữa chua", "quantity": 2000, "unit": "g", "supplier": "Vinamilk", "min_quantity": 500},
        {"name": "Bột kem sữa", "quantity": 1500, "unit": "g", "supplier": "Nestle", "min_quantity": 300},
        
        # Đường và siro
        {"name": "Đường trắng", "quantity": 8000, "unit": "g", "supplier": "Biên Hòa", "min_quantity": 1000},
        {"name": "Đường nâu", "quantity": 2000, "unit": "g", "supplier": "Biên Hòa", "min_quantity": 500},
        {"name": "Siro vani", "quantity": 1000, "unit": "ml", "supplier": "Torani", "min_quantity": 200},
        {"name": "Siro chocolate", "quantity": 1200, "unit": "ml", "supplier": "Torani", "min_quantity": 200},
        {"name": "Siro caramel", "quantity": 1200, "unit": "ml", "supplier": "Torani", "min_quantity": 200},
        {"name": "Siro hạnh nhân", "quantity": 1000, "unit": "ml", "supplier": "Torani", "min_quantity": 200},
        
        # Trà
        {"name": "Trà đen", "quantity": 2000, "unit": "g", "supplier": "Lipton", "min_quantity": 400},
        {"name": "Trà xanh", "quantity": 2000, "unit": "g", "supplier": "Cozy", "min_quantity": 400},
        {"name": "Trà hoa cúc", "quantity": 1000, "unit": "g", "supplier": "Cozy", "min_quantity": 200},
        {"name": "Trà hoa lài", "quantity": 1000, "unit": "g", "supplier": "Cozy", "min_quantity": 200},
        {"name": "Trà đào", "quantity": 1500, "unit": "g", "supplier": "Cozy", "min_quantity": 300},
        
        # Trái cây
        {"name": "Chanh tươi", "quantity": 2000, "unit": "g", "supplier": "Chợ đầu mối", "min_quantity": 500},
        {"name": "Cam tươi", "quantity": 3000, "unit": "g", "supplier": "Chợ đầu mối", "min_quantity": 1000},
        {"name": "Dâu tây", "quantity": 1500, "unit": "g", "supplier": "Chợ đầu mối", "min_quantity": 300},
        {"name": "Việt quất", "quantity": 1000, "unit": "g", "supplier": "Chợ đầu mối", "min_quantity": 200},
        {"name": "Xoài", "quantity": 2000, "unit": "g", "supplier": "Chợ đầu mối", "min_quantity": 500},
        {"name": "Đào miếng", "quantity": 1500, "unit": "g", "supplier": "Meko", "min_quantity": 300},
        
        # Nguyên liệu khác
        {"name": "Bột chocolate", "quantity": 2000, "unit": "g", "supplier": "Nestle", "min_quantity": 400},
        {"name": "Bột matcha", "quantity": 1000, "unit": "g", "supplier": "Nhật Bản", "min_quantity": 200},
        {"name": "Đá viên", "quantity": 10000, "unit": "g", "supplier": "Tự sản xuất", "min_quantity": 2000},
        {"name": "Whipping cream", "quantity": 2000, "unit": "ml", "supplier": "Anchor", "min_quantity": 500},
        {"name": "Sauce chocolate", "quantity": 1500, "unit": "ml", "supplier": "Hershey's", "min_quantity": 300},
        
        # Đồ khô
        {"name": "Hạt hạnh nhân", "quantity": 1000, "unit": "g", "supplier": "Mỹ", "min_quantity": 200},
        {"name": "Hạt macadamia", "quantity": 800, "unit": "g", "supplier": "Úc", "min_quantity": 200},
        {"name": "Cookie", "quantity": 1500, "unit": "g", "supplier": "Oreo", "min_quantity": 300},
        
        # Một số nguyên liệu gần hết để test cảnh báo
        {"name": "Trân châu đen", "quantity": 100, "unit": "g", "supplier": "Đài Loan", "min_quantity": 200},
        {"name": "Thạch trà xanh", "quantity": 150, "unit": "g", "supplier": "Đài Loan", "min_quantity": 200},
        {"name": "Bột caramel", "quantity": 50, "unit": "g", "supplier": "Nestle", "min_quantity": 100}
    ]
    
    try:
        # Thêm từng mục vào cơ sở dữ liệu
        for item in sample_inventory:
            # Kiểm tra xem đã tồn tại chưa
            existing = db.query(Inventory).filter(Inventory.name == item["name"]).first()
            if not existing:
                new_item = Inventory(
                    name=item["name"],
                    quantity=item["quantity"],
                    unit=item["unit"],
                    supplier=item["supplier"],
                    min_quantity=item["min_quantity"],
                    last_update=datetime.now()
                )
                db.add(new_item)
        
        db.commit()
        print("Đã thêm dữ liệu mẫu cho kho hàng!")
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Lỗi khi thêm dữ liệu mẫu cho kho hàng: {e}")
    finally:
        db.close()

def create_sample_recipes():
    """Tạo dữ liệu mẫu cho bảng Recipe"""
    db = get_db()
    
    # Lấy danh sách menu items
    menu_items = db.query(MenuItem).all()
    
    # Nếu không có menu items, không thể tạo công thức
    if not menu_items:
        print("Không có món trong menu, không thể tạo công thức!")
        return
    
    # Lấy danh sách nguyên liệu
    inventory_items = db.query(Inventory).all()
    
    # Tạo map ánh xạ từ tên đến ID để dễ sử dụng
    inventory_map = {item.name: item.id for item in inventory_items}
    menu_map = {item.name: item.id for item in menu_items}
    
    # Danh sách công thức mẫu
    sample_recipes = [
        # Cà phê đen
        {
            "menu_item": "Cà phê đen",
            "ingredients": [
                {"name": "Cà phê xay", "quantity": 20},
                {"name": "Đường trắng", "quantity": 10},
                {"name": "Đá viên", "quantity": 100}
            ]
        },
        # Cà phê sữa
        {
            "menu_item": "Cà phê sữa",
            "ingredients": [
                {"name": "Cà phê xay", "quantity": 20},
                {"name": "Sữa đặc", "quantity": 30},
                {"name": "Đường trắng", "quantity": 5},
                {"name": "Đá viên", "quantity": 100}
            ]
        },
        # Cappuccino
        {
            "menu_item": "Cappuccino",
            "ingredients": [
                {"name": "Cà phê hạt Arabica", "quantity": 18},
                {"name": "Sữa tươi không đường", "quantity": 120},
                {"name": "Bột kem sữa", "quantity": 10}
            ]
        },
        # Latte
        {
            "menu_item": "Latte",
            "ingredients": [
                {"name": "Cà phê hạt Arabica", "quantity": 18},
                {"name": "Sữa tươi không đường", "quantity": 150},
                {"name": "Bột kem sữa", "quantity": 5}
            ]
        },
        # Mocha
        {
            "menu_item": "Mocha",
            "ingredients": [
                {"name": "Cà phê hạt Arabica", "quantity": 18},
                {"name": "Sữa tươi không đường", "quantity": 120},
                {"name": "Sauce chocolate", "quantity": 20},
                {"name": "Whipping cream", "quantity": 20}
            ]
        },
        # Trà đào
        {
            "menu_item": "Trà đào",
            "ingredients": [
                {"name": "Trà đào", "quantity": 15},
                {"name": "Đường trắng", "quantity": 20},
                {"name": "Đào miếng", "quantity": 30},
                {"name": "Đá viên", "quantity": 150}
            ]
        },
        # Trà sữa trân châu
        {
            "menu_item": "Trà sữa trân châu",
            "ingredients": [
                {"name": "Trà đen", "quantity": 15},
                {"name": "Sữa đặc", "quantity": 30},
                {"name": "Đường nâu", "quantity": 20},
                {"name": "Trân châu đen", "quantity": 50},
                {"name": "Đá viên", "quantity": 150}
            ]
        },
        # Matcha đá xay
        {
            "menu_item": "Matcha đá xay",
            "ingredients": [
                {"name": "Bột matcha", "quantity": 15},
                {"name": "Sữa tươi không đường", "quantity": 100},
                {"name": "Đường trắng", "quantity": 20},
                {"name": "Đá viên", "quantity": 200},
                {"name": "Whipping cream", "quantity": 30}
            ]
        },
        # Sinh tố xoài
        {
            "menu_item": "Sinh tố xoài",
            "ingredients": [
                {"name": "Xoài", "quantity": 150},
                {"name": "Sữa chua", "quantity": 100},
                {"name": "Đường trắng", "quantity": 20},
                {"name": "Đá viên", "quantity": 100}
            ]
        },
        # Nước cam
        {
            "menu_item": "Nước cam",
            "ingredients": [
                {"name": "Cam tươi", "quantity": 300},
                {"name": "Đường trắng", "quantity": 15},
                {"name": "Đá viên", "quantity": 100}
            ]
        }
    ]
    
    try:
        # Thêm công thức cho từng món
        for recipe in sample_recipes:
            menu_item_name = recipe["menu_item"]
            
            # Kiểm tra xem món này có trong menu không
            if menu_item_name in menu_map:
                menu_item_id = menu_map[menu_item_name]
                
                # Thêm từng nguyên liệu vào công thức
                for ingredient in recipe["ingredients"]:
                    ingredient_name = ingredient["name"]
                    
                    # Kiểm tra xem nguyên liệu này có trong kho không
                    if ingredient_name in inventory_map:
                        inventory_id = inventory_map[ingredient_name]
                        quantity = ingredient["quantity"]
                        
                        # Kiểm tra xem đã có công thức này chưa
                        existing = db.query(Recipe).filter(
                            Recipe.menu_item_id == menu_item_id,
                            Recipe.inventory_id == inventory_id
                        ).first()
                        
                        if not existing:
                            # Thêm nguyên liệu vào công thức
                            new_recipe = Recipe(
                                menu_item_id=menu_item_id,
                                inventory_id=inventory_id,
                                quantity=quantity
                            )
                            db.add(new_recipe)
                    else:
                        print(f"Không tìm thấy nguyên liệu '{ingredient_name}' trong kho")
            else:
                print(f"Không tìm thấy món '{menu_item_name}' trong menu")
        
        db.commit()
        print("Đã thêm dữ liệu mẫu cho công thức!")
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Lỗi khi thêm dữ liệu mẫu cho công thức: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Bắt đầu tạo dữ liệu mẫu cho kho hàng và công thức...")
    
    # Tạo dữ liệu mẫu cho kho hàng
    create_sample_inventory()
    
    # Tạo dữ liệu mẫu cho công thức
    create_sample_recipes()
    
    print("Hoàn thành tạo dữ liệu mẫu!") 