from app.database.db_config import get_db
from app.models.models import Order, MenuItem, OrderItem, Table
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta

class OrderController:
    @staticmethod
    def create_order(table_id, staff_id, customer_id=None):
        db = get_db()
        try:
            # Update table status
            table = db.query(Table).filter(Table.id == table_id).first()
            if not table:
                return None
            
            table.status = "đang phục vụ"
            
            # Create new order
            new_order = Order(
                table_id=table_id,
                staff_id=staff_id,
                customer_id=customer_id,
                status="chờ xử lý",
                order_time=datetime.now()
            )
            
            db.add(new_order)
            db.commit()
            db.refresh(new_order)
            return new_order.id
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def create_online_order(staff_id, customer_name=None, phone_number=None, order_type="Mang đi"):
        """Tạo đơn hàng online không gắn với bàn cụ thể"""
        db = get_db()
        try:
            # Create new order
            new_order = Order(
                staff_id=staff_id,
                status="chờ xử lý",
                order_time=datetime.now(),
                note=f"Đơn hàng {order_type.lower()} - KH: {customer_name} - SĐT: {phone_number}"
            )
            
            db.add(new_order)
            db.commit()
            db.refresh(new_order)
            return new_order.id
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def add_item_to_order(order_id, menu_item_id, quantity=1, note=None):
        db = get_db()
        try:
            # Get the order
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order or order.status == "đã thanh toán":
                return False
            
            # Get the menu item
            menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
            if not menu_item:
                return False
            
            # Check if item is already in the order
            existing_item = db.query(OrderItem).filter(
                OrderItem.order_id == order_id,
                OrderItem.menu_item_id == menu_item_id
            ).first()
            
            if existing_item:
                # Update quantity
                existing_item.quantity += quantity
                existing_item.note = note
            else:
                # Add new item
                new_item = OrderItem(
                    order_id=order_id,
                    menu_item_id=menu_item_id,
                    quantity=quantity,
                    note=note,
                    status="chờ pha chế"
                )
                db.add(new_item)
            
            # Update order total
            total = quantity * menu_item.price
            order.total_amount += total
            order.final_amount = order.total_amount - order.discount
            
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def update_order_item(order_id, menu_item_id, quantity, note=None):
        db = get_db()
        try:
            # Get the order
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order or order.status == "đã thanh toán":
                return False
            
            # Get the menu item
            menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
            if not menu_item:
                return False
            
            # Check if item is in the order
            existing_item = db.query(OrderItem).filter(
                OrderItem.order_id == order_id,
                OrderItem.menu_item_id == menu_item_id
            ).first()
            
            if not existing_item:
                return False
            
            # Calculate price difference
            old_total = existing_item.quantity * menu_item.price
            new_total = quantity * menu_item.price
            difference = new_total - old_total
            
            if quantity <= 0:
                # Remove item
                db.delete(existing_item)
            else:
                # Update quantity
                existing_item.quantity = quantity
                existing_item.note = note
            
            # Update order total
            order.total_amount += difference
            order.final_amount = order.total_amount - order.discount
            
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def get_order_details(order_id):
        db = get_db()
        try:
            # Tải order với các quan hệ cần thiết
            order = db.query(Order).options(
                joinedload(Order.table),
                joinedload(Order.staff),
                joinedload(Order.customer),
                joinedload(Order.order_items).joinedload(OrderItem.menu_item)
            ).filter(Order.id == order_id).first()
            
            if not order:
                return None
            
            items_details = []
            for item in order.order_items:
                items_details.append({
                    'id': item.menu_item.id,
                    'name': item.menu_item.name,
                    'price': item.menu_item.price,
                    'quantity': item.quantity,
                    'note': item.note,
                    'status': item.status,
                    'subtotal': item.menu_item.price * item.quantity
                })
            
            order_details = {
                'order_id': order.id,
                'table_id': order.table_id,
                'table_name': order.table.name if order.table else None,
                'staff_id': order.staff_id,
                'staff_name': order.staff.name if order.staff else None,
                'customer_id': order.customer_id,
                'customer_name': order.customer.name if order.customer else None,
                'order_time': order.order_time,
                'status': order.status,
                'total_amount': order.total_amount,
                'discount': order.discount,
                'final_amount': order.final_amount,
                'payment_method': order.payment_method,
                'note': order.note,
                'items': items_details
            }
            
            return order_details
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_current_orders():
        db = get_db()
        try:
            # Sử dụng joinedload để tải trước các quan hệ cần thiết
            return db.query(Order).options(
                joinedload(Order.table),
                joinedload(Order.staff),
                joinedload(Order.customer),
                joinedload(Order.order_items)
            ).filter(Order.status != "đã thanh toán").all()
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_orders_by_table(table_id):
        db = get_db()
        try:
            # Sử dụng joinedload để tải trước các quan hệ cần thiết
            return db.query(Order).options(
                joinedload(Order.table),
                joinedload(Order.staff),
                joinedload(Order.customer),
                joinedload(Order.order_items)
            ).filter(
                Order.table_id == table_id,
                Order.status != "đã thanh toán"
            ).all()
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def complete_order(order_id, payment_method="tiền mặt", discount=0):
        db = get_db()
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order or order.status == "đã thanh toán":
                return False
            
            # Update order
            order.status = "đã thanh toán"
            order.payment_method = payment_method
            order.discount = discount
            order.final_amount = order.total_amount - discount
            
            # Update table status
            if order.table:
                order.table.status = "trống"
            
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def cancel_order(order_id):
        db = get_db()
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order or order.status == "đã thanh toán":
                return False
            
            # Update order
            order.status = "hủy"
            
            # Update table status
            if order.table:
                order.table.status = "trống"
            
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def get_daily_revenue(day=None):
        if not day:
            day = datetime.now().date()
        
        start_date = datetime.combine(day, datetime.min.time())
        end_date = start_date + timedelta(days=1)
        
        db = get_db()
        try:
            revenue = db.query(func.sum(Order.final_amount)).filter(
                Order.order_time >= start_date,
                Order.order_time < end_date,
                Order.status == "đã thanh toán"
            ).scalar() or 0
            
            return revenue
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return 0
        finally:
            db.close()
    
    @staticmethod
    def get_popular_items(limit=10, days=30):
        start_date = datetime.now() - timedelta(days=days)
        
        db = get_db()
        try:
            # Query for popular items
            result = db.query(
                MenuItem.id,
                MenuItem.name,
                func.sum(OrderItem.quantity).label('total_ordered')
            ).join(
                OrderItem,
                MenuItem.id == OrderItem.menu_item_id
            ).join(
                Order,
                Order.id == OrderItem.order_id
            ).filter(
                Order.order_time >= start_date,
                Order.status == "đã thanh toán"
            ).group_by(
                MenuItem.id,
                MenuItem.name
            ).order_by(
                func.sum(OrderItem.quantity).desc()
            ).limit(limit).all()
            
            return result
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_active_orders():
        """Lấy tất cả các đơn hàng đang xử lý"""
        db = get_db()
        try:
            return db.query(Order).options(
                joinedload(Order.table),
                joinedload(Order.staff),
                joinedload(Order.order_items).joinedload(OrderItem.menu_item)
            ).filter(
                Order.status.in_(["chờ xử lý", "đang phục vụ"])
            ).order_by(Order.order_time.desc()).all()
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_pending_items():
        """Lấy tất cả các món đang chờ pha chế"""
        db = get_db()
        try:
            # Sử dụng ORM trực tiếp thay vì raw SQL
            order_items = db.query(OrderItem).join(
                Order, OrderItem.order_id == Order.id
            ).join(
                MenuItem, OrderItem.menu_item_id == MenuItem.id
            ).filter(
                Order.status.in_(["chờ xử lý", "đang phục vụ"]),
                OrderItem.status == "chờ pha chế"
            ).order_by(Order.order_time.asc()).options(
                joinedload(OrderItem.menu_item).joinedload(MenuItem.category),
                joinedload(OrderItem.order).joinedload(Order.table)
            ).all()
            
            return order_items
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def complete_order_item(order_item_id, staff_id=None):
        """Đánh dấu một món đã hoàn thành pha chế"""
        db = get_db()
        try:
            # Tìm order item
            order_item = db.query(OrderItem).filter(OrderItem.id == order_item_id).first()
            if not order_item:
                return False
                
            # Cập nhật trạng thái
            order_item.status = "đã hoàn thành"
            order_item.completed_by = staff_id
            order_item.completed_at = datetime.now()
            
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def get_completed_items_count(staff_id):
        """Lấy số lượng món đã hoàn thành bởi một nhân viên trong ca làm việc hiện tại"""
        db = get_db()
        try:
            # Lấy số lượng món đã làm trong ngày
            today = datetime.now().date()
            start_date = datetime.combine(today, datetime.min.time())
            end_date = start_date + timedelta(days=1)
            
            count = db.query(func.count(OrderItem.id)).filter(
                OrderItem.status == "đã hoàn thành",
                OrderItem.completed_by == staff_id,
                OrderItem.completed_at >= start_date,
                OrderItem.completed_at < end_date
            ).scalar() or 0
            
            return count
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return 0
        finally:
            db.close()
    
    @staticmethod
    def update_order_status(order_id, status):
        """Cập nhật trạng thái của đơn hàng"""
        db = get_db()
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return False
            
            order.status = status
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False
        finally:
            db.close() 