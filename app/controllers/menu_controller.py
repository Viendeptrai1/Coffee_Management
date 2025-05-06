from app.database.db_config import get_db
from app.models.models import MenuItem, MenuCategory
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

class MenuController:
    @staticmethod
    def get_all_categories():
        db = get_db()
        try:
            return db.query(MenuCategory).all()
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_items_by_category(category_id):
        db = get_db()
        try:
            # Sử dụng joinedload để tải trước quan hệ category
            return db.query(MenuItem).options(
                joinedload(MenuItem.category)
            ).filter(
                MenuItem.category_id == category_id, 
                MenuItem.is_available == True
            ).all()
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_all_items():
        db = get_db()
        try:
            # Sử dụng joinedload để tải trước quan hệ category
            return db.query(MenuItem).options(
                joinedload(MenuItem.category)
            ).filter(
                MenuItem.is_available == True
            ).all()
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def search_items(keyword):
        db = get_db()
        try:
            # Sử dụng joinedload để tải trước quan hệ category
            return db.query(MenuItem).options(
                joinedload(MenuItem.category)
            ).filter(
                MenuItem.name.ilike(f"%{keyword}%"),
                MenuItem.is_available == True
            ).all()
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def add_item(name, price, category_id, description=None, image_path=None):
        db = get_db()
        try:
            new_item = MenuItem(
                name=name,
                price=price,
                category_id=category_id,
                description=description,
                image_path=image_path
            )
            db.add(new_item)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def update_item(item_id, **kwargs):
        db = get_db()
        try:
            item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
            if not item:
                return False
            
            for key, value in kwargs.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def delete_item(item_id):
        db = get_db()
        try:
            item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
            if not item:
                return False
            
            # Soft delete - just mark as unavailable
            item.is_available = False
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def get_all_menu_items():
        """Alias của get_all_items() để tương thích với code hiện tại"""
        return MenuController.get_all_items() 