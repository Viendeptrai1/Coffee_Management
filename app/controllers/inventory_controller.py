from app.database.db_config import get_db
from app.models.models import Inventory, MenuItem, Recipe
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from sqlalchemy import func

class InventoryController:
    @staticmethod
    def get_all_inventory_items():
        """Lấy tất cả các mục trong kho"""
        db = get_db()
        try:
            return db.query(Inventory).all()
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_inventory_item(inventory_id):
        """Lấy thông tin một mục trong kho dựa trên ID"""
        db = get_db()
        try:
            return db.query(Inventory).filter(Inventory.id == inventory_id).first()
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def add_inventory_item(name, quantity, unit, supplier=None, min_quantity=0):
        """Thêm một mục mới vào kho"""
        db = get_db()
        try:
            new_item = Inventory(
                name=name,
                quantity=quantity,
                unit=unit,
                supplier=supplier,
                min_quantity=min_quantity,
                last_update=datetime.now()
            )
            db.add(new_item)
            db.commit()
            db.refresh(new_item)
            return new_item.id
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def update_inventory_item(inventory_id, name=None, quantity=None, unit=None, supplier=None, min_quantity=None):
        """Cập nhật thông tin đầy đủ của một mục trong kho"""
        db = get_db()
        try:
            item = db.query(Inventory).filter(Inventory.id == inventory_id).first()
            if not item:
                return False
            
            if name:
                item.name = name
            if quantity is not None:
                item.quantity = quantity
            if unit:
                item.unit = unit
            if supplier is not None:
                item.supplier = supplier
            if min_quantity is not None:
                item.min_quantity = min_quantity
                
            item.last_update = datetime.now()
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def delete_inventory_item(inventory_id):
        """Xóa một mục khỏi kho"""
        db = get_db()
        try:
            item = db.query(Inventory).filter(Inventory.id == inventory_id).first()
            if not item:
                return False
            
            db.delete(item)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def get_low_stock_items():
        """Lấy danh sách các mục đang sắp hết hàng"""
        db = get_db()
        try:
            return db.query(Inventory).filter(
                Inventory.quantity <= Inventory.min_quantity
            ).all()
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def calculate_required_ingredients(menu_item_id, quantity=1):
        """Tính toán số lượng nguyên liệu cần dùng cho một món sử dụng bảng Recipe"""
        db = get_db()
        try:
            # Lấy tất cả nguyên liệu theo công thức
            recipes = db.query(Recipe, Inventory).join(
                Inventory, Recipe.inventory_id == Inventory.id
            ).filter(
                Recipe.menu_item_id == menu_item_id
            ).all()
            
            if not recipes:
                # Nếu không có công thức, trả về dữ liệu mẫu
                return [
                    {"name": "Cà phê", "quantity": 10 * quantity, "unit": "g"},
                    {"name": "Sữa", "quantity": 100 * quantity, "unit": "ml"},
                    {"name": "Đường", "quantity": 5 * quantity, "unit": "g"}
                ]
            
            result = []
            for recipe, inventory in recipes:
                result.append({
                    "name": inventory.name,
                    "quantity": recipe.quantity * quantity,
                    "unit": inventory.unit
                })
            
            return result
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def add_recipe_ingredient(menu_item_id, inventory_id, quantity):
        """Thêm một nguyên liệu vào công thức của món"""
        db = get_db()
        try:
            # Kiểm tra xem đã có nguyên liệu này trong công thức chưa
            existing = db.query(Recipe).filter(
                Recipe.menu_item_id == menu_item_id,
                Recipe.inventory_id == inventory_id
            ).first()
            
            if existing:
                # Nếu đã tồn tại, cập nhật số lượng
                existing.quantity = quantity
            else:
                # Nếu chưa có, tạo mới
                new_recipe = Recipe(
                    menu_item_id=menu_item_id,
                    inventory_id=inventory_id,
                    quantity=quantity
                )
                db.add(new_recipe)
            
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def remove_recipe_ingredient(menu_item_id, inventory_id):
        """Xóa một nguyên liệu khỏi công thức của món"""
        db = get_db()
        try:
            recipe = db.query(Recipe).filter(
                Recipe.menu_item_id == menu_item_id,
                Recipe.inventory_id == inventory_id
            ).first()
            
            if recipe:
                db.delete(recipe)
                db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def get_recipe(menu_item_id):
        """Lấy công thức của một món"""
        db = get_db()
        try:
            recipes = db.query(Recipe, Inventory).join(
                Inventory, Recipe.inventory_id == Inventory.id
            ).filter(
                Recipe.menu_item_id == menu_item_id
            ).all()
            
            result = []
            for recipe, inventory in recipes:
                result.append({
                    "id": recipe.id,
                    "inventory_id": inventory.id,
                    "name": inventory.name,
                    "quantity": recipe.quantity,
                    "unit": inventory.unit
                })
            
            return result
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def check_ingredients_availability(menu_item_id, quantity=1):
        """Kiểm tra xem có đủ nguyên liệu để làm món không"""
        required = InventoryController.calculate_required_ingredients(menu_item_id, quantity)
        
        db = get_db()
        try:
            for item in required:
                inventory = db.query(Inventory).filter(Inventory.name == item["name"]).first()
                if not inventory or inventory.quantity < item["quantity"]:
                    return {
                        "available": False,
                        "missing": item["name"],
                        "required": item["quantity"],
                        "available_quantity": inventory.quantity if inventory else 0
                    }
            
            return {"available": True}
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return {"available": False, "error": str(e)}
        finally:
            db.close()
    
    @staticmethod
    def update_stock_after_order(order_id):
        """Cập nhật kho sau khi có đơn hàng mới"""
        from app.models.models import OrderItem
        
        db = get_db()
        try:
            # Lấy tất cả món trong đơn hàng
            order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
            
            for order_item in order_items:
                menu_item_id = order_item.menu_item_id
                quantity = order_item.quantity
                
                # Lấy công thức của món
                required = InventoryController.calculate_required_ingredients(menu_item_id, quantity)
                
                # Giảm số lượng nguyên liệu
                for item in required:
                    inventory = db.query(Inventory).filter(Inventory.name == item["name"]).first()
                    if inventory:
                        inventory.quantity -= item["quantity"]
                        inventory.last_update = datetime.now()
            
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def update_inventory_quantity(inventory_id, new_quantity):
        """Cập nhật số lượng của một mục trong kho"""
        db = get_db()
        try:
            item = db.query(Inventory).filter(Inventory.id == inventory_id).first()
            if not item:
                return False
            
            item.quantity = new_quantity
            item.last_update = datetime.now()
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False
        finally:
            db.close() 