from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QStatusBar, QAction,
                             QMessageBox, QFrame, QToolButton, QListWidget, QListWidgetItem,
                             QSplitter, QComboBox, QGroupBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QCheckBox, QSpinBox)
from PyQt5.QtCore import Qt, QSize, QTimer, QDateTime
from PyQt5.QtGui import QIcon, QFont, QColor, QBrush

from app.controllers.order_controller import OrderController
from app.controllers.staff_controller import StaffController
from app.controllers.inventory_controller import InventoryController

class OrderItemWidget(QWidget):
    def __init__(self, order_item, parent=None):
        super().__init__(parent)
        self.order_item = order_item
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Frame chứa thông tin
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet("background-color: #f5f5f5; border-radius: 5px;")
        self.frame_layout = QVBoxLayout(frame)
        
        # Thông tin món
        if hasattr(self.order_item, 'menu_item') and self.order_item.menu_item:
            name_label = QLabel(f"<b>{self.order_item.menu_item.name}</b>")
            name_label.setFont(QFont("Arial", 12))
            
            quantity_label = QLabel(f"Số lượng: {self.order_item.quantity}")
            
            # Hiển thị ghi chú nếu có
            note = getattr(self.order_item, 'note', '')
            note_label = QLabel(f"Ghi chú: {note if note else 'Không có'}")
            
            # Hiển thị thời gian đặt hàng
            created_at = getattr(self.order_item, 'created_at', None)
            time_str = created_at.strftime("%H:%M") if created_at else "Không rõ"
            time_label = QLabel(f"Thời gian: {time_str}")
            
            # Thông tin bàn và đơn hàng
            table_name = "Không rõ"
            order_id = "?"
            
            if hasattr(self.order_item, 'order') and self.order_item.order:
                order_id = str(self.order_item.order.id)
                if hasattr(self.order_item.order, 'table') and self.order_item.order.table:
                    table_name = self.order_item.order.table.name
            
            info_label = QLabel(f"Bàn: {table_name} | Đơn: #{order_id}")
            
            # Thêm các label vào layout
            self.frame_layout.addWidget(name_label)
            self.frame_layout.addWidget(quantity_label)
            self.frame_layout.addWidget(note_label)
            self.frame_layout.addWidget(time_label)
            self.frame_layout.addWidget(info_label)
        else:
            name_label = QLabel("<b>Không có thông tin món</b>")
            quantity_label = QLabel("Không có thông tin")
            note_label = QLabel("")
            time_label = QLabel("")
            info_label = QLabel("")
            
            # Thêm các label vào layout
            self.frame_layout.addWidget(name_label)
            self.frame_layout.addWidget(quantity_label)
            self.frame_layout.addWidget(note_label)
            self.frame_layout.addWidget(time_label)
            self.frame_layout.addWidget(info_label)
        
        # Nút hoàn thành
        button_layout = QHBoxLayout()
        self.complete_button = QPushButton("Hoàn thành")
        self.complete_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.postpone_button = QPushButton("Hoãn lại")
        self.postpone_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        
        button_layout.addWidget(self.postpone_button)
        button_layout.addWidget(self.complete_button)
        
        self.frame_layout.addLayout(button_layout)
        
        layout.addWidget(frame)

class BaristaWindow(QMainWindow):
    def __init__(self, current_staff=None):
        super().__init__()
        
        self.current_staff = current_staff
        self.pending_orders = []  # Đơn hàng đang đợi pha chế
        self.selected_item = None  # Lưu item hiện tại đang được chọn
        
        self.setWindowTitle("Pha Chế - Quản lý Quán Cafe")
        self.setMinimumSize(1200, 900)  # Tăng chiều cao tối thiểu từ 800 lên 900
        
        # Timer tự động làm mới
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_pending_orders)
        self.refresh_timer.start(30000)  # Làm mới mỗi 30 giây
        
        self.setup_ui()
        self.load_pending_orders()
    
    def setup_ui(self):
        # Menu bar
        self.setup_menu_bar()
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(10)  # Thêm khoảng cách giữa các thành phần
        
        # Header
        header_layout = QHBoxLayout()
        
        cafe_label = QLabel("PHA CHẾ")
        cafe_label.setFont(QFont("Arial", 18, QFont.Bold))
        cafe_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addStretch()
        header_layout.addWidget(cafe_label)
        header_layout.addStretch()
        
        if self.current_staff:
            # Hiển thị thông tin nhân viên pha chế
            user_frame = QFrame()
            user_frame.setFrameShape(QFrame.StyledPanel)
            user_frame.setStyleSheet("background-color: #ffecb3; border-radius: 5px; padding: 5px;")
            user_layout = QVBoxLayout(user_frame)
            
            user_info = QLabel(f"Barista: {self.current_staff.name}")
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
        
        # Bộ lọc và công cụ
        filter_layout = QHBoxLayout()
        
        # Dropdown lọc theo loại đồ uống
        self.category_filter = QComboBox()
        self.category_filter.addItem("Tất cả")
        self.category_filter.addItem("Cà phê")
        self.category_filter.addItem("Trà")
        self.category_filter.addItem("Đồ uống đá xay")
        self.category_filter.addItem("Đồ ăn")
        self.category_filter.currentIndexChanged.connect(self.apply_filters)
        
        # Nút làm mới
        refresh_btn = QPushButton("Làm mới")
        refresh_btn.setStyleSheet("background-color: #2196F3; color: white;")
        refresh_btn.clicked.connect(self.load_pending_orders)
        
        filter_layout.addWidget(QLabel("Lọc theo loại:"))
        filter_layout.addWidget(self.category_filter)
        filter_layout.addSpacing(20)
        filter_layout.addStretch()
        filter_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(filter_layout)
        
        # Khu vực hiển thị hàng đợi và công thức (QSplitter cho phép kéo thả điều chỉnh kích thước)
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Panel trái: Hàng đợi đơn hàng
        orders_group = QGroupBox("Hàng đợi đơn hàng")
        orders_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        orders_layout = QVBoxLayout(orders_group)
        
        self.orders_list = QListWidget()
        self.orders_list.setMinimumWidth(450)  # Tăng chiều rộng tối thiểu
        self.orders_list.setMinimumHeight(500)  # Tăng chiều cao tối thiểu
        self.orders_list.currentItemChanged.connect(self.on_order_selected)
        
        orders_layout.addWidget(self.orders_list)
        
        # Panel phải: Hiển thị công thức
        recipe_group = QGroupBox("Chi tiết công thức")
        recipe_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        recipe_layout = QVBoxLayout(recipe_group)
        
        self.recipe_info = QLabel("Chọn một món để xem công thức")
        self.recipe_info.setAlignment(Qt.AlignCenter)
        self.recipe_info.setFont(QFont("Arial", 11))
        
        self.recipe_table = QTableWidget()
        self.recipe_table.setColumnCount(3)
        self.recipe_table.setHorizontalHeaderLabels(["Nguyên liệu", "Số lượng", "Đơn vị"])
        self.recipe_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.recipe_table.setStyleSheet("background-color: #f0f0f0;")
        self.recipe_table.setMinimumHeight(350)  # Tăng chiều cao tối thiểu của bảng
        
        recipe_layout.addWidget(self.recipe_info)
        recipe_layout.addWidget(self.recipe_table)
        
        # Thêm các panel vào splitter
        self.splitter.addWidget(orders_group)
        self.splitter.addWidget(recipe_group)
        self.splitter.setSizes([600, 600])  # Tăng kích thước ban đầu của các panel
        
        # Đặt stretch factors để panel đơn hàng rộng hơn panel công thức
        self.splitter.setStretchFactor(0, 2)  # Panel đơn hàng (trọng số 2)
        self.splitter.setStretchFactor(1, 3)  # Panel công thức (trọng số 3)
        
        main_layout.addWidget(self.splitter, 1)  # Stretch factor 1 cho phép khu vực này mở rộng
        
        # Thông kê món đang làm
        stats_layout = QHBoxLayout()
        
        # Số lượng món đang chờ
        self.waiting_label = QLabel("Đang chờ: 0 món")
        self.waiting_label.setFont(QFont("Arial", 10, QFont.Bold))
        
        # Số lượng món đã hoàn thành
        self.completed_label = QLabel("Hoàn thành: 0 món")
        self.completed_label.setFont(QFont("Arial", 10, QFont.Bold))
        
        stats_layout.addWidget(self.waiting_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.completed_label)
        
        main_layout.addLayout(stats_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Sẵn sàng pha chế")
    
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
    
    def load_pending_orders(self):
        """Tải các đơn hàng đang chờ pha chế"""
        # Lấy các đơn hàng đang xử lý
        self.pending_orders = OrderController.get_pending_items()
        
        # Áp dụng bộ lọc và cập nhật giao diện
        self.apply_filters()
        
        # Cập nhật số lượng
        self.waiting_label.setText(f"Đang chờ: {len(self.pending_orders)} món")
        
        # Số lượng món đã hoàn thành
        completed_count = OrderController.get_completed_items_count(self.current_staff.id) if self.current_staff else 0
        self.completed_label.setText(f"Hoàn thành: {completed_count} món")
        
        # Cập nhật trạng thái
        self.status_bar.showMessage(f"Đã cập nhật lúc {QDateTime.currentDateTime().toString('hh:mm:ss')}")
    
    def apply_filters(self):
        """Áp dụng bộ lọc và cập nhật giao diện hiển thị"""
        filtered_orders = self.pending_orders
        
        # Lọc theo loại nếu không phải "Tất cả"
        category = self.category_filter.currentText()
        if category != "Tất cả":
            filtered_orders = [
                order for order in filtered_orders
                if hasattr(order, 'menu_item') and 
                order.menu_item and 
                hasattr(order.menu_item, 'category') and
                order.menu_item.category and
                order.menu_item.category.name == category
            ]
        
        # Cập nhật danh sách đơn hàng
        self.update_orders_list(filtered_orders)
    
    def update_orders_list(self, filtered_orders):
        """Cập nhật danh sách đơn hàng"""
        # Lưu lại item đang chọn nếu có
        current_selected_id = None
        if self.selected_item and hasattr(self.selected_item, 'id'):
            current_selected_id = self.selected_item.id
        
        # Xóa danh sách hiện tại
        self.orders_list.clear()
        
        # Thêm các món vào hàng đợi
        for item in filtered_orders:
            self.add_item_to_list(self.orders_list, item)
        
        # Chọn lại item đã chọn trước đó nếu có
        if current_selected_id:
            for i in range(self.orders_list.count()):
                item = self.orders_list.item(i)
                widget = self.orders_list.itemWidget(item)
                if hasattr(widget, 'order_item') and widget.order_item.id == current_selected_id:
                    self.orders_list.setCurrentItem(item)
                    break
    
    def add_item_to_list(self, list_widget, order_item):
        """Thêm một item vào danh sách và cấu hình các nút điều khiển"""
        item_widget = OrderItemWidget(order_item)
        
        # Kết nối các sự kiện của nút
        item_widget.complete_button.clicked.connect(lambda: self.complete_item(order_item, item_widget))
        item_widget.postpone_button.clicked.connect(lambda: self.postpone_item(order_item, item_widget))
        
        # Tạo item và thêm vào list
        list_item = QListWidgetItem(list_widget)
        list_item.setSizeHint(item_widget.sizeHint())
        list_widget.addItem(list_item)
        list_widget.setItemWidget(list_item, item_widget)
    
    def on_order_selected(self, current, previous):
        """Xử lý khi người dùng chọn một đơn hàng trong danh sách"""
        if not current:
            # Xóa thông tin công thức nếu không có item nào được chọn
            self.recipe_info.setText("Chọn một món để xem công thức")
            self.recipe_table.setRowCount(0)
            self.selected_item = None
            return
        
        # Lấy widget của item đang chọn
        item_widget = self.orders_list.itemWidget(current)
        if not item_widget or not hasattr(item_widget, 'order_item'):
            return
        
        order_item = item_widget.order_item
        self.selected_item = order_item
        
        # Hiển thị thông tin món
        if hasattr(order_item, 'menu_item') and order_item.menu_item:
            self.recipe_info.setText(f"<b>Công thức cho: {order_item.menu_item.name}</b><br>"
                                    f"Số lượng: {order_item.quantity}<br>"
                                    f"Ghi chú: {order_item.note if hasattr(order_item, 'note') and order_item.note else 'Không có'}")
            
            # Lấy công thức
            recipe_items = InventoryController.get_recipe(order_item.menu_item_id)
            
            # Hiển thị công thức lên bảng
            self.recipe_table.setRowCount(0)
            if recipe_items:
                self.recipe_table.setRowCount(len(recipe_items))
                for row, item in enumerate(recipe_items):
                    # Tính toán số lượng cần dùng cho đơn hàng này
                    quantity_needed = item["quantity"] * order_item.quantity
                    
                    name_item = QTableWidgetItem(item["name"])
                    quantity_item = QTableWidgetItem(f"{quantity_needed:.2f}")
                    unit_item = QTableWidgetItem(item["unit"])
                    
                    # Kiểm tra số lượng tồn kho
                    inventory_items = InventoryController.get_all_inventory_items()
                    inventory_map = {inv.name: inv for inv in inventory_items}
                    
                    # Tô màu dựa trên tình trạng tồn kho
                    if item["name"] in inventory_map:
                        inventory = inventory_map[item["name"]]
                        if inventory.quantity <= 0:
                            name_item.setBackground(QBrush(QColor("#ffcdd2")))  # Đỏ nhạt - hết hàng
                        elif inventory.quantity < quantity_needed:
                            name_item.setBackground(QBrush(QColor("#fff9c4")))  # Vàng nhạt - thiếu hàng
                    
                    self.recipe_table.setItem(row, 0, name_item)
                    self.recipe_table.setItem(row, 1, quantity_item)
                    self.recipe_table.setItem(row, 2, unit_item)
            else:
                self.recipe_info.setText(f"<b>Công thức cho: {order_item.menu_item.name}</b><br>"
                                        f"Số lượng: {order_item.quantity}<br>"
                                        f"<font color='red'>Không có công thức cho món này</font>")
        else:
            self.recipe_info.setText("Không có thông tin về món này")
            self.recipe_table.setRowCount(0)
    
    def complete_item(self, order_item, item_widget):
        """Đánh dấu một món là đã hoàn thành"""
        # Gọi API để cập nhật trạng thái món
        if OrderController.complete_order_item(order_item.id, self.current_staff.id if self.current_staff else None):
            # Xóa item khỏi danh sách
            for i in range(self.orders_list.count()):
                item = self.orders_list.item(i)
                if self.orders_list.itemWidget(item) == item_widget:
                    self.orders_list.takeItem(i)
                    break
            
            # Nếu item hoàn thành là item đang chọn, xóa thông tin công thức
            if self.selected_item and self.selected_item.id == order_item.id:
                self.recipe_info.setText("Chọn một món để xem công thức")
                self.recipe_table.setRowCount(0)
                self.selected_item = None
            
            # Cập nhật số lượng đã hoàn thành
            completed_count = OrderController.get_completed_items_count(self.current_staff.id) if self.current_staff else 0
            self.completed_label.setText(f"Hoàn thành: {completed_count} món")
            
            # Cập nhật số lượng đang chờ
            waiting_count = self.orders_list.count()
            self.waiting_label.setText(f"Đang chờ: {waiting_count} món")
            
            QMessageBox.information(self, "Thành công", f"Đã hoàn thành món {order_item.menu_item.name if hasattr(order_item, 'menu_item') and order_item.menu_item else 'Không rõ'}")
        else:
            QMessageBox.warning(self, "Lỗi", "Không thể cập nhật trạng thái món")
    
    def postpone_item(self, order_item, item_widget):
        """Chuyển món xuống cuối hàng đợi"""
        # Tìm và xóa item khỏi danh sách
        for i in range(self.orders_list.count()):
            item = self.orders_list.item(i)
            if self.orders_list.itemWidget(item) == item_widget:
                self.orders_list.takeItem(i)
                break
        
        # Thêm lại vào cuối danh sách
        self.add_item_to_list(self.orders_list, order_item)
        
        # Thông báo
        QMessageBox.information(self, "Đã hoãn", f"Đã chuyển món {order_item.menu_item.name if hasattr(order_item, 'menu_item') and order_item.menu_item else 'Không rõ'} xuống cuối hàng đợi")
    
    def logout(self):
        reply = QMessageBox.question(self, "Đăng xuất", 
                                     "Bạn có chắc chắn muốn đăng xuất?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Dừng timer
            self.refresh_timer.stop()
            
            from app.views.login_view import LoginView
            self.close()
            self.login_view = LoginView()
            self.login_view.show()
    
    def show_about(self):
        QMessageBox.about(self, "Giới thiệu", 
                         "Phần mềm Quản lý Quán Cafe\n"
                         "Phiên bản 1.0\n"
                         "© 2023 - Mọi quyền được bảo lưu")
    
    def closeEvent(self, event):
        # Dừng timer khi đóng cửa sổ
        self.refresh_timer.stop()
        super().closeEvent(event) 