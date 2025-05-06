from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QPushButton, QLabel, QStatusBar, QAction, 
                             QMessageBox, QFrame, QToolButton, QSplitter, QTableWidget,
                             QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QSize, QDateTime
from PyQt5.QtGui import QIcon, QFont, QColor

from app.views.table_view import TableView
from app.views.order_view import OrderView
from app.controllers.order_controller import OrderController
from app.controllers.staff_controller import StaffController

class CashierWindow(QMainWindow):
    def __init__(self, current_staff=None):
        super().__init__()
        
        self.current_staff = current_staff
        self.active_orders = []
        
        self.setWindowTitle("Thu Ngân - Quản lý Quán Cafe")
        self.setMinimumSize(1200, 800)
        
        self.setup_ui()
        self.load_active_orders()
    
    def setup_ui(self):
        # Menu bar với các tùy chọn giới hạn cho thu ngân
        self.setup_menu_bar()
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        main_layout = QVBoxLayout(main_widget)
        
        # Header với thông tin ca làm việc
        header_layout = QHBoxLayout()
        
        cafe_label = QLabel("THU NGÂN")
        cafe_label.setFont(QFont("Arial", 18, QFont.Bold))
        cafe_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addStretch()
        header_layout.addWidget(cafe_label)
        header_layout.addStretch()
        
        if self.current_staff:
            # Hiển thị thông tin nhân viên và ca làm việc
            user_frame = QFrame()
            user_frame.setFrameShape(QFrame.StyledPanel)
            user_frame.setStyleSheet("background-color: #e3f2fd; border-radius: 5px; padding: 5px;")
            user_layout = QVBoxLayout(user_frame)
            
            user_info = QLabel(f"Nhân viên: {self.current_staff.name}")
            user_info.setFont(QFont("Arial", 10, QFont.Bold))
            
            # Hiển thị thời gian hiện tại của ca làm việc
            current_time = QDateTime.currentDateTime().toString("hh:mm - dd/MM/yyyy")
            shift_info = QLabel(f"Ca làm việc: {self.current_staff.shift or 'Không xác định'}")
            time_info = QLabel(f"Thời gian: {current_time}")
            
            user_layout.addWidget(user_info)
            user_layout.addWidget(shift_info)
            user_layout.addWidget(time_info)
            
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
            user_layout.addWidget(logout_btn)
            
            header_layout.addWidget(user_frame)
        
        main_layout.addLayout(header_layout)
        
        # Buttons cho các chức năng chính
        buttons_layout = QHBoxLayout()
        
        new_order_btn = QToolButton()
        new_order_btn.setText("Đơn mới")
        new_order_btn.setIcon(QIcon.fromTheme("document-new"))
        new_order_btn.setIconSize(QSize(32, 32))
        new_order_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        new_order_btn.setMinimumSize(100, 80)
        new_order_btn.clicked.connect(self.show_table_view)
        
        payment_btn = QToolButton()
        payment_btn.setText("Thanh toán")
        payment_btn.setIcon(QIcon.fromTheme("document-save"))
        payment_btn.setIconSize(QSize(32, 32))
        payment_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        payment_btn.setMinimumSize(100, 80)
        payment_btn.clicked.connect(self.process_payment)
        
        receipt_btn = QToolButton()
        receipt_btn.setText("In hóa đơn")
        receipt_btn.setIcon(QIcon.fromTheme("document-print"))
        receipt_btn.setIconSize(QSize(32, 32))
        receipt_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        receipt_btn.setMinimumSize(100, 80)
        receipt_btn.clicked.connect(self.print_receipt)
        
        buttons_layout.addWidget(new_order_btn)
        buttons_layout.addWidget(payment_btn)
        buttons_layout.addWidget(receipt_btn)
        buttons_layout.addStretch()
        
        main_layout.addLayout(buttons_layout)
        
        # Content area with splitter
        self.content_splitter = QSplitter(Qt.Horizontal)
        
        # Bảng đơn hàng đang hoạt động
        self.orders_widget = QWidget()
        orders_layout = QVBoxLayout(self.orders_widget)
        
        orders_header = QLabel("ĐƠN HÀNG ĐANG XỬ LÝ")
        orders_header.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(5)
        self.orders_table.setHorizontalHeaderLabels(["ID", "Bàn", "Thời gian", "Trạng thái", "Tổng tiền"])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.orders_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.orders_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.orders_table.doubleClicked.connect(self.view_order_details)
        
        refresh_btn = QPushButton("Làm mới")
        refresh_btn.clicked.connect(self.load_active_orders)
        
        orders_layout.addWidget(orders_header)
        orders_layout.addWidget(self.orders_table)
        orders_layout.addWidget(refresh_btn)
        
        # Khu vực xem chi tiết đơn hàng
        self.detail_widget = QWidget()
        self.detail_layout = QVBoxLayout(self.detail_widget)
        
        detail_header = QLabel("CHI TIẾT ĐƠN HÀNG")
        detail_header.setFont(QFont("Arial", 12, QFont.Bold))
        
        # Nội dung chi tiết đơn hàng sẽ được thêm khi chọn đơn
        self.detail_content = QLabel("Chọn một đơn hàng để xem chi tiết")
        self.detail_content.setAlignment(Qt.AlignCenter)
        self.detail_content.setStyleSheet("color: #888; font-style: italic;")
        
        self.detail_layout.addWidget(detail_header)
        self.detail_layout.addWidget(self.detail_content)
        
        # Thêm các widget vào splitter
        self.content_splitter.addWidget(self.orders_widget)
        self.content_splitter.addWidget(self.detail_widget)
        self.content_splitter.setSizes([400, 800])
        
        main_layout.addWidget(self.content_splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Sẵn sàng phục vụ")
    
    def setup_menu_bar(self):
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&Hệ thống")
        
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
    
    def load_active_orders(self):
        # Xóa dữ liệu hiện tại
        self.orders_table.setRowCount(0)
        
        # Lấy các đơn hàng đang hoạt động (đang phục vụ, chưa thanh toán)
        self.active_orders = OrderController.get_active_orders()
        
        # Hiển thị lên bảng
        for row, order in enumerate(self.active_orders):
            self.orders_table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(order.id))
            self.orders_table.setItem(row, 0, id_item)
            
            # Bàn
            table_name = order.table.name if order.table else "Không xác định"
            table_item = QTableWidgetItem(table_name)
            self.orders_table.setItem(row, 1, table_item)
            
            # Thời gian
            time_str = order.created_at.strftime("%H:%M - %d/%m/%Y") if order.created_at else "Không xác định"
            time_item = QTableWidgetItem(time_str)
            self.orders_table.setItem(row, 2, time_item)
            
            # Trạng thái
            status_item = QTableWidgetItem(order.status)
            if order.status == "đang phục vụ":
                status_item.setForeground(QColor("#FF9800"))
            elif order.status == "hoàn thành":
                status_item.setForeground(QColor("#4CAF50"))
            self.orders_table.setItem(row, 3, status_item)
            
            # Tổng tiền
            total_item = QTableWidgetItem(f"{order.total_amount:,.0f} VNĐ" if order.total_amount else "0 VNĐ")
            self.orders_table.setItem(row, 4, total_item)
        
        # Cập nhật trạng thái
        self.status_bar.showMessage(f"Đang có {len(self.active_orders)} đơn hàng đang xử lý")
    
    def view_order_details(self, index):
        row = index.row()
        order_id = int(self.orders_table.item(row, 0).text())
        
        # Tìm đơn hàng trong danh sách
        order = next((o for o in self.active_orders if o.id == order_id), None)
        
        if order:
            # Xóa widget chi tiết hiện tại
            for i in reversed(range(self.detail_layout.count())):
                widget = self.detail_layout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()
            
            # Tạo lại widgets hiển thị chi tiết
            header = QLabel("CHI TIẾT ĐƠN HÀNG")
            header.setFont(QFont("Arial", 12, QFont.Bold))
            self.detail_layout.addWidget(header)
            
            # Thông tin đơn hàng
            order_frame = QFrame()
            order_frame.setFrameShape(QFrame.StyledPanel)
            order_frame.setStyleSheet("background-color: #e8f5e9; border-radius: 5px; padding: 10px;")
            order_info_layout = QVBoxLayout(order_frame)
            
            # Thông tin chung
            order_info_layout.addWidget(QLabel(f"<b>Mã đơn:</b> #{order.id}"))
            order_info_layout.addWidget(QLabel(f"<b>Bàn:</b> {order.table.name if order.table else 'Không xác định'}"))
            order_info_layout.addWidget(QLabel(f"<b>Nhân viên:</b> {order.staff.name if order.staff else 'Không xác định'}"))
            order_info_layout.addWidget(QLabel(f"<b>Thời gian:</b> {order.created_at.strftime('%H:%M - %d/%m/%Y') if order.created_at else 'Không xác định'}"))
            order_info_layout.addWidget(QLabel(f"<b>Trạng thái:</b> {order.status}"))
            
            self.detail_layout.addWidget(order_frame)
            
            # Danh sách món
            items_label = QLabel("Danh sách món:")
            items_label.setFont(QFont("Arial", 11, QFont.Bold))
            self.detail_layout.addWidget(items_label)
            
            items_table = QTableWidget()
            items_table.setColumnCount(4)
            items_table.setHorizontalHeaderLabels(["Món", "Số lượng", "Đơn giá", "Thành tiền"])
            items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
            # Thêm các món vào bảng
            if hasattr(order, 'order_items') and order.order_items:
                items_table.setRowCount(len(order.order_items))
                for row, item in enumerate(order.order_items):
                    # Tên món
                    name_item = QTableWidgetItem(item.menu_item.name if item.menu_item else "Không xác định")
                    items_table.setItem(row, 0, name_item)
                    
                    # Số lượng
                    quantity_item = QTableWidgetItem(str(item.quantity))
                    items_table.setItem(row, 1, quantity_item)
                    
                    # Đơn giá
                    price = item.menu_item.price if item.menu_item else 0
                    price_item = QTableWidgetItem(f"{price:,.0f} VNĐ")
                    items_table.setItem(row, 2, price_item)
                    
                    # Thành tiền
                    subtotal = price * item.quantity
                    subtotal_item = QTableWidgetItem(f"{subtotal:,.0f} VNĐ")
                    items_table.setItem(row, 3, subtotal_item)
            else:
                items_table.setRowCount(1)
                items_table.setSpan(0, 0, 1, 4)
                items_table.setItem(0, 0, QTableWidgetItem("Không có món nào"))
            
            self.detail_layout.addWidget(items_table)
            
            # Tổng tiền
            total_frame = QFrame()
            total_frame.setFrameShape(QFrame.StyledPanel)
            total_frame.setStyleSheet("background-color: #e3f2fd; border-radius: 5px; padding: 10px;")
            total_layout = QVBoxLayout(total_frame)
            
            total_label = QLabel(f"Tổng tiền: {order.total_amount:,.0f} VNĐ" if order.total_amount else "Tổng tiền: 0 VNĐ")
            total_label.setFont(QFont("Arial", 12, QFont.Bold))
            total_label.setAlignment(Qt.AlignRight)
            total_layout.addWidget(total_label)
            
            self.detail_layout.addWidget(total_frame)
            
            # Các nút xử lý
            buttons_layout = QHBoxLayout()
            
            payment_btn = QPushButton("Thanh toán")
            payment_btn.setStyleSheet("background-color: #4CAF50; color: white;")
            payment_btn.clicked.connect(lambda: self.process_payment(order.id))
            
            print_btn = QPushButton("In hóa đơn")
            print_btn.clicked.connect(lambda: self.print_receipt(order.id))
            
            cancel_btn = QPushButton("Hủy đơn")
            cancel_btn.setStyleSheet("background-color: #f44336; color: white;")
            cancel_btn.clicked.connect(lambda: self.cancel_order(order.id))
            
            buttons_layout.addWidget(cancel_btn)
            buttons_layout.addStretch()
            buttons_layout.addWidget(print_btn)
            buttons_layout.addWidget(payment_btn)
            
            self.detail_layout.addLayout(buttons_layout)
            
            # Thêm khoảng trống cuối cùng
            self.detail_layout.addStretch()
    
    def show_table_view(self):
        # Hiển thị giao diện quản lý bàn để tạo đơn hàng mới
        self.table_view = TableView(self.current_staff)
        self.table_view.show()
        # Khi đóng, làm mới danh sách đơn hàng
        self.table_view.destroyed.connect(self.load_active_orders)
    
    def process_payment(self, order_id=None):
        if not order_id and self.orders_table.selectedItems():
            row = self.orders_table.currentRow()
            order_id = int(self.orders_table.item(row, 0).text())
        
        if order_id:
            # TODO: Tạo dialog thu tiền và xử lý thanh toán
            result = OrderController.complete_order(order_id)
            if result:
                QMessageBox.information(self, "Thành công", "Đã thanh toán đơn hàng thành công")
                self.load_active_orders()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể thanh toán đơn hàng")
        else:
            QMessageBox.warning(self, "Chưa chọn đơn", "Vui lòng chọn một đơn hàng để thanh toán")
    
    def print_receipt(self, order_id=None):
        if not order_id and self.orders_table.selectedItems():
            row = self.orders_table.currentRow()
            order_id = int(self.orders_table.item(row, 0).text())
        
        if order_id:
            # TODO: Tạo và in hóa đơn
            QMessageBox.information(self, "In hóa đơn", "Chức năng in hóa đơn đang được phát triển")
        else:
            QMessageBox.warning(self, "Chưa chọn đơn", "Vui lòng chọn một đơn hàng để in hóa đơn")
    
    def cancel_order(self, order_id):
        if order_id:
            reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc chắn muốn hủy đơn hàng này?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                result = OrderController.cancel_order(order_id)
                if result:
                    QMessageBox.information(self, "Thành công", "Đã hủy đơn hàng")
                    self.load_active_orders()
                else:
                    QMessageBox.warning(self, "Lỗi", "Không thể hủy đơn hàng")
    
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