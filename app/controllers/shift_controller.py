from app.database.db_config import get_db
from app.models.models import Shift, Staff
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_
from datetime import datetime, timedelta

class ShiftController:
    @staticmethod
    def get_all_shifts():
        db = get_db()
        try:
            return db.query(Shift).order_by(Shift.date.desc(), Shift.start_time.desc()).all()
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_shifts_by_staff(staff_id):
        db = get_db()
        try:
            return db.query(Shift).filter(Shift.staff_id == staff_id).order_by(Shift.date.desc(), Shift.start_time.desc()).all()
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_shifts_by_date_range(start_date, end_date):
        db = get_db()
        try:
            return db.query(Shift).filter(
                Shift.date >= start_date,
                Shift.date <= end_date
            ).order_by(Shift.date, Shift.start_time).all()
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_shifts_by_week(week_start_date=None):
        if week_start_date is None:
            # Lấy ngày đầu tiên của tuần hiện tại (thứ Hai)
            today = datetime.now().date()
            week_start_date = today - timedelta(days=today.weekday())
        
        week_end_date = week_start_date + timedelta(days=6)
        
        return ShiftController.get_shifts_by_date_range(week_start_date, week_end_date)
    
    @staticmethod
    def add_shift(staff_id, date, start_time, end_time, status="lịch"):
        db = get_db()
        try:
            # Kiểm tra xem nhân viên có tồn tại không
            staff = db.query(Staff).filter(Staff.id == staff_id).first()
            if not staff:
                return False, "Nhân viên không tồn tại"
            
            # Kiểm tra xem ca làm việc có bị trùng không
            existing_shift = db.query(Shift).filter(
                and_(
                    Shift.staff_id == staff_id,
                    Shift.date == date,
                    or_(
                        and_(Shift.start_time <= start_time, Shift.end_time > start_time),
                        and_(Shift.start_time < end_time, Shift.end_time >= end_time),
                        and_(Shift.start_time >= start_time, Shift.end_time <= end_time)
                    )
                )
            ).first()
            
            if existing_shift:
                return False, "Nhân viên đã có ca làm việc trong khoảng thời gian này"
            
            new_shift = Shift(
                staff_id=staff_id,
                date=date,
                start_time=start_time,
                end_time=end_time,
                status=status
            )
            
            db.add(new_shift)
            db.commit()
            return True, "Đã thêm ca làm việc thành công"
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False, f"Lỗi cơ sở dữ liệu: {e}"
        finally:
            db.close()
    
    @staticmethod
    def update_shift(shift_id, **kwargs):
        db = get_db()
        try:
            shift = db.query(Shift).filter(Shift.id == shift_id).first()
            if not shift:
                return False, "Ca làm việc không tồn tại"
            
            # Kiểm tra xem có bị trùng ca không nếu thay đổi thời gian
            if ('start_time' in kwargs or 'end_time' in kwargs or 'date' in kwargs) and 'staff_id' in kwargs:
                start_time = kwargs.get('start_time', shift.start_time)
                end_time = kwargs.get('end_time', shift.end_time)
                date = kwargs.get('date', shift.date)
                staff_id = kwargs.get('staff_id', shift.staff_id)
                
                existing_shift = db.query(Shift).filter(
                    and_(
                        Shift.staff_id == staff_id,
                        Shift.date == date,
                        or_(
                            and_(Shift.start_time <= start_time, Shift.end_time > start_time),
                            and_(Shift.start_time < end_time, Shift.end_time >= end_time),
                            and_(Shift.start_time >= start_time, Shift.end_time <= end_time)
                        ),
                        Shift.id != shift_id  # Loại trừ chính nó
                    )
                ).first()
                
                if existing_shift:
                    return False, "Nhân viên đã có ca làm việc trong khoảng thời gian này"
            
            # Cập nhật các trường
            for key, value in kwargs.items():
                if hasattr(shift, key):
                    setattr(shift, key, value)
            
            db.commit()
            return True, "Đã cập nhật ca làm việc thành công"
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False, f"Lỗi cơ sở dữ liệu: {e}"
        finally:
            db.close()
    
    @staticmethod
    def delete_shift(shift_id):
        db = get_db()
        try:
            shift = db.query(Shift).filter(Shift.id == shift_id).first()
            if not shift:
                return False, "Ca làm việc không tồn tại"
            
            db.delete(shift)
            db.commit()
            return True, "Đã xóa ca làm việc thành công"
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False, f"Lỗi cơ sở dữ liệu: {e}"
        finally:
            db.close()
    
    @staticmethod
    def get_current_shifts():
        """Lấy các ca đang diễn ra"""
        now = datetime.now()
        current_date = now.date()
        
        db = get_db()
        try:
            return db.query(Shift).filter(
                Shift.date == current_date,
                Shift.start_time <= now,
                Shift.end_time >= now
            ).all()
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close() 