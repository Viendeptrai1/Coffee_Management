#!/usr/bin/env python3
import sys
import os

# Thêm thư mục gốc vào Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.db_config import get_db, Base, engine
from app.models.models import MenuItem, MenuCategory
from sqlalchemy.exc import SQLAlchemyError

def create_sample_categories():
    """Tạo các danh mục món"""
    db = get_db()
    
    # Danh sách danh mục mẫu
    categories = [
        {"name": "Cà phê", "description": "Các loại cà phê truyền thống và đặc biệt"},
        {"name": "Trà", "description": "Các loại trà và trà sữa"},
        {"name": "Nước ép", "description": "Nước ép hoa quả tươi"},
        {"name": "Sinh tố", "description": "Các loại sinh tố từ trái cây tươi"},
        {"name": "Đồ uống đặc biệt", "description": "Các món đặc biệt của quán"},
        {"name": "Bánh ngọt", "description": "Các loại bánh và đồ ăn nhẹ"}
    ]
    
    category_ids = {}
    
    try:
        # Thêm từng danh mục
        for category in categories:
            # Kiểm tra xem danh mục đã tồn tại chưa
            existing = db.query(MenuCategory).filter(MenuCategory.name == category["name"]).first()
            
            if existing:
                category_ids[category["name"]] = existing.id
            else:
                new_category = MenuCategory(
                    name=category["name"],
                    description=category["description"]
                )
                db.add(new_category)
                db.flush()  # Flush để lấy ID mà không cần commit
                category_ids[category["name"]] = new_category.id
        
        db.commit()
        print("Đã thêm danh mục món!")
        return category_ids
        
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Lỗi khi thêm danh mục: {e}")
        return {}
    finally:
        db.close()

def create_sample_menu_items(category_ids):
    """Tạo các món trong menu"""
    if not category_ids:
        print("Không có danh mục, không thể thêm món!")
        return
    
    db = get_db()
    
    # Danh sách món mẫu
    menu_items = [
        # Cà phê
        {"name": "Cà phê đen", "price": 25000, "description": "Cà phê truyền thống đậm đà", 
         "category": "Cà phê", "preparation_time": 3},
        {"name": "Cà phê sữa", "price": 29000, "description": "Cà phê với sữa đặc", 
         "category": "Cà phê", "preparation_time": 3},
        {"name": "Cappuccino", "price": 45000, "description": "Cà phê Ý với bọt sữa", 
         "category": "Cà phê", "preparation_time": 5},
        {"name": "Latte", "price": 49000, "description": "Cà phê với nhiều sữa và ít bọt", 
         "category": "Cà phê", "preparation_time": 5},
        {"name": "Americano", "price": 39000, "description": "Espresso pha loãng với nước nóng", 
         "category": "Cà phê", "preparation_time": 4},
        {"name": "Espresso", "price": 35000, "description": "Cà phê đậm đặc kiểu Ý", 
         "category": "Cà phê", "preparation_time": 2},
        {"name": "Mocha", "price": 55000, "description": "Cà phê với sữa và sốt chocolate", 
         "category": "Cà phê", "preparation_time": 6},
        
        # Trà
        {"name": "Trà đào", "price": 45000, "description": "Trà với đào tươi và syrup đào", 
         "category": "Trà", "preparation_time": 4},
        {"name": "Trà sữa trân châu", "price": 49000, "description": "Trà sữa với trân châu đen", 
         "category": "Trà", "preparation_time": 5},
        {"name": "Trà chanh", "price": 35000, "description": "Trà với chanh tươi và đường", 
         "category": "Trà", "preparation_time": 3},
        {"name": "Trà gừng", "price": 39000, "description": "Trà với gừng tươi - tốt cho sức khỏe", 
         "category": "Trà", "preparation_time": 4},
        {"name": "Trà xanh matcha", "price": 45000, "description": "Trà xanh matcha Nhật Bản", 
         "category": "Trà", "preparation_time": 4},
        
        # Nước ép
        {"name": "Nước cam", "price": 39000, "description": "Nước cam tươi vắt", 
         "category": "Nước ép", "preparation_time": 5},
        {"name": "Nước ép táo", "price": 45000, "description": "Nước ép từ táo tươi nguyên chất", 
         "category": "Nước ép", "preparation_time": 6},
        {"name": "Nước ép dưa hấu", "price": 39000, "description": "Nước ép từ dưa hấu tươi ngọt mát", 
         "category": "Nước ép", "preparation_time": 5},
        {"name": "Nước ép dứa", "price": 42000, "description": "Nước ép từ dứa tươi", 
         "category": "Nước ép", "preparation_time": 6},
        
        # Sinh tố
        {"name": "Sinh tố xoài", "price": 49000, "description": "Sinh tố từ xoài chín mọng", 
         "category": "Sinh tố", "preparation_time": 7},
        {"name": "Sinh tố bơ", "price": 55000, "description": "Sinh tố từ bơ béo ngậy", 
         "category": "Sinh tố", "preparation_time": 7},
        {"name": "Sinh tố dâu", "price": 53000, "description": "Sinh tố từ dâu tây tươi", 
         "category": "Sinh tố", "preparation_time": 7},
        {"name": "Sinh tố chuối", "price": 45000, "description": "Sinh tố chuối mát lành", 
         "category": "Sinh tố", "preparation_time": 6},
        
        # Đồ uống đặc biệt
        {"name": "Matcha đá xay", "price": 59000, "description": "Matcha Nhật Bản xay với đá và sữa", 
         "category": "Đồ uống đặc biệt", "preparation_time": 8},
        {"name": "Chocolate đá xay", "price": 59000, "description": "Chocolate xay với đá và sữa", 
         "category": "Đồ uống đặc biệt", "preparation_time": 8},
        {"name": "Cookie đá xay", "price": 59000, "description": "Cookie xay với đá và sữa", 
         "category": "Đồ uống đặc biệt", "preparation_time": 8},
        {"name": "Caramel Macchiato", "price": 55000, "description": "Espresso với caramel và sữa", 
         "category": "Đồ uống đặc biệt", "preparation_time": 7},
        
        # Bánh ngọt
        {"name": "Bánh chuối", "price": 35000, "description": "Bánh chuối mềm thơm", 
         "category": "Bánh ngọt", "preparation_time": 0},
        {"name": "Tiramisu", "price": 45000, "description": "Bánh tiramisu truyền thống", 
         "category": "Bánh ngọt", "preparation_time": 0},
        {"name": "Bánh brownie", "price": 39000, "description": "Bánh brownie chocolate", 
         "category": "Bánh ngọt", "preparation_time": 0},
        {"name": "Bánh phô mai", "price": 42000, "description": "Bánh phô mai mềm mịn", 
         "category": "Bánh ngọt", "preparation_time": 0}
    ]
    
    try:
        # Thêm từng món vào menu
        for item in menu_items:
            # Kiểm tra xem món đã tồn tại chưa
            existing = db.query(MenuItem).filter(MenuItem.name == item["name"]).first()
            
            if not existing and item["category"] in category_ids:
                new_item = MenuItem(
                    name=item["name"],
                    price=item["price"],
                    description=item["description"],
                    category_id=category_ids[item["category"]],
                    preparation_time=item["preparation_time"],
                    is_available=True
                )
                db.add(new_item)
        
        db.commit()
        print("Đã thêm các món vào menu!")
        
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Lỗi khi thêm món vào menu: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Bắt đầu tạo dữ liệu mẫu cho menu...")
    
    # Tạo danh mục
    category_ids = create_sample_categories()
    
    # Tạo món
    create_sample_menu_items(category_ids)
    
    print("Hoàn thành tạo dữ liệu mẫu cho menu!") 