from app.database.db_config import get_db
from app.models.models import Shift, Staff
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_
from datetime import datetime, timedelta

from app.utils.csp_scheduler import generate_optimal_shifts

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
    
    @staticmethod
    def generate_automatic_schedule(week_start_date, min_staff_per_day=2, max_shifts_per_week=5):
        """
        Tạo lịch làm việc tự động sử dụng thuật toán CSP
        
        Args:
            week_start_date: Ngày bắt đầu tuần
            min_staff_per_day: Số nhân viên tối thiểu mỗi ngày
            max_shifts_per_week: Số ca tối đa mỗi nhân viên một tuần
            
        Returns:
            tuple: (success, message)
        """
        db = get_db()
        try:
            # Lấy danh sách nhân viên đang hoạt động
            staff_list = db.query(Staff).filter(Staff.is_active == True).all()
            
            if not staff_list:
                return False, "Không có nhân viên nào đang hoạt động"
            
            # Xóa tất cả ca làm việc đã có trong tuần này
            week_end_date = week_start_date + timedelta(days=6)
            existing_shifts = db.query(Shift).filter(
                Shift.date >= week_start_date,
                Shift.date <= week_end_date
            ).all()
            
            for shift in existing_shifts:
                db.delete(shift)
            
            # Tạo lịch tự động bằng thuật toán CSP
            optimal_shifts = generate_optimal_shifts(
                staff_list,
                week_start_date,
                min_staff_per_day,
                max_shifts_per_week
            )
            
            if not optimal_shifts:
                return False, "Không thể tạo lịch làm việc thỏa mãn tất cả ràng buộc"
            
            # Lưu lịch làm việc vào cơ sở dữ liệu
            for shift_data in optimal_shifts:
                new_shift = Shift(
                    staff_id=shift_data["staff_id"],
                    date=shift_data["date"],
                    start_time=shift_data["start_time"],
                    end_time=shift_data["end_time"],
                    status=shift_data["status"]
                )
                db.add(new_shift)
            
            db.commit()
            return True, f"Đã tạo {len(optimal_shifts)} ca làm việc tự động"
            
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {e}")
            return False, f"Lỗi cơ sở dữ liệu: {e}"
        finally:
            db.close()
    
    @staticmethod
    def get_staff_workload(week_start_date=None):
        """
        Tính toán khối lượng công việc của nhân viên trong tuần
        
        Args:
            week_start_date: Ngày bắt đầu tuần, mặc định là tuần hiện tại
            
        Returns:
            list: Danh sách [{'staff_id': id, 'staff_name': name, 'shift_count': count, 'total_hours': hours}]
        """
        if week_start_date is None:
            today = datetime.now().date()
            week_start_date = today - timedelta(days=today.weekday())
        
        week_end_date = week_start_date + timedelta(days=6)
        
        db = get_db()
        try:
            # Lấy danh sách ca làm việc trong tuần
            shifts = db.query(Shift).filter(
                Shift.date >= week_start_date,
                Shift.date <= week_end_date
            ).all()
            
            # Lấy danh sách nhân viên
            staffs = db.query(Staff).filter(Staff.is_active == True).all()
            
            # Tính toán khối lượng công việc cho từng nhân viên
            workloads = []
            for staff in staffs:
                staff_shifts = [s for s in shifts if s.staff_id == staff.id]
                shift_count = len(staff_shifts)
                
                # Tính tổng số giờ làm việc
                total_hours = 0
                for shift in staff_shifts:
                    hours = (shift.end_time - shift.start_time).total_seconds() / 3600
                    total_hours += hours
                
                workloads.append({
                    'staff_id': staff.id,
                    'staff_name': staff.name,
                    'shift_count': shift_count,
                    'total_hours': round(total_hours, 1)
                })
            
            # Sắp xếp theo khối lượng công việc giảm dần
            workloads.sort(key=lambda x: x['total_hours'], reverse=True)
            
            return workloads
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []
        finally:
            db.close() 