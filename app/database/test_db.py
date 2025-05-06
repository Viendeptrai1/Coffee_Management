import os
import sys
import hashlib
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Đảm bảo có thể import các module từ thư mục gốc
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.database.db_config import Base
from app.models.models import (MenuCategory, MenuItem, Table, Staff, Customer, 
                             Order, OrderItem, Inventory, Reservation, Shift)

def hash_password(password):
    """Hashes the password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_test_database():
    """Tạo cơ sở dữ liệu thử nghiệm với dữ liệu mẫu cho 1 năm"""
    from app.database.db_config import DATABASE_URL
    
    # Kết nối tới cơ sở dữ liệu
    engine = create_engine(DATABASE_URL)
    Base.metadata.drop_all(engine)  # Xóa tất cả bảng hiện có
    Base.metadata.create_all(engine)  # Tạo lại các bảng
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 1. Tạo danh mục menu
        categories = [
            {"name": "Cà phê", "description": "Các loại cà phê từ truyền thống đến hiện đại"},
            {"name": "Trà", "description": "Các loại trà từ truyền thống đến hiện đại"},
            {"name": "Nước ép", "description": "Nước ép trái cây tươi"},
            {"name": "Đồ uống đá xay", "description": "Các loại đồ uống đá xay phù hợp mùa hè"},
            {"name": "Đồ ăn", "description": "Bánh ngọt và đồ ăn nhẹ"}
        ]
        
        category_objects = []
        for cat in categories:
            category = MenuCategory(name=cat["name"], description=cat["description"])
            session.add(category)
            category_objects.append(category)
        
        session.commit()
        
        # 2. Tạo các món trong menu
        menu_items = [
            # Cà phê
            {"name": "Cà phê đen", "price": 20000, "category_id": 1, "preparation_time": 3},
            {"name": "Cà phê sữa", "price": 25000, "category_id": 1, "preparation_time": 3},
            {"name": "Bạc xỉu", "price": 30000, "category_id": 1, "preparation_time": 4},
            {"name": "Cappuccino", "price": 35000, "category_id": 1, "preparation_time": 5},
            {"name": "Latte", "price": 35000, "category_id": 1, "preparation_time": 5},
            {"name": "Americano", "price": 30000, "category_id": 1, "preparation_time": 4},
            {"name": "Espresso", "price": 25000, "category_id": 1, "preparation_time": 2},
            {"name": "Mocha", "price": 40000, "category_id": 1, "preparation_time": 6},
            
            # Trà
            {"name": "Trà đào", "price": 30000, "category_id": 2, "preparation_time": 4},
            {"name": "Trà chanh", "price": 25000, "category_id": 2, "preparation_time": 3},
            {"name": "Trà hoa cúc", "price": 30000, "category_id": 2, "preparation_time": 3},
            {"name": "Trà gừng", "price": 30000, "category_id": 2, "preparation_time": 4},
            {"name": "Trà xanh", "price": 25000, "category_id": 2, "preparation_time": 3},
            {"name": "Hồng trà", "price": 25000, "category_id": 2, "preparation_time": 3},
            {"name": "Trà sữa truyền thống", "price": 35000, "category_id": 2, "preparation_time": 5},
            {"name": "Trà sữa matcha", "price": 40000, "category_id": 2, "preparation_time": 6},
            
            # Nước ép
            {"name": "Nước cam", "price": 35000, "category_id": 3, "preparation_time": 5},
            {"name": "Nước dưa hấu", "price": 35000, "category_id": 3, "preparation_time": 5},
            {"name": "Nước ép táo", "price": 40000, "category_id": 3, "preparation_time": 6},
            {"name": "Nước ép dứa", "price": 40000, "category_id": 3, "preparation_time": 6},
            {"name": "Nước ép cà rốt", "price": 40000, "category_id": 3, "preparation_time": 7},
            {"name": "Sinh tố bơ", "price": 45000, "category_id": 3, "preparation_time": 8},
            {"name": "Sinh tố dâu", "price": 45000, "category_id": 3, "preparation_time": 7},
            {"name": "Sinh tố xoài", "price": 45000, "category_id": 3, "preparation_time": 7},
            
            # Đồ uống đá xay
            {"name": "Frappuccino cà phê", "price": 45000, "category_id": 4, "preparation_time": 8},
            {"name": "Frappuccino socola", "price": 45000, "category_id": 4, "preparation_time": 8},
            {"name": "Frappuccino matcha", "price": 50000, "category_id": 4, "preparation_time": 8},
            {"name": "Đá xay caramel", "price": 50000, "category_id": 4, "preparation_time": 9},
            {"name": "Đá xay trà xanh", "price": 45000, "category_id": 4, "preparation_time": 8},
            {"name": "Đá xay dâu", "price": 50000, "category_id": 4, "preparation_time": 9},
            
            # Đồ ăn
            {"name": "Bánh sừng bò", "price": 25000, "category_id": 5, "preparation_time": 1},
            {"name": "Bánh chocolate", "price": 30000, "category_id": 5, "preparation_time": 1},
            {"name": "Bánh bông lan", "price": 25000, "category_id": 5, "preparation_time": 1},
            {"name": "Bánh tiramisu", "price": 35000, "category_id": 5, "preparation_time": 1},
            {"name": "Sandwich gà", "price": 40000, "category_id": 5, "preparation_time": 10},
            {"name": "Sandwich trứng", "price": 35000, "category_id": 5, "preparation_time": 10},
            {"name": "Mì Ý", "price": 50000, "category_id": 5, "preparation_time": 15},
            {"name": "Salad", "price": 40000, "category_id": 5, "preparation_time": 10}
        ]
        
        menu_item_objects = []
        for item in menu_items:
            menu_item = MenuItem(
                name=item["name"],
                price=item["price"],
                category_id=item["category_id"],
                description=f"Mô tả cho {item['name']}",
                is_available=True,
                preparation_time=item["preparation_time"]
            )
            session.add(menu_item)
            menu_item_objects.append(menu_item)
        
        session.commit()
        
        # 3. Tạo các bàn
        tables = [
            {"name": "Bàn 1", "capacity": 2, "location": "Cửa sổ"},
            {"name": "Bàn 2", "capacity": 2, "location": "Cửa sổ"},
            {"name": "Bàn 3", "capacity": 4, "location": "Giữa"},
            {"name": "Bàn 4", "capacity": 4, "location": "Giữa"},
            {"name": "Bàn 5", "capacity": 6, "location": "Góc"},
            {"name": "Bàn 6", "capacity": 6, "location": "Góc"},
            {"name": "Bàn 7", "capacity": 8, "location": "Sân vườn"},
            {"name": "Bàn 8", "capacity": 8, "location": "Sân vườn"},
            {"name": "Bàn 9", "capacity": 4, "location": "Giữa"},
            {"name": "Bàn 10", "capacity": 4, "location": "Giữa"},
            {"name": "Bàn 11", "capacity": 2, "location": "Cửa sổ"},
            {"name": "Bàn 12", "capacity": 2, "location": "Cửa sổ"},
        ]
        
        table_objects = []
        for table in tables:
            t = Table(
                name=table["name"],
                capacity=table["capacity"],
                location=table["location"],
                status="trống"
            )
            session.add(t)
            table_objects.append(t)
        
        session.commit()
        
        # 4. Tạo nhân viên
        staffs = [
            {"name": "Nguyễn Văn Admin", "role": "Quản lý", "username": "admin", "password": "admin123", "shift": "Toàn thời gian"},
            {"name": "Trần Văn Phục Vụ", "role": "Phục vụ", "username": "phucvu", "password": "phucvu123", "shift": "Sáng"},
            {"name": "Lê Thị Pha Chế", "role": "Pha chế", "username": "phache", "password": "phache123", "shift": "Sáng"},
            {"name": "Phạm Văn Thu Ngân", "role": "Thu ngân", "username": "thungan", "password": "thungan123", "shift": "Sáng"},
            {"name": "Đỗ Thị Phục Vụ", "role": "Phục vụ", "username": "phucvu2", "password": "phucvu123", "shift": "Chiều"},
            {"name": "Hoàng Văn Pha Chế", "role": "Pha chế", "username": "phache2", "password": "phache123", "shift": "Chiều"},
            {"name": "Ngô Thị Thu Ngân", "role": "Thu ngân", "username": "thungan2", "password": "thungan123", "shift": "Chiều"}
        ]
        
        staff_objects = []
        for staff in staffs:
            s = Staff(
                name=staff["name"],
                role=staff["role"],
                username=staff["username"],
                password=hash_password(staff["password"]),
                phone=f"090{random.randint(1000000, 9999999)}",
                email=f"{staff['username']}@cafe.com",
                is_active=True,
                shift=staff["shift"]
            )
            session.add(s)
            staff_objects.append(s)
        
        session.commit()
        
        # 5. Tạo khách hàng
        customers = []
        for i in range(30):
            c = Customer(
                name=f"Khách hàng {i+1}",
                phone=f"097{random.randint(1000000, 9999999)}",
                email=f"customer{i+1}@example.com",
                points=random.randint(0, 100)
            )
            session.add(c)
            customers.append(c)
        
        session.commit()
        
        # 6. Tạo lịch làm việc
        shifts = []
        # Ngày bắt đầu là 1 năm trước
        start_date = datetime.now() - timedelta(days=365)
        
        # Cho mỗi ngày trong năm
        for day in range(365):
            current_date = start_date + timedelta(days=day)
            
            # Ca sáng: 8h-15h
            for staff in staff_objects:
                if staff.shift in ["Sáng", "Toàn thời gian"]:
                    shift_start = datetime.combine(current_date.date(), datetime.min.time()) + timedelta(hours=8)
                    shift_end = datetime.combine(current_date.date(), datetime.min.time()) + timedelta(hours=15)
                    shift = Shift(
                        staff_id=staff.id,
                        date=current_date,
                        start_time=shift_start,
                        end_time=shift_end,
                        status="đã làm" if current_date < datetime.now() else "lịch"
                    )
                    session.add(shift)
            
            # Ca chiều: 15h-22h
            for staff in staff_objects:
                if staff.shift in ["Chiều", "Toàn thời gian"]:
                    shift_start = datetime.combine(current_date.date(), datetime.min.time()) + timedelta(hours=15)
                    shift_end = datetime.combine(current_date.date(), datetime.min.time()) + timedelta(hours=22)
                    shift = Shift(
                        staff_id=staff.id,
                        date=current_date,
                        start_time=shift_start,
                        end_time=shift_end,
                        status="đã làm" if current_date < datetime.now() else "lịch"
                    )
                    session.add(shift)
        
        session.commit()
        
        # 7. Tạo đơn hàng trong 1 năm
        orders = []
        # Số đơn trung bình mỗi ngày
        orders_per_day = 15
        
        # Phân bố số đơn theo ngày trong tuần (cuối tuần sẽ nhiều đơn hơn)
        day_distribution = {
            0: 0.8,  # Thứ 2: 80% so với trung bình
            1: 0.9,  # Thứ 3: 90% so với trung bình
            2: 1.0,  # Thứ 4: 100% so với trung bình
            3: 1.1,  # Thứ 5: 110% so với trung bình
            4: 1.2,  # Thứ 6: 120% so với trung bình
            5: 1.5,  # Thứ 7: 150% so với trung bình
            6: 1.5,  # Chủ nhật: 150% so với trung bình
        }
        
        # Phân bố số đơn theo giờ trong ngày
        hour_distribution = {
            8: 0.5,   # 8h: 50% so với trung bình
            9: 0.8,   # 9h: 80% so với trung bình
            10: 1.0,  # 10h: 100% so với trung bình
            11: 1.2,  # 11h: 120% so với trung bình
            12: 1.5,  # 12h: 150% so với trung bình
            13: 1.2,  # 13h: 120% so với trung bình
            14: 1.0,  # 14h: 100% so với trung bình
            15: 0.8,  # 15h: 80% so với trung bình
            16: 1.0,  # 16h: 100% so với trung bình
            17: 1.2,  # 17h: 120% so với trung bình
            18: 1.5,  # 18h: 150% so với trung bình
            19: 1.3,  # 19h: 130% so với trung bình
            20: 1.0,  # 20h: 100% so với trung bình
            21: 0.7,  # 21h: 70% so với trung bình
        }
        
        # Tỷ lệ đặt hàng online
        online_order_rate = 0.3
        
        # Cho mỗi ngày trong năm
        for day in range(365):
            current_date = start_date + timedelta(days=day)
            
            # Đảm bảo đơn hàng trong quá khứ
            if current_date >= datetime.now():
                continue
            
            # Số đơn trong ngày dựa trên ngày trong tuần
            day_of_week = current_date.weekday()
            orders_today = int(orders_per_day * day_distribution.get(day_of_week, 1.0))
            
            # Tạo đơn hàng cho mỗi giờ trong ngày
            for hour in range(8, 22):
                # Số đơn trong giờ này
                hour_factor = hour_distribution.get(hour, 1.0)
                orders_this_hour = max(1, int(orders_today / 14 * hour_factor))
                
                for i in range(orders_this_hour):
                    # Thời gian đơn hàng
                    minutes = random.randint(0, 59)
                    order_time = datetime.combine(current_date.date(), datetime.min.time()) + timedelta(hours=hour, minutes=minutes)
                    
                    # Xác định xem đơn hàng này là tại chỗ hay mang đi
                    is_online = random.random() < online_order_rate
                    
                    if is_online:
                        # Đơn online không cần bàn
                        table_id = None
                    else:
                        # Chọn một bàn ngẫu nhiên
                        table_id = random.choice(table_objects).id
                    
                    # Chọn nhân viên phù hợp với ca làm việc
                    if hour < 15:
                        staff = random.choice([s for s in staff_objects if s.shift in ["Sáng", "Toàn thời gian"]])
                    else:
                        staff = random.choice([s for s in staff_objects if s.shift in ["Chiều", "Toàn thời gian"]])
                    
                    # Khách hàng (có thể là khách vãng lai)
                    customer = None
                    if random.random() < 0.3:  # 30% khả năng có khách hàng đăng ký
                        customer = random.choice(customers)
                    
                    # Tạo đơn hàng
                    order = Order(
                        table_id=table_id,
                        staff_id=staff.id,
                        customer_id=customer.id if customer else None,
                        order_time=order_time,
                        status="đã thanh toán",
                        total_amount=0,
                        discount=0,
                        final_amount=0,
                        payment_method=random.choice(["tiền mặt", "thẻ", "ví điện tử"]),
                        note="Đơn hàng mang đi" if is_online else None
                    )
                    session.add(order)
                    session.flush()  # Để lấy ID của order
                    
                    # Số lượng món trong đơn
                    num_items = random.randint(1, 5)
                    total_amount = 0
                    
                    # Thêm các món vào đơn hàng
                    selected_items = random.sample(menu_item_objects, num_items)
                    for menu_item in selected_items:
                        quantity = random.randint(1, 3)
                        
                        # Thêm OrderItem
                        order_item = OrderItem(
                            order_id=order.id,
                            menu_item_id=menu_item.id,
                            quantity=quantity,
                            note=None,
                            status="đã hoàn thành",
                            created_at=order_time,
                            completed_at=order_time + timedelta(minutes=random.randint(5, 15)),
                            completed_by=random.choice([s.id for s in staff_objects if s.role == "Pha chế"])
                        )
                        session.add(order_item)
                        
                        # Cập nhật tổng tiền
                        item_total = menu_item.price * quantity
                        total_amount += item_total
                    
                    # Áp dụng giảm giá cho khách hàng thân thiết
                    discount = 0
                    if customer and customer.points > 50:
                        discount = total_amount * 0.1  # Giảm 10% cho khách hàng thân thiết
                    
                    # Cập nhật thông tin đơn hàng
                    order.total_amount = total_amount
                    order.discount = discount
                    order.final_amount = total_amount - discount
            
            # Commit sau mỗi ngày để tránh quá nhiều dữ liệu trong bộ nhớ
            session.commit()
            print(f"Đã tạo dữ liệu cho ngày {current_date.date()}")
        
        print("Đã tạo xong dữ liệu mẫu cho 1 năm!")
        
    except Exception as e:
        session.rollback()
        print(f"Lỗi: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    create_test_database() 