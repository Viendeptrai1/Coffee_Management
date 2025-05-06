from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db_config import Base

# Bảng Recipe để lưu công thức món ăn
class Recipe(Base):
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    inventory_id = Column(Integer, ForeignKey("inventories.id"))
    quantity = Column(Float, nullable=False)  # Số lượng nguyên liệu cần dùng
    
    menu_item = relationship("MenuItem", back_populates="ingredients")
    inventory = relationship("Inventory", back_populates="used_in_recipes")

class MenuCategory(Base):
    __tablename__ = "menu_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    menu_items = relationship("MenuItem", back_populates="category")

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    image_path = Column(String(255), nullable=True)
    category_id = Column(Integer, ForeignKey("menu_categories.id"))
    is_available = Column(Boolean, default=True)
    preparation_time = Column(Integer, default=5)  # Thời gian chuẩn bị (phút)
    
    category = relationship("MenuCategory", back_populates="menu_items")
    order_items = relationship("OrderItem", back_populates="menu_item")
    ingredients = relationship("Recipe", back_populates="menu_item")

class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    status = Column(String(20), default="trống")  # trống, đang phục vụ, đã đặt trước
    capacity = Column(Integer, default=4)
    location = Column(String(50), nullable=True)
    
    orders = relationship("Order", back_populates="table")
    reservations = relationship("Reservation", back_populates="table")

class Staff(Base):
    __tablename__ = "staffs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)  # chức vụ: quản lý, phục vụ, pha chế, ...
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    shift = Column(String(50), nullable=True)  # ca làm việc
    
    orders = relationship("Order", back_populates="staff")
    shifts = relationship("Shift", back_populates="staff")

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True, unique=True)
    email = Column(String(100), nullable=True)
    points = Column(Integer, default=0)  # điểm tích lũy
    
    orders = relationship("Order", back_populates="customer")
    reservations = relationship("Reservation", back_populates="customer")
    feedbacks = relationship("Feedback", back_populates="customer")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("tables.id"))
    staff_id = Column(Integer, ForeignKey("staffs.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    order_time = Column(DateTime, default=datetime.now)
    status = Column(String(20), default="chờ xử lý")  # chờ xử lý, đang phục vụ, đã thanh toán, hủy
    total_amount = Column(Float, default=0)
    discount = Column(Float, default=0)
    final_amount = Column(Float, default=0)
    payment_method = Column(String(50), nullable=True)
    note = Column(Text, nullable=True)
    
    table = relationship("Table", back_populates="orders")
    staff = relationship("Staff", back_populates="orders")
    customer = relationship("Customer", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")
    feedbacks = relationship("Feedback", back_populates="order")

class Inventory(Base):
    __tablename__ = "inventories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)  # đơn vị: kg, g, chai, ...
    supplier = Column(String(100), nullable=True)
    last_update = Column(DateTime, default=datetime.now)
    min_quantity = Column(Float, default=0)  # số lượng tối thiểu cần có
    
    used_in_recipes = relationship("Recipe", back_populates="inventory")

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    table_id = Column(Integer, ForeignKey("tables.id"))
    reservation_time = Column(DateTime, nullable=False)
    duration = Column(Integer, default=60)  # thời gian dự kiến (phút)
    num_guests = Column(Integer, default=1)
    status = Column(String(20), default="đã đặt")  # đã đặt, đã xác nhận, đã đến, hủy
    note = Column(Text, nullable=True)
    
    customer = relationship("Customer", back_populates="reservations")
    table = relationship("Table", back_populates="reservations")

class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staffs.id"))
    date = Column(DateTime, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(20), default="lịch")  # lịch, đang làm, đã làm, vắng
    
    staff = relationship("Staff", back_populates="shifts")

# Chuyển đổi order_item từ Table sang class đầy đủ
class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer, default=1)
    note = Column(String(255), nullable=True)
    status = Column(String(20), default="chờ pha chế")  # chờ pha chế, đang pha chế, đã hoàn thành, hủy
    created_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)
    completed_by = Column(Integer, ForeignKey("staffs.id"), nullable=True)
    
    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="order_items")
    completed_by_staff = relationship("Staff", foreign_keys=[completed_by])

class Feedback(Base):
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    rating = Column(Integer, nullable=False)  # 1-5 sao
    comment = Column(Text, nullable=True)
    service_rating = Column(Integer, nullable=True)  # 1-5 sao đánh giá dịch vụ
    food_rating = Column(Integer, nullable=True)  # 1-5 sao đánh giá món ăn
    ambience_rating = Column(Integer, nullable=True)  # 1-5 sao đánh giá không khí
    created_at = Column(DateTime, default=datetime.now)
    
    order = relationship("Order")
    customer = relationship("Customer") 