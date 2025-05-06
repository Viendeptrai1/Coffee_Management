from app.database.db_config import get_db
from app.models.models import Order, MenuItem, order_item, Table
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
            stmt = order_item.select().where(
                order_item.c.order_id == order_id,
                order_item.c.menu_item_id == menu_item_id
            )
            existing_item = db.execute(stmt).first()
            
            if existing_item:
                # Update quantity
                stmt = order_item.update().where(
                    order_item.c.order_id == order_id,
                    order_item.c.menu_item_id == menu_item_id
                ).values(quantity=existing_item.quantity + quantity)
                db.execute(stmt)
            else:
                # Add new item
                stmt = order_item.insert().values(
                    order_id=order_id,
                    menu_item_id=menu_item_id,
                    quantity=quantity,
                    note=note
                )
                db.execute(stmt)
            
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
            stmt = order_item.select().where(
                order_item.c.order_id == order_id,
                order_item.c.menu_item_id == menu_item_id
            )
            existing_item = db.execute(stmt).first()
            
            if not existing_item:
                return False
            
            # Calculate price difference
            old_total = existing_item.quantity * menu_item.price
            new_total = quantity * menu_item.price
            difference = new_total - old_total
            
            if quantity <= 0:
                # Remove item
                stmt = order_item.delete().where(
                    order_item.c.order_id == order_id,
                    order_item.c.menu_item_id == menu_item_id
                )
                db.execute(stmt)
            else:
                # Update quantity
                stmt = order_item.update().where(
                    order_item.c.order_id == order_id,
                    order_item.c.menu_item_id == menu_item_id
                ).values(quantity=quantity, note=note)
                db.execute(stmt)
            
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
                joinedload(Order.customer)
            ).filter(Order.id == order_id).first()
            
            if not order:
                return None
            
            # Get all items in the order
            stmt = order_item.select().where(order_item.c.order_id == order_id)
            order_items = db.execute(stmt).fetchall()
            
            items_details = []
            for item in order_items:
                menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
                items_details.append({
                    'id': menu_item.id,
                    'name': menu_item.name,
                    'price': menu_item.price,
                    'quantity': item.quantity,
                    'note': item.note,
                    'subtotal': menu_item.price * item.quantity
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
                joinedload(Order.customer)
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
                joinedload(Order.customer)
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
    def complete_order(order_id, payment_method, discount=0):
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
            stmt = db.query(
                MenuItem.id,
                MenuItem.name,
                func.sum(order_item.c.quantity).label('total_ordered')
            ).join(
                order_item,
                MenuItem.id == order_item.c.menu_item_id
            ).join(
                Order,
                Order.id == order_item.c.order_id
            ).filter(
                Order.order_time >= start_date,
                Order.status == "đã thanh toán"
            ).group_by(
                MenuItem.id
            ).order_by(
                func.sum(order_item.c.quantity).desc()
            ).limit(limit)
            
            return stmt.all()
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close() 