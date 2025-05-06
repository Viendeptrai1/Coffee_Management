from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QPixmap

from app.controllers.staff_controller import StaffController

class LoginView(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Đăng nhập - Quản lý Quán Cafe")
        self.setFixedSize(400, 500)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        
        # Logo/Image
        logo_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_label.setFixedSize(150, 150)
        # Here you would set the actual cafe logo
        # logo_label.setPixmap(QPixmap("app/resources/logo.png").scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setStyleSheet("background-color: #f5f5f5; border-radius: 75px;")
        logo_layout.addStretch()
        logo_layout.addWidget(logo_label)
        logo_layout.addStretch()
        
        title_label = QLabel("QUẢN LÝ QUÁN CAFE")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Vui lòng đăng nhập để tiếp tục")
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        # Add some spacing
        main_layout.addLayout(logo_layout)
        main_layout.addSpacing(20)
        main_layout.addWidget(title_label)
        main_layout.addWidget(subtitle_label)
        main_layout.addSpacing(30)
        
        # Username
        username_label = QLabel("Tên đăng nhập:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nhập tên đăng nhập")
        self.username_input.setMinimumHeight(35)
        
        # Password
        password_label = QLabel("Mật khẩu:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Nhập mật khẩu")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(35)
        
        # Login button
        self.login_button = QPushButton("ĐĂNG NHẬP")
        self.login_button.setMinimumHeight(40)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #367c39;
            }
        """)
        self.login_button.clicked.connect(self.handle_login)
        
        # Exit button
        self.exit_button = QPushButton("THOÁT")
        self.exit_button.setMinimumHeight(40)
        self.exit_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        self.exit_button.clicked.connect(self.close)
        
        # Add widgets to layout
        main_layout.addWidget(username_label)
        main_layout.addWidget(self.username_input)
        main_layout.addSpacing(10)
        main_layout.addWidget(password_label)
        main_layout.addWidget(self.password_input)
        main_layout.addSpacing(20)
        main_layout.addWidget(self.login_button)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.exit_button)
        
        main_layout.addStretch()
        
        # Footer
        footer_label = QLabel("© 2023 - Phần mềm Quản lý Quán Cafe")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("color: #888;")
        main_layout.addWidget(footer_label)
        
        # Set default focus to username input
        self.username_input.setFocus()
        
        # Connect enter key to login
        self.username_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(self.handle_login)
    
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Lỗi đăng nhập", "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu")
            return
        
        # Authenticate
        staff = StaffController.authenticate(username, password)
        
        if staff:
            # Login successful
            self.hide()
            if staff.role == "Pha chế":
                from app.views.barista_window import BaristaWindow
                self.main_window = BaristaWindow(staff)
            elif staff.role == "Thu ngân":
                from app.views.cashier_window import CashierWindow  
                self.main_window = CashierWindow(staff)
            else:
                from app.views.main_window import MainWindow
                self.main_window = MainWindow(staff)
            
            self.main_window.show()
        else:
            # Login failed
            QMessageBox.warning(self, "Lỗi đăng nhập", "Tên đăng nhập hoặc mật khẩu không chính xác") 