from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGridLayout, QScrollArea, QFrame,
                             QDialog, QLineEdit, QSpinBox, QComboBox, QMessageBox,
                             QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem,
                             QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsPixmapItem)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QRectF, QPointF
from PyQt5.QtGui import QIcon, QFont, QColor, QPen, QBrush, QPainter, QPainterPath, QPixmap

from app.controllers.table_controller import TableController
from app.controllers.order_controller import OrderController

class TableItem(QGraphicsRectItem):
    def __init__(self, table_id, table_name, status, capacity, x, y, width, height, parent=None):
        super().__init__(x, y, width, height, parent)
        self.table_id = table_id
        self.table_name = table_name
        self.status = status
        self.capacity = capacity
        self.setAcceptHoverEvents(True)
        
        # Thiết lập màu sắc dựa trên trạng thái
        self.update_color()
        
        # Thêm text hiển thị tên bàn và số chỗ
        self.text_item = QGraphicsTextItem(f"{table_name}\n({capacity} chỗ)", self)
        self.text_item.setPos(x + 5, y + 5)
        self.text_item.setDefaultTextColor(Qt.white)
        font = QFont("Arial", 10, QFont.Bold)
        self.text_item.setFont(font)
        
    def update_color(self):
        brush = QBrush()
        if self.status == "trống":
            brush.setColor(QColor("#4CAF50"))  # Green
        elif self.status == "đang phục vụ":
            brush.setColor(QColor("#FF9800"))  # Orange
        else:  # đã đặt trước
            brush.setColor(QColor("#9E9E9E"))  # Gray
        brush.setStyle(Qt.SolidPattern)
        self.setBrush(brush)
        
        # Viền
        pen = QPen(Qt.black)
        pen.setWidth(2)
        self.setPen(pen)
    
    def mousePressEvent(self, event):
        # Gửi tín hiệu tới scene khi bàn được nhấp vào
        scene = self.scene()
        if scene and hasattr(scene, 'tableClicked'):
            scene.tableClicked.emit(self.table_id)
        super().mousePressEvent(event)
    
    def hoverEnterEvent(self, event):
        # Hiệu ứng khi hover
        pen = QPen(Qt.white)
        pen.setWidth(3)
        self.setPen(pen)
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        # Trở lại bình thường khi hết hover
        pen = QPen(Qt.black)
        pen.setWidth(2)
        self.setPen(pen)
        super().hoverLeaveEvent(event)

class CafeScene(QGraphicsScene):
    tableClicked = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tables = {}  # Lưu trữ các đối tượng TableItem theo table_id
        
        # Thiết lập kích thước scene
        self.setSceneRect(0, 0, 800, 600)
        
        # Vẽ nền và layout của quán cafe
        self.setup_cafe_layout()
    
    def setup_cafe_layout(self):
        # Vẽ viền ngoài của quán cafe (tường)
        wall = QGraphicsRectItem(0, 0, 800, 600)
        wall.setBrush(QBrush(QColor("#F5F5F5")))
        wall.setPen(QPen(Qt.black, 2))
        self.addItem(wall)
        
        # Vẽ cửa vào
        door = QGraphicsRectItem(350, 0, 100, 10)
        door.setBrush(QBrush(QColor("#8D6E63")))  # Nâu
        door.setPen(QPen(Qt.black, 2))
        self.addItem(door)
        door_text = QGraphicsTextItem("CỬA VÀO")
        door_text.setPos(370, 15)
        door_text.setDefaultTextColor(Qt.black)
        door_text.setFont(QFont("Arial", 10, QFont.Bold))
        self.addItem(door_text)
        
        # Vẽ quầy cafe
        counter = QGraphicsRectItem(600, 50, 150, 80)
        counter.setBrush(QBrush(QColor("#A1887F")))  # Nâu nhạt
        counter.setPen(QPen(Qt.black, 2))
        self.addItem(counter)
        counter_text = QGraphicsTextItem("QUẦY CAFE")
        counter_text.setPos(630, 80)
        counter_text.setDefaultTextColor(Qt.white)
        counter_text.setFont(QFont("Arial", 10, QFont.Bold))
        self.addItem(counter_text)
        
        # Vẽ khu vực sân vườn
        garden = QGraphicsRectItem(50, 400, 400, 150)
        garden.setBrush(QBrush(QColor("#C5E1A5")))  # Xanh lá nhạt
        garden.setPen(QPen(Qt.black, 2))
        self.addItem(garden)
        garden_text = QGraphicsTextItem("SÂN VƯỜN")
        garden_text.setPos(200, 450)
        garden_text.setDefaultTextColor(Qt.black)
        garden_text.setFont(QFont("Arial", 12, QFont.Bold))
        self.addItem(garden_text)
        
        # Vẽ khu vực cửa sổ
        window_area = QGraphicsRectItem(50, 50, 130, 300)
        window_area.setBrush(QBrush(QColor("#B3E5FC")))  # Xanh dương nhạt
        window_area.setPen(QPen(Qt.black, 2))
        self.addItem(window_area)
        window_text = QGraphicsTextItem("CỬA SỔ")
        window_text.setPos(80, 180)
        window_text.setDefaultTextColor(Qt.black)
        window_text.setFont(QFont("Arial", 10, QFont.Bold))
        self.addItem(window_text)
        
        # Vẽ khu vực trung tâm
        center_area = QGraphicsRectItem(200, 150, 350, 200)
        center_area.setBrush(QBrush(QColor("#FFECB3")))  # Vàng nhạt
        center_area.setPen(QPen(Qt.black, 2))
        self.addItem(center_area)
        center_text = QGraphicsTextItem("KHU VỰC GIỮA")
        center_text.setPos(310, 240)
        center_text.setDefaultTextColor(Qt.black)
        center_text.setFont(QFont("Arial", 10, QFont.Bold))
        self.addItem(center_text)
        
        # Vẽ khu vực góc
        corner_area = QGraphicsRectItem(600, 200, 150, 350)
        corner_area.setBrush(QBrush(QColor("#E1BEE7")))  # Tím nhạt
        corner_area.setPen(QPen(Qt.black, 2))
        self.addItem(corner_area)
        corner_text = QGraphicsTextItem("GÓC")
        corner_text.setPos(655, 360)
        corner_text.setDefaultTextColor(Qt.black)
        corner_text.setFont(QFont("Arial", 10, QFont.Bold))
        self.addItem(corner_text)
    
    def add_table(self, table_id, table_name, status, capacity, location):
        # Xác định vị trí dựa trên location
        x, y = self.get_position_for_location(table_id, location)
        
        # Tạo bàn với kích thước dựa trên capacity
        width = min(80 + capacity * 5, 120)
        height = min(70 + capacity * 5, 100)
        
        # Tạo đối tượng TableItem
        table_item = TableItem(table_id, table_name, status, capacity, x, y, width, height)
        
        # Thêm vào scene và lưu trữ
        self.addItem(table_item)
        self.tables[table_id] = table_item
    
    def get_position_for_location(self, table_id, location):
        # Định vị trí đặt bàn dựa trên location và id
        if location == "Cửa sổ":
            if table_id % 2 == 0:
                return 70, 70 + (table_id // 2) * 120
            else:
                return 70, 130 + (table_id // 2) * 120
        elif location == "Giữa":
            offset = table_id - 3  # Bàn 3 và 4 thuộc khu vực giữa
            col = offset % 2
            row = offset // 2
            return 250 + col * 150, 200 + row * 100
        elif location == "Góc":
            offset = table_id - 5  # Bàn 5 và 6 thuộc khu vực góc
            return 620, 230 + offset * 120
        elif location == "Sân vườn":
            offset = table_id - 7  # Bàn 7 và 8 thuộc khu vực sân vườn
            col = offset % 2
            return 100 + col * 250, 430
        else:
            # Mặc định nếu không rơi vào các khu vực trên
            return 350, 300
    
    def update_table(self, table_id, status):
        if table_id in self.tables:
            self.tables[table_id].status = status
            self.tables[table_id].update_color()

class TableView(QWidget):
    def __init__(self, current_staff=None):
        super().__init__()
        
        self.current_staff = current_staff
        self.tables = []
        
        self.setup_ui()
        self.load_tables()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("QUẢN LÝ BÀN")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        
        refresh_button = QPushButton("Làm mới")
        refresh_button.setFixedSize(100, 30)
        refresh_button.clicked.connect(self.load_tables)
        
        add_table_button = QPushButton("Thêm bàn")
        add_table_button.setFixedSize(100, 30)
        add_table_button.clicked.connect(self.show_add_table_dialog)
        
        # Only enable add button for managers
        if self.current_staff and self.current_staff.role != "Quản lý":
            add_table_button.setEnabled(False)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(refresh_button)
        header_layout.addWidget(add_table_button)
        
        main_layout.addLayout(header_layout)
        
        # Cafe map view
        self.cafe_scene = CafeScene()
        self.cafe_scene.tableClicked.connect(self.handle_table_click)
        
        self.cafe_view = QGraphicsView(self.cafe_scene)
        self.cafe_view.setRenderHint(QPainter.Antialiasing)
        self.cafe_view.setMinimumHeight(600)
        
        main_layout.addWidget(self.cafe_view)
        
        # Legend
        legend_layout = QHBoxLayout()
        
        # Available
        available_color = QFrame()
        available_color.setFixedSize(20, 20)
        available_color.setStyleSheet("background-color: #4CAF50; border-radius: 3px;")
        legend_layout.addWidget(available_color)
        legend_layout.addWidget(QLabel("Trống"))
        
        legend_layout.addSpacing(20)
        
        # Occupied
        occupied_color = QFrame()
        occupied_color.setFixedSize(20, 20)
        occupied_color.setStyleSheet("background-color: #FF9800; border-radius: 3px;")
        legend_layout.addWidget(occupied_color)
        legend_layout.addWidget(QLabel("Đang phục vụ"))
        
        legend_layout.addSpacing(20)
        
        # Reserved
        reserved_color = QFrame()
        reserved_color.setFixedSize(20, 20)
        reserved_color.setStyleSheet("background-color: #9E9E9E; border-radius: 3px;")
        legend_layout.addWidget(reserved_color)
        legend_layout.addWidget(QLabel("Đã đặt trước"))
        
        legend_layout.addStretch()
        
        main_layout.addLayout(legend_layout)
    
    def load_tables(self):
        # Clear existing tables
        for table_id in list(self.cafe_scene.tables.keys()):
            self.cafe_scene.removeItem(self.cafe_scene.tables[table_id])
            self.cafe_scene.tables.pop(table_id)
        
        # Get tables from database
        self.tables = TableController.get_all_tables()
        
        # Add tables to the cafe map
        for table in self.tables:
            self.cafe_scene.add_table(
                table.id,
                table.name,
                table.status,
                table.capacity,
                table.location
            )
    
    def handle_table_click(self, table_id):
        # Find the table
        table = TableController.get_table_by_id(table_id)
        
        if not table:
            return
        
        if table.status == "trống":
            # Create new order if table is available
            self.create_new_order(table)
        else:
            # View existing order if table is occupied
            self.view_table_order(table)
    
    def create_new_order(self, table):
        # Create a confirmation dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Tạo đơn hàng mới cho {table.name}")
        dialog.setFixedSize(300, 200)
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel(f"Bạn muốn tạo đơn hàng mới cho {table.name}?"))
        layout.addSpacing(20)
        
        # Create buttons
        buttons_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Hủy")
        cancel_button.clicked.connect(dialog.reject)
        
        confirm_button = QPushButton("Tạo đơn hàng")
        confirm_button.setStyleSheet("background-color: #4CAF50; color: white;")
        confirm_button.clicked.connect(dialog.accept)
        
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(confirm_button)
        
        layout.addLayout(buttons_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            # Create new order
            if self.current_staff:
                order_id = OrderController.create_order(table.id, self.current_staff.id)
                
                if order_id:
                    QMessageBox.information(self, "Thành công", 
                                           f"Đã tạo đơn hàng mới cho {table.name}")
                    self.load_tables()
                    
                    # Switch to order view tab
                    self.parent().parent().setCurrentIndex(2)  # Index of order tab
                else:
                    QMessageBox.warning(self, "Lỗi", 
                                       f"Không thể tạo đơn hàng cho {table.name}")
            else:
                QMessageBox.warning(self, "Lỗi", "Bạn chưa đăng nhập")
    
    def view_table_order(self, table):
        # Get current order for this table
        orders = OrderController.get_orders_by_table(table.id)
        
        if not orders:
            QMessageBox.information(self, "Thông báo", 
                                  f"{table.name} đang được đặt trước hoặc không có đơn hàng nào")
            return
        
        # Switch to order view tab and show this order
        self.parent().parent().setCurrentIndex(2)  # Index of order tab
    
    def show_add_table_dialog(self):
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Thêm bàn mới")
        dialog.setFixedSize(300, 250)
        
        layout = QVBoxLayout(dialog)
        
        # Name
        layout.addWidget(QLabel("Tên bàn:"))
        name_input = QLineEdit()
        name_input.setPlaceholderText("Nhập tên bàn")
        layout.addWidget(name_input)
        
        # Capacity
        layout.addWidget(QLabel("Số chỗ ngồi:"))
        capacity_input = QSpinBox()
        capacity_input.setRange(1, 20)
        capacity_input.setValue(4)
        layout.addWidget(capacity_input)
        
        # Location
        layout.addWidget(QLabel("Vị trí:"))
        location_input = QComboBox()
        location_input.addItems(["Cửa sổ", "Giữa", "Góc", "Sân vườn", "Khác"])
        layout.addWidget(location_input)
        
        layout.addSpacing(20)
        
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
            capacity = capacity_input.value()
            location = location_input.currentText()
            
            if not name:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên bàn")
                return
            
            # Add table
            success = TableController.add_table(name, capacity, location)
            
            if success:
                QMessageBox.information(self, "Thành công", f"Đã thêm bàn {name}")
                self.load_tables()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể thêm bàn mới") 