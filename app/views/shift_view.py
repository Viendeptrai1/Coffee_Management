from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QDialog, QFormLayout, QLineEdit, QComboBox, QMessageBox,
                             QDateEdit, QTimeEdit, QCalendarWidget, QTabWidget, QScrollArea,
                             QGridLayout, QFrame, QSplitter, QMenu, QGroupBox)
from PyQt5.QtCore import Qt, QSize, QDate, QTime, QDateTime
from PyQt5.QtGui import QIcon, QFont, QColor, QBrush

from datetime import datetime, timedelta, time
import calendar

from app.controllers.shift_controller import ShiftController
from app.controllers.staff_controller import StaffController

class WeeklyShiftTable(QTableWidget):
    """Bảng hiển thị ca làm việc theo tuần"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(8)  # 1 cột cho tên NV + 7 ngày trong tuần
        self.setHorizontalHeaderLabels(["Nhân viên", "Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "CN"])
        
        self.setShowGrid(True)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectItems)
        self.setSelectionMode(QTableWidget.SingleSelection)
        
        # Định dạng bảng
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for i in range(1, 8):
            self.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
        
        self.week_start_date = self._get_current_week_start()
        self.shifts = []
        self.staffs = []
        
        # Kết nối sự kiện khi click chuột phải
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def _get_current_week_start(self):
        today = datetime.now().date()
        return today - timedelta(days=today.weekday())
    
    def set_week(self, week_start_date):
        self.week_start_date = week_start_date
        self.update_table()
    
    def next_week(self):
        self.week_start_date += timedelta(days=7)
        self.update_table()
    
    def prev_week(self):
        self.week_start_date -= timedelta(days=7)
        self.update_table()
    
    def this_week(self):
        self.week_start_date = self._get_current_week_start()
        self.update_table()
    
    def update_table(self):
        self.clearContents()
        
        # Cập nhật tiêu đề cột với ngày tương ứng
        weekday_names = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "CN"]
        for i in range(7):
            date = self.week_start_date + timedelta(days=i)
            date_str = date.strftime("%d/%m")
            self.setHorizontalHeaderItem(i + 1, QTableWidgetItem(f"{weekday_names[i]}\n{date_str}"))
        
        # Lấy tất cả nhân viên
        self.staffs = StaffController.get_all_staff()
        self.setRowCount(len(self.staffs))
        
        # Thêm tên nhân viên vào cột đầu tiên
        for row, staff in enumerate(self.staffs):
            self.setItem(row, 0, QTableWidgetItem(staff.name))
            
            # Set màu nền cho các ô
            for col in range(1, 8):
                empty_item = QTableWidgetItem("")
                empty_item.setBackground(QColor("#f5f5f5"))
                self.setItem(row, col, empty_item)
        
        # Lấy ca làm việc trong tuần
        self.shifts = ShiftController.get_shifts_by_week(self.week_start_date)
        
        # Hiển thị ca làm việc trong bảng
        for shift in self.shifts:
            # Tìm nhân viên tương ứng
            staff_row = -1
            for row, staff in enumerate(self.staffs):
                if staff.id == shift.staff_id:
                    staff_row = row
                    break
            
            if staff_row == -1:
                continue
            
            # Xác định cột tương ứng với ngày của ca làm việc
            shift_date = shift.date
            # Chuyển đổi shift_date về date nếu nó là datetime
            if isinstance(shift_date, datetime):
                shift_date = shift_date.date()
            
            day_diff = (shift_date - self.week_start_date).days
            
            if 0 <= day_diff < 7:
                col = day_diff + 1
                
                # Định dạng hiển thị giờ làm việc
                start_time_str = shift.start_time.strftime("%H:%M")
                end_time_str = shift.end_time.strftime("%H:%M")
                shift_text = f"{start_time_str} - {end_time_str}"
                
                # Set item với thông tin ca làm việc
                shift_item = QTableWidgetItem(shift_text)
                
                # Màu sắc theo trạng thái ca làm việc
                if shift.status == "đã làm":
                    shift_item.setBackground(QColor("#e6f7ff"))  # Màu xanh nhạt
                elif shift.status == "đang làm":
                    shift_item.setBackground(QColor("#d4edda"))  # Màu xanh lá nhạt
                elif shift.status == "vắng":
                    shift_item.setBackground(QColor("#f8d7da"))  # Màu đỏ nhạt
                else:  # Mặc định - lịch
                    shift_item.setBackground(QColor("#fff3cd"))  # Màu vàng nhạt
                
                # Lưu thông tin shift để sử dụng trong context menu
                shift_item.setData(Qt.UserRole, shift.id)
                
                self.setItem(staff_row, col, shift_item)
    
    def show_context_menu(self, position):
        item = self.itemAt(position)
        if not item:
            return
        
        # Lấy thông tin về ô được chọn
        row = item.row()
        col = item.column()
        
        # Nếu click vào ô nhân viên (cột 0), không làm gì
        if col == 0:
            return
        
        # Tạo menu
        context_menu = QMenu(self)
        
        # Lấy thông tin ngày từ cột
        day_offset = col - 1
        shift_date = self.week_start_date + timedelta(days=day_offset)
        
        # Lấy thông tin nhân viên từ hàng
        staff = self.staffs[row]
        
        # Kiểm tra xem ô có ca làm việc không
        shift_id = item.data(Qt.UserRole) if item.data(Qt.UserRole) else None
        
        if shift_id:  # Đã có ca làm việc
            # Tìm shift trong danh sách
            shift = next((s for s in self.shifts if s.id == shift_id), None)
            
            if shift:
                # Menu cho ca làm việc đã tồn tại
                edit_action = context_menu.addAction("Chỉnh sửa ca làm việc")
                mark_action = context_menu.addAction("Đánh dấu trạng thái")
                delete_action = context_menu.addAction("Xóa ca làm việc")
                
                # Tạo sub-menu cho đánh dấu trạng thái
                status_menu = QMenu("Đánh dấu trạng thái", self)
                scheduled_action = status_menu.addAction("Lịch")
                working_action = status_menu.addAction("Đang làm")
                done_action = status_menu.addAction("Đã làm")
                absent_action = status_menu.addAction("Vắng")
                
                mark_action.setMenu(status_menu)
                
                # Thực hiện hành động khi chọn
                action = context_menu.exec_(self.mapToGlobal(position))
                
                if action == edit_action:
                    self.show_edit_shift_dialog(shift, staff)
                elif action == delete_action:
                    self.delete_shift(shift)
                elif action == scheduled_action:
                    self.update_shift_status(shift, "lịch")
                elif action == working_action:
                    self.update_shift_status(shift, "đang làm")
                elif action == done_action:
                    self.update_shift_status(shift, "đã làm")
                elif action == absent_action:
                    self.update_shift_status(shift, "vắng")
        else:  # Chưa có ca làm việc
            add_action = context_menu.addAction("Thêm ca làm việc")
            
            action = context_menu.exec_(self.mapToGlobal(position))
            
            if action == add_action:
                self.show_add_shift_dialog(staff, shift_date)
    
    def show_add_shift_dialog(self, staff, shift_date):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Thêm ca làm việc cho {staff.name}")
        dialog.setFixedWidth(350)
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        
        # Ngày
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate(shift_date.year, shift_date.month, shift_date.day))
        form_layout.addRow("Ngày:", date_edit)
        
        # Giờ bắt đầu
        start_time_edit = QTimeEdit()
        start_time_edit.setTime(QTime(8, 0))  # Mặc định 8:00 AM
        form_layout.addRow("Giờ bắt đầu:", start_time_edit)
        
        # Giờ kết thúc
        end_time_edit = QTimeEdit()
        end_time_edit.setTime(QTime(17, 0))  # Mặc định 5:00 PM
        form_layout.addRow("Giờ kết thúc:", end_time_edit)
        
        # Trạng thái
        status_combo = QComboBox()
        status_combo.addItems(["lịch", "đang làm", "đã làm", "vắng"])
        form_layout.addRow("Trạng thái:", status_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Hủy")
        cancel_button.clicked.connect(dialog.reject)
        
        save_button = QPushButton("Lưu")
        save_button.setStyleSheet("background-color: #4CAF50; color: white;")
        save_button.clicked.connect(dialog.accept)
        
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)
        
        layout.addLayout(buttons_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            # Lấy thông tin từ dialog
            selected_date = date_edit.date().toPyDate()
            
            start_time_qtime = start_time_edit.time()
            start_datetime = datetime.combine(
                selected_date, 
                time(start_time_qtime.hour(), start_time_qtime.minute())
            )
            
            end_time_qtime = end_time_edit.time()
            end_datetime = datetime.combine(
                selected_date, 
                time(end_time_qtime.hour(), end_time_qtime.minute())
            )
            
            status = status_combo.currentText()
            
            # Kiểm tra thời gian hợp lệ
            if start_datetime >= end_datetime:
                QMessageBox.warning(self, "Lỗi", "Thời gian bắt đầu phải trước thời gian kết thúc")
                return
            
            # Thêm ca làm việc
            success, message = ShiftController.add_shift(
                staff_id=staff.id,
                date=selected_date,
                start_time=start_datetime,
                end_time=end_datetime,
                status=status
            )
            
            if success:
                QMessageBox.information(self, "Thành công", message)
                self.update_table()
            else:
                QMessageBox.warning(self, "Lỗi", message)
    
    def show_edit_shift_dialog(self, shift, staff):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Chỉnh sửa ca làm việc của {staff.name}")
        dialog.setFixedWidth(350)
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        
        # Ngày
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate(shift.date.year, shift.date.month, shift.date.day))
        form_layout.addRow("Ngày:", date_edit)
        
        # Giờ bắt đầu
        start_time_edit = QTimeEdit()
        start_time_edit.setTime(QTime(shift.start_time.hour, shift.start_time.minute))
        form_layout.addRow("Giờ bắt đầu:", start_time_edit)
        
        # Giờ kết thúc
        end_time_edit = QTimeEdit()
        end_time_edit.setTime(QTime(shift.end_time.hour, shift.end_time.minute))
        form_layout.addRow("Giờ kết thúc:", end_time_edit)
        
        # Trạng thái
        status_combo = QComboBox()
        status_combo.addItems(["lịch", "đang làm", "đã làm", "vắng"])
        status_combo.setCurrentText(shift.status)
        form_layout.addRow("Trạng thái:", status_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Hủy")
        cancel_button.clicked.connect(dialog.reject)
        
        save_button = QPushButton("Lưu")
        save_button.setStyleSheet("background-color: #4CAF50; color: white;")
        save_button.clicked.connect(dialog.accept)
        
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)
        
        layout.addLayout(buttons_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            # Lấy thông tin từ dialog
            selected_date = date_edit.date().toPyDate()
            
            start_time_qtime = start_time_edit.time()
            start_datetime = datetime.combine(
                selected_date, 
                time(start_time_qtime.hour(), start_time_qtime.minute())
            )
            
            end_time_qtime = end_time_edit.time()
            end_datetime = datetime.combine(
                selected_date, 
                time(end_time_qtime.hour(), end_time_qtime.minute())
            )
            
            status = status_combo.currentText()
            
            # Kiểm tra thời gian hợp lệ
            if start_datetime >= end_datetime:
                QMessageBox.warning(self, "Lỗi", "Thời gian bắt đầu phải trước thời gian kết thúc")
                return
            
            # Cập nhật ca làm việc
            success, message = ShiftController.update_shift(
                shift_id=shift.id,
                date=selected_date,
                start_time=start_datetime,
                end_time=end_datetime,
                status=status
            )
            
            if success:
                QMessageBox.information(self, "Thành công", message)
                self.update_table()
            else:
                QMessageBox.warning(self, "Lỗi", message)
    
    def delete_shift(self, shift):
        reply = QMessageBox.question(
            self, 
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa ca làm việc này?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success, message = ShiftController.delete_shift(shift.id)
            
            if success:
                QMessageBox.information(self, "Thành công", message)
                self.update_table()
            else:
                QMessageBox.warning(self, "Lỗi", message)
    
    def update_shift_status(self, shift, status):
        success, message = ShiftController.update_shift(shift.id, status=status)
        
        if success:
            QMessageBox.information(self, "Thành công", f"Đã cập nhật trạng thái thành '{status}'")
            self.update_table()
        else:
            QMessageBox.warning(self, "Lỗi", message)


class ShiftView(QWidget):
    def __init__(self, current_staff=None):
        super().__init__()
        
        self.current_staff = current_staff
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("QUẢN LÝ CA LÀM VIỆC")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        
        # Năm - Tháng
        date_nav_layout = QHBoxLayout()
        
        self.prev_week_btn = QPushButton("◀")
        self.prev_week_btn.setFixedSize(30, 30)
        self.prev_week_btn.clicked.connect(self.prev_week)
        
        self.current_week_label = QLabel()
        self.current_week_label.setAlignment(Qt.AlignCenter)
        self.current_week_label.setFont(QFont("Arial", 12))
        
        self.next_week_btn = QPushButton("▶")
        self.next_week_btn.setFixedSize(30, 30)
        self.next_week_btn.clicked.connect(self.next_week)
        
        self.today_btn = QPushButton("Tuần này")
        self.today_btn.setFixedSize(80, 30)
        self.today_btn.clicked.connect(self.this_week)
        
        date_nav_layout.addWidget(self.prev_week_btn)
        date_nav_layout.addWidget(self.current_week_label)
        date_nav_layout.addWidget(self.next_week_btn)
        date_nav_layout.addWidget(self.today_btn)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addLayout(date_nav_layout)
        
        # Add header to main layout
        main_layout.addLayout(header_layout)
        
        # Weekly shift table
        self.shift_table = WeeklyShiftTable()
        main_layout.addWidget(self.shift_table)
        
        # Update week label
        self.update_week_label()
    
    def update_week_label(self):
        week_start = self.shift_table.week_start_date
        week_end = week_start + timedelta(days=6)
        
        week_start_str = week_start.strftime("%d/%m/%Y")
        week_end_str = week_end.strftime("%d/%m/%Y")
        
        self.current_week_label.setText(f"{week_start_str} - {week_end_str}")
    
    def prev_week(self):
        self.shift_table.prev_week()
        self.update_week_label()
    
    def next_week(self):
        self.shift_table.next_week()
        self.update_week_label()
    
    def this_week(self):
        self.shift_table.this_week()
        self.update_week_label()
    
    def refresh(self):
        self.shift_table.update_table()
        self.update_week_label() 