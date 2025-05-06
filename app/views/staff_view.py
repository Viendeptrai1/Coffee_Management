from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QDialog, QFormLayout, QLineEdit, QComboBox, QMessageBox,
                             QCheckBox, QGroupBox, QSpinBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QColor

from app.controllers.staff_controller import StaffController

class StaffView(QWidget):
    def __init__(self, current_staff=None):
        super().__init__()
        
        self.current_staff = current_staff
        self.staffs = []
        
        self.setup_ui()
        self.load_staff()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("QUẢN LÝ NHÂN VIÊN")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        
        refresh_button = QPushButton("Làm mới")
        refresh_button.setFixedSize(100, 30)
        refresh_button.clicked.connect(self.load_staff)
        
        add_staff_button = QPushButton("Thêm nhân viên")
        add_staff_button.setFixedSize(120, 30)
        add_staff_button.clicked.connect(self.show_add_staff_dialog)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(refresh_button)
        header_layout.addWidget(add_staff_button)
        
        main_layout.addLayout(header_layout)
        
        # Staff table
        self.staff_table = QTableWidget()
        self.staff_table.setColumnCount(6)
        self.staff_table.setHorizontalHeaderLabels(["ID", "Tên nhân viên", "Chức vụ", "SĐT", "Email", "Trạng thái"])
        self.staff_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.staff_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.staff_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.staff_table.verticalHeader().setVisible(False)
        self.staff_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.staff_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.staff_table.doubleClicked.connect(self.on_staff_double_clicked)
        
        main_layout.addWidget(self.staff_table)
    
    def load_staff(self):
        # Clear existing staff
        self.staff_table.setRowCount(0)
        
        # Get staff from database
        self.staffs = StaffController.get_all_staff()
        
        # Add staff to table
        for row, staff in enumerate(self.staffs):
            self.staff_table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(staff.id))
            self.staff_table.setItem(row, 0, id_item)
            
            # Name
            name_item = QTableWidgetItem(staff.name)
            self.staff_table.setItem(row, 1, name_item)
            
            # Role
            role_item = QTableWidgetItem(staff.role)
            self.staff_table.setItem(row, 2, role_item)
            
            # Phone
            phone_item = QTableWidgetItem(staff.phone or "--")
            self.staff_table.setItem(row, 3, phone_item)
            
            # Email
            email_item = QTableWidgetItem(staff.email or "--")
            self.staff_table.setItem(row, 4, email_item)
            
            # Status
            status_text = "Hoạt động" if staff.is_active else "Không hoạt động"
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(QColor("#4CAF50") if staff.is_active else QColor("#f44336"))
            self.staff_table.setItem(row, 5, status_item)
    
    def on_staff_double_clicked(self, index):
        row = index.row()
        staff_id = int(self.staff_table.item(row, 0).text())
        
        # Find the staff in our list
        selected_staff = next((staff for staff in self.staffs if staff.id == staff_id), None)
        
        if selected_staff:
            self.show_edit_staff_dialog(selected_staff)
    
    def show_add_staff_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Thêm nhân viên mới")
        dialog.setFixedWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        
        # Name
        name_input = QLineEdit()
        name_input.setPlaceholderText("Nhập tên nhân viên")
        form_layout.addRow("Tên nhân viên:", name_input)
        
        # Role
        role_combo = QComboBox()
        role_combo.addItems(["Quản lý", "Phục vụ", "Pha chế", "Thu ngân"])
        form_layout.addRow("Chức vụ:", role_combo)
        
        # Phone
        phone_input = QLineEdit()
        phone_input.setPlaceholderText("Nhập số điện thoại")
        form_layout.addRow("SĐT:", phone_input)
        
        # Email
        email_input = QLineEdit()
        email_input.setPlaceholderText("Nhập email")
        form_layout.addRow("Email:", email_input)
        
        # Username and password
        username_input = QLineEdit()
        username_input.setPlaceholderText("Nhập tên đăng nhập")
        form_layout.addRow("Tên đăng nhập:", username_input)
        
        password_input = QLineEdit()
        password_input.setPlaceholderText("Nhập mật khẩu")
        password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Mật khẩu:", password_input)
        
        # Shift
        shift_combo = QComboBox()
        shift_combo.addItems(["Sáng", "Chiều", "Tối", "Toàn thời gian"])
        form_layout.addRow("Ca làm việc:", shift_combo)
        
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
            name = name_input.text().strip()
            role = role_combo.currentText()
            phone = phone_input.text().strip() or None
            email = email_input.text().strip() or None
            username = username_input.text().strip()
            password = password_input.text().strip()
            shift = shift_combo.currentText()
            
            if not name or not username or not password:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin bắt buộc")
                return
            
            # Add staff
            success = StaffController.add_staff(
                name=name,
                role=role,
                username=username,
                password=password,
                phone=phone,
                email=email,
                shift=shift
            )
            
            if success:
                QMessageBox.information(self, "Thành công", f"Đã thêm nhân viên {name}")
                self.load_staff()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể thêm nhân viên. Có thể tên đăng nhập đã tồn tại.")
    
    def show_edit_staff_dialog(self, staff):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Chỉnh sửa: {staff.name}")
        dialog.setFixedWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        
        # Name
        name_input = QLineEdit(staff.name)
        form_layout.addRow("Tên nhân viên:", name_input)
        
        # Role
        role_combo = QComboBox()
        roles = ["Quản lý", "Phục vụ", "Pha chế", "Thu ngân"]
        role_combo.addItems(roles)
        role_combo.setCurrentText(staff.role)
        form_layout.addRow("Chức vụ:", role_combo)
        
        # Phone
        phone_input = QLineEdit(staff.phone or "")
        form_layout.addRow("SĐT:", phone_input)
        
        # Email
        email_input = QLineEdit(staff.email or "")
        form_layout.addRow("Email:", email_input)
        
        # Username
        username_input = QLineEdit(staff.username)
        username_input.setEnabled(False)  # Cannot change username
        form_layout.addRow("Tên đăng nhập:", username_input)
        
        # Change password checkbox
        change_password_check = QCheckBox("Đổi mật khẩu")
        form_layout.addRow(change_password_check)
        
        # Password
        password_group = QGroupBox("Mật khẩu mới")
        password_group.setEnabled(False)
        password_layout = QFormLayout(password_group)
        
        password_input = QLineEdit()
        password_input.setPlaceholderText("Nhập mật khẩu mới")
        password_input.setEchoMode(QLineEdit.Password)
        password_layout.addRow("Mật khẩu mới:", password_input)
        
        # Enable password fields when checkbox is checked
        change_password_check.stateChanged.connect(lambda state: password_group.setEnabled(state))
        
        form_layout.addRow(password_group)
        
        # Shift
        shift_combo = QComboBox()
        shift_combo.addItems(["Sáng", "Chiều", "Tối", "Toàn thời gian"])
        if staff.shift:
            shift_combo.setCurrentText(staff.shift)
        form_layout.addRow("Ca làm việc:", shift_combo)
        
        # Status
        status_check = QCheckBox("Hoạt động")
        status_check.setChecked(staff.is_active)
        form_layout.addRow("Trạng thái:", status_check)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Hủy")
        cancel_button.clicked.connect(dialog.reject)
        
        save_button = QPushButton("Lưu")
        save_button.setStyleSheet("background-color: #4CAF50; color: white;")
        save_button.clicked.connect(dialog.accept)
        
        delete_button = QPushButton("Xóa")
        delete_button.setStyleSheet("background-color: #f44336; color: white;")
        delete_button.clicked.connect(lambda: self.delete_staff(staff, dialog))
        
        buttons_layout.addWidget(delete_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)
        
        layout.addLayout(buttons_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            name = name_input.text().strip()
            role = role_combo.currentText()
            phone = phone_input.text().strip() or None
            email = email_input.text().strip() or None
            shift = shift_combo.currentText()
            is_active = status_check.isChecked()
            
            if not name:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên nhân viên")
                return
            
            # Prepare data to update
            update_data = {
                'name': name,
                'role': role,
                'phone': phone,
                'email': email,
                'shift': shift,
                'is_active': is_active
            }
            
            # Add password if changed
            if change_password_check.isChecked():
                new_password = password_input.text().strip()
                if not new_password:
                    QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mật khẩu mới")
                    return
                update_data['password'] = new_password
            
            # Update staff
            success = StaffController.update_staff(staff.id, **update_data)
            
            if success:
                QMessageBox.information(self, "Thành công", f"Đã cập nhật thông tin nhân viên {name}")
                self.load_staff()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể cập nhật thông tin nhân viên")
    
    def delete_staff(self, staff, parent_dialog=None):
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa nhân viên '{staff.name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Delete staff (soft delete)
            success = StaffController.delete_staff(staff.id)
            
            if success:
                QMessageBox.information(self, "Thành công", f"Đã xóa nhân viên {staff.name}")
                if parent_dialog:
                    parent_dialog.reject()
                self.load_staff()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể xóa nhân viên") 