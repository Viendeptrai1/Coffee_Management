from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QPushButton, QLabel, QStatusBar, QAction, 
                             QMessageBox, QMenu)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont

from app.views.table_view import TableView
from app.views.menu_view import MenuView
from app.views.order_view import OrderView
from app.views.staff_view import StaffView
from app.views.shift_view import ShiftView
from app.views.stats_view import StatsView
from app.controllers.staff_controller import StaffController

class MainWindow(QMainWindow):
    def __init__(self, current_staff=None):
        super().__init__()
        
        self.current_staff = current_staff
        
        self.setWindowTitle("Quản lý Quán Cafe")
        self.setMinimumSize(1200, 800)
        
        self.setup_ui()
    
    def setup_ui(self):
        # Menu bar
        self.setup_menu_bar()
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        main_layout = QVBoxLayout(main_widget)
        
        # Header
        header_layout = QHBoxLayout()
        
        cafe_label = QLabel("QUẢN LÝ QUÁN CAFE")
        cafe_label.setFont(QFont("Arial", 18, QFont.Bold))
        cafe_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addStretch()
        header_layout.addWidget(cafe_label)
        header_layout.addStretch()
        
        if self.current_staff:
            user_info = QLabel(f"Nhân viên: {self.current_staff.name} ({self.current_staff.role})")
            user_info.setFont(QFont("Arial", 10))
            user_info.setAlignment(Qt.AlignRight)
            header_layout.addWidget(user_info)
            
            # Add logout button
            logout_btn = QPushButton("Đăng xuất")
            logout_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border-radius: 3px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
            """)
            logout_btn.clicked.connect(self.logout)
            header_layout.addWidget(logout_btn)
        
        main_layout.addLayout(header_layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.create_tabs()
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Sẵn sàng phục vụ")
    
    def setup_menu_bar(self):
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&Hệ thống")
        
        # Settings action
        settings_action = QAction("Cài đặt", self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)
        
        # Backup action
        backup_action = QAction("Sao lưu dữ liệu", self)
        backup_action.triggered.connect(self.backup_data)
        file_menu.addAction(backup_action)
        
        file_menu.addSeparator()
        
        # Logout action
        logout_action = QAction("Đăng xuất", self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        
        # Exit action
        exit_action = QAction("Thoát", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Trợ giúp")
        
        # About action
        about_action = QAction("Giới thiệu", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_tabs(self):
        # Table tab
        self.table_view = TableView(self.current_staff)
        self.tab_widget.addTab(self.table_view, "Quản lý bàn")
        
        # Menu tab
        self.menu_view = MenuView(self.current_staff)
        self.tab_widget.addTab(self.menu_view, "Quản lý thực đơn")
        
        # Order tab
        self.order_view = OrderView(self.current_staff)
        self.tab_widget.addTab(self.order_view, "Quản lý đơn hàng")
        
        # Only add these tabs for managers
        if self.current_staff and self.current_staff.role == "Quản lý":
            # Staff tab
            self.staff_view = StaffView(self.current_staff)
            self.tab_widget.addTab(self.staff_view, "Quản lý nhân viên")
            
            # Shift tab
            self.shift_view = ShiftView(self.current_staff)
            self.tab_widget.addTab(self.shift_view, "Quản lý ca làm việc")
            
            # Inventory tab
            from app.views.inventory_view import InventoryView
            self.inventory_view = InventoryView()
            self.tab_widget.addTab(self.inventory_view, "Quản lý kho")
            
            # Stats tab
            self.stats_view = StatsView()
            self.tab_widget.addTab(self.stats_view, "Thống kê")
    
    def open_settings(self):
        QMessageBox.information(self, "Cài đặt", "Chức năng cài đặt đang được phát triển")
    
    def backup_data(self):
        QMessageBox.information(self, "Sao lưu", "Chức năng sao lưu đang được phát triển")
    
    def logout(self):
        reply = QMessageBox.question(self, "Đăng xuất", 
                                     "Bạn có chắc chắn muốn đăng xuất?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            from app.views.login_view import LoginView
            self.close()
            self.login_view = LoginView()
            self.login_view.show()
    
    def show_about(self):
        QMessageBox.about(self, "Giới thiệu", 
                          "Phần mềm Quản lý Quán Cafe\n"
                          "Phiên bản 1.0\n"
                          "© 2023 - Mọi quyền được bảo lưu") 