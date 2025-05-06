"""
Constraint Satisfaction Problem (CSP) Scheduler
Triển khai thuật toán CSP cho việc lập lịch ca làm việc tự động
"""

import random
from datetime import datetime, timedelta, time
from collections import defaultdict

# Định nghĩa các ca làm việc chuẩn
STANDARD_SHIFTS = [
    {"name": "Ca sáng", "start_hour": 8, "start_minute": 0, "end_hour": 14, "end_minute": 0},
    {"name": "Ca chiều", "start_hour": 14, "start_minute": 0, "end_hour": 20, "end_minute": 0},
    {"name": "Ca tối", "start_hour": 16, "start_minute": 0, "end_hour": 22, "end_minute": 0},
    {"name": "Ca toàn thời gian", "start_hour": 8, "start_minute": 0, "end_hour": 17, "end_minute": 0},
]

class StaffShiftCSP:
    """
    Giải quyết bài toán lập lịch ca làm việc sử dụng CSP
    """
    
    def __init__(self, staff_list, week_start_date, min_staff_per_day=2, max_shifts_per_week=5):
        """
        Khởi tạo bài toán CSP
        
        Args:
            staff_list: Danh sách nhân viên
            week_start_date: Ngày bắt đầu tuần
            min_staff_per_day: Số nhân viên tối thiểu mỗi ngày
            max_shifts_per_week: Số ca tối đa mỗi nhân viên một tuần
        """
        self.staff_list = staff_list
        self.week_start_date = week_start_date
        self.min_staff_per_day = min_staff_per_day
        self.max_shifts_per_week = max_shifts_per_week
        self.days = 7  # Số ngày trong tuần
        self.shifts = STANDARD_SHIFTS  # Các ca chuẩn
        
        # Khởi tạo các biến domain và assignment
        self.variables = [(staff.id, day, shift_idx) 
                          for staff in staff_list 
                          for day in range(self.days)
                          for shift_idx in range(len(self.shifts))]
        
        self.domains = {var: [0, 1] for var in self.variables}  # 0: không làm, 1: làm
        self.assignment = {}
    
    def is_consistent(self, var, value):
        """
        Kiểm tra xem giá trị có thỏa mãn các ràng buộc không
        
        Args:
            var: Biến (staff_id, day, shift_idx)
            value: Giá trị (0 hoặc 1)
            
        Returns:
            bool: True nếu thỏa mãn ràng buộc, False nếu không
        """
        if value == 0:  # Nếu không làm việc, luôn thỏa mãn
            return True
        
        staff_id, day, shift_idx = var
        
        # Kiểm tra xem nhân viên đã được phân công ca này chưa
        if var in self.assignment and self.assignment[var] == 1:
            return False
            
        # Kiểm tra xem nhân viên có bị trùng ca trong cùng ngày không
        for other_shift_idx in range(len(self.shifts)):
            if other_shift_idx != shift_idx:
                other_var = (staff_id, day, other_shift_idx)
                if other_var in self.assignment and self.assignment[other_var] == 1:
                    # Kiểm tra xem ca có bị chồng chéo không
                    if self._shifts_overlap(shift_idx, other_shift_idx):
                        return False
        
        # Kiểm tra số ca làm việc tối đa trong tuần
        if self._count_weekly_shifts(staff_id) >= self.max_shifts_per_week:
            return False
        
        # Kiểm tra nhân viên không làm hai ngày liên tiếp với ca tối và ca sáng
        if shift_idx == 2:  # Ca tối
            next_day_morning = (staff_id, (day + 1) % self.days, 0)  # Ca sáng ngày kế
            if next_day_morning in self.assignment and self.assignment[next_day_morning] == 1:
                return False
        
        return True
    
    def _shifts_overlap(self, shift1_idx, shift2_idx):
        """Kiểm tra hai ca làm việc có chồng chéo nhau không"""
        shift1 = self.shifts[shift1_idx]
        shift2 = self.shifts[shift2_idx]
        
        start1 = time(shift1["start_hour"], shift1["start_minute"])
        end1 = time(shift1["end_hour"], shift1["end_minute"])
        start2 = time(shift2["start_hour"], shift2["start_minute"])
        end2 = time(shift2["end_hour"], shift2["end_minute"])
        
        return (start1 <= start2 < end1) or (start1 < end2 <= end1) or (start2 <= start1 < end2)
    
    def _count_weekly_shifts(self, staff_id):
        """Đếm số ca làm việc của nhân viên trong tuần hiện tại"""
        count = 0
        for day in range(self.days):
            for shift_idx in range(len(self.shifts)):
                var = (staff_id, day, shift_idx)
                if var in self.assignment and self.assignment[var] == 1:
                    count += 1
        return count
    
    def verify_min_staff_constraint(self):
        """Kiểm tra ràng buộc số nhân viên tối thiểu mỗi ngày"""
        daily_counts = defaultdict(int)
        
        for var, value in self.assignment.items():
            if value == 1:
                staff_id, day, shift_idx = var
                daily_counts[day] += 1
        
        for day in range(self.days):
            if daily_counts[day] < self.min_staff_per_day:
                return False
        
        return True
    
    def backtracking_search(self):
        """Thuật toán Backtracking Search để giải bài toán CSP"""
        return self._backtrack({})
    
    def _backtrack(self, assignment):
        """
        Thuật toán backtracking với forward checking
        
        Args:
            assignment: Assignment hiện tại
            
        Returns:
            dict: Assignment đầy đủ hoặc None nếu không tìm được
        """
        self.assignment = assignment
        
        # Nếu assignment đầy đủ
        if len(assignment) == len(self.variables):
            if self.verify_min_staff_constraint():
                return assignment
            return None
        
        # Chọn biến chưa gán giá trị
        unassigned = [var for var in self.variables if var not in assignment]
        var = self._select_unassigned_variable(unassigned)
        
        # Thử các giá trị
        for value in self._order_domain_values(var):
            if self.is_consistent(var, value):
                assignment[var] = value
                
                result = self._backtrack(assignment)
                if result is not None:
                    return result
                
                # Backtrack
                del assignment[var]
        
        return None
    
    def _select_unassigned_variable(self, unassigned_vars):
        """
        Heuristic MRV (Minimum Remaining Values) - chọn biến có ít giá trị hợp lệ nhất
        Kết hợp với degree heuristic cho biến có nhiều ràng buộc nhất
        """
        # Ưu tiên biến tương ứng với ngày có ít nhân viên nhất
        day_counts = defaultdict(int)
        for var in self.assignment:
            if self.assignment[var] == 1:
                _, day, _ = var
                day_counts[day] += 1
        
        # Ưu tiên những ngày có ít nhân viên
        min_day = min(range(self.days), key=lambda d: day_counts.get(d, 0))
        day_vars = [var for var in unassigned_vars if var[1] == min_day]
        
        if day_vars:
            return random.choice(day_vars)
        
        return random.choice(unassigned_vars)
    
    def _order_domain_values(self, var):
        """
        Heuristic LCV (Least Constraining Value) - thử giá trị ít hạn chế nhất trước
        ở đây, 0 (không làm) ít hạn chế hơn 1 (làm), nên thử 0 trước
        """
        staff_id, day, _ = var
        
        # Nếu nhân viên đã làm nhiều ca, ưu tiên không phân công (0)
        if self._count_weekly_shifts(staff_id) >= self.max_shifts_per_week - 1:
            return [0, 1]
        
        # Nếu ngày này đã có đủ nhân viên tối thiểu, ưu tiên không phân công (0)
        day_count = sum(1 for (s, d, _), v in self.assignment.items() 
                        if d == day and v == 1)
        if day_count >= self.min_staff_per_day:
            return [0, 1]
        
        # Ngược lại, ưu tiên phân công (1)
        return [1, 0]
    
    def generate_shifts(self):
        """
        Tạo lịch làm việc cho cả tuần
        
        Returns:
            list: Danh sách ca làm việc [(staff_id, date, start_time, end_time)]
        """
        result = self.backtracking_search()
        if not result:
            return []
        
        shifts = []
        for var, value in result.items():
            if value == 1:  # Nếu được phân công ca này
                staff_id, day, shift_idx = var
                shift = self.shifts[shift_idx]
                
                # Tính toán ngày và giờ làm việc
                shift_date = self.week_start_date + timedelta(days=day)
                
                start_datetime = datetime.combine(
                    shift_date, 
                    time(shift["start_hour"], shift["start_minute"])
                )
                
                end_datetime = datetime.combine(
                    shift_date, 
                    time(shift["end_hour"], shift["end_minute"])
                )
                
                shifts.append({
                    "staff_id": staff_id,
                    "date": shift_date,
                    "start_time": start_datetime,
                    "end_time": end_datetime,
                    "status": "lịch"
                })
        
        return shifts

def generate_optimal_shifts(staff_list, week_start_date, min_staff_per_day=2, max_shifts_per_week=5):
    """
    Hàm tiện ích để tạo lịch làm việc tối ưu
    
    Args:
        staff_list: Danh sách nhân viên
        week_start_date: Ngày bắt đầu tuần
        min_staff_per_day: Số nhân viên tối thiểu mỗi ngày
        max_shifts_per_week: Số ca tối đa mỗi nhân viên một tuần
    
    Returns:
        list: Danh sách ca làm việc hoặc rỗng nếu không tìm được lịch thỏa mãn
    """
    csp = StaffShiftCSP(staff_list, week_start_date, min_staff_per_day, max_shifts_per_week)
    return csp.generate_shifts() 