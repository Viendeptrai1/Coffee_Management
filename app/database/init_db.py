from app.database.db_config import engine, get_db
from app.models.models import Base, MenuItem, MenuCategory, Table, Staff, Feedback, Shift
import os
import hashlib

def hash_password(password):
    """Hashes the password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    # Tạo tất cả các bảng trong cơ sở dữ liệu
    Base.metadata.create_all(bind=engine)
    
    # Kiểm tra xem đã có dữ liệu mẫu chưa
    db = get_db()
    if db.query(MenuCategory).count() == 0:
        populate_sample_data(db)
    db.close()

def populate_sample_data(db):
    # Thêm danh mục món
    categories = [
        MenuCategory(name="Cà phê", description="Các loại cà phê"),
        MenuCategory(name="Trà", description="Các loại trà"),
        MenuCategory(name="Nước ép", description="Các loại nước ép trái cây"),
        MenuCategory(name="Sinh tố", description="Các loại sinh tố"),
        MenuCategory(name="Bánh ngọt", description="Các loại bánh ngọt")
    ]
    db.add_all(categories)
    db.commit()
    
    # Thêm món ăn/đồ uống
    menu_items = [
        MenuItem(name="Cà phê đen", price=25000, category_id=1),
        MenuItem(name="Cà phê sữa", price=30000, category_id=1),
        MenuItem(name="Cappuccino", price=45000, category_id=1),
        MenuItem(name="Trà xanh", price=30000, category_id=2),
        MenuItem(name="Trà chanh", price=25000, category_id=2),
        MenuItem(name="Nước ép cam", price=35000, category_id=3),
        MenuItem(name="Nước ép dứa", price=35000, category_id=3),
        MenuItem(name="Sinh tố xoài", price=40000, category_id=4),
        MenuItem(name="Sinh tố bơ", price=45000, category_id=4),
        MenuItem(name="Bánh flan", price=20000, category_id=5),
        MenuItem(name="Bánh tiramisu", price=35000, category_id=5)
    ]
    db.add_all(menu_items)
    db.commit()
    
    # Thêm bàn
    tables = [
        Table(name="Bàn 1", capacity=2, location="Cửa sổ"),
        Table(name="Bàn 2", capacity=2, location="Cửa sổ"),
        Table(name="Bàn 3", capacity=4, location="Giữa"),
        Table(name="Bàn 4", capacity=4, location="Giữa"),
        Table(name="Bàn 5", capacity=6, location="Góc"),
        Table(name="Bàn 6", capacity=6, location="Góc"),
        Table(name="Bàn 7", capacity=8, location="Sân vườn"),
        Table(name="Bàn 8", capacity=8, location="Sân vườn")
    ]
    db.add_all(tables)
    db.commit()
    
    # Thêm nhân viên với mật khẩu đã mã hóa
    staffs = [
        Staff(name="Admin", role="Quản lý", username="admin", password=hash_password("admin123"), phone="0123456789"),
        Staff(name="Nguyễn Văn A", role="Phục vụ", username="nguyenvana", password=hash_password("123456"), phone="0123456781"),
        Staff(name="Trần Thị B", role="Pha chế", username="tranthib", password=hash_password("123456"), phone="0123456782")
    ]
    db.add_all(staffs)
    db.commit()

if __name__ == "__main__":
    init_db() 