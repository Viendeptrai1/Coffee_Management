from app.database.db_config import get_db
from app.models.models import Staff
from sqlalchemy.exc import SQLAlchemyError
import hashlib

class StaffController:
    @staticmethod
    def hash_password(password):
        """Hashes the password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def authenticate(username, password):
        """Authenticates a user by username and password"""
        db = get_db()
        try:
            hashed_password = StaffController.hash_password(password)
            staff = db.query(Staff).filter(
                Staff.username == username,
                Staff.password == hashed_password,
                Staff.is_active == True
            ).first()
            
            return staff
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_all_staff():
        db = get_db()
        try:
            return db.query(Staff).filter(Staff.is_active == True).all()
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_staff_by_id(staff_id):
        db = get_db()
        try:
            return db.query(Staff).filter(Staff.id == staff_id).first()
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def add_staff(name, role, username, password, phone=None, email=None, shift=None):
        db = get_db()
        try:
            # Check if username already exists
            existing_staff = db.query(Staff).filter(Staff.username == username).first()
            if existing_staff:
                return False
            
            hashed_password = StaffController.hash_password(password)
            
            new_staff = Staff(
                name=name,
                role=role,
                username=username,
                password=hashed_password,
                phone=phone,
                email=email,
                shift=shift,
                is_active=True
            )
            
            db.add(new_staff)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def update_staff(staff_id, **kwargs):
        db = get_db()
        try:
            staff = db.query(Staff).filter(Staff.id == staff_id).first()
            if not staff:
                return False
            
            # If password is being updated, hash it
            if 'password' in kwargs:
                kwargs['password'] = StaffController.hash_password(kwargs['password'])
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(staff, key):
                    setattr(staff, key, value)
            
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def delete_staff(staff_id):
        db = get_db()
        try:
            staff = db.query(Staff).filter(Staff.id == staff_id).first()
            if not staff:
                return False
            
            # Soft delete
            staff.is_active = False
            
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def change_password(staff_id, old_password, new_password):
        db = get_db()
        try:
            staff = db.query(Staff).filter(Staff.id == staff_id).first()
            if not staff:
                return False
            
            # Verify old password
            if staff.password != StaffController.hash_password(old_password):
                return False
            
            # Update password
            staff.password = StaffController.hash_password(new_password)
            
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False
        finally:
            db.close() 