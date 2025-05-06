from app.database.db_config import get_db
from app.models.models import Table
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

class TableController:
    @staticmethod
    def get_all_tables():
        db = get_db()
        try:
            return db.query(Table).all()
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_available_tables():
        db = get_db()
        try:
            return db.query(Table).filter(Table.status == "trống").all()
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_table_by_id(table_id):
        db = get_db()
        try:
            return db.query(Table).filter(Table.id == table_id).first()
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def update_table_status(table_id, status):
        db = get_db()
        try:
            table = db.query(Table).filter(Table.id == table_id).first()
            if not table:
                return False
            
            table.status = status
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def add_table(name, capacity=4, location=None):
        db = get_db()
        try:
            new_table = Table(
                name=name,
                capacity=capacity,
                location=location,
                status="trống"
            )
            db.add(new_table)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def update_table(table_id, **kwargs):
        db = get_db()
        try:
            table = db.query(Table).filter(Table.id == table_id).first()
            if not table:
                return False
            
            for key, value in kwargs.items():
                if hasattr(table, key):
                    setattr(table, key, value)
            
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def delete_table(table_id):
        db = get_db()
        try:
            table = db.query(Table).filter(Table.id == table_id).first()
            if not table:
                return False
            
            db.delete(table)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False
        finally:
            db.close() 