from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QComboBox, QLineEdit, QDialog, QFormLayout, QDoubleSpinBox,
                             QTextEdit, QMessageBox, QGroupBox, QRadioButton, QSplitter)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QPixmap

from app.controllers.menu_controller import MenuController

class MenuView(QWidget):
    def __init__(self, current_staff=None):
        super().__init__()
        
        self.current_staff = current_staff
        self.selected_category = None
        self.menu_items = []
        
        self.setup_ui()
        self.load_categories()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("QUẢN LÝ THỰC ĐƠN")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tìm kiếm món...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self.search_items)
        
        refresh_button = QPushButton("Làm mới")
        refresh_button.setFixedSize(100, 30)
        refresh_button.clicked.connect(self.load_menu_items)
        
        add_item_button = QPushButton("Thêm món")
        add_item_button.setFixedSize(100, 30)
        add_item_button.clicked.connect(self.show_add_item_dialog)
        
        # Only enable add button for managers
        if self.current_staff and self.current_staff.role != "Quản lý":
            add_item_button.setEnabled(False)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.search_input)
        header_layout.addWidget(refresh_button)
        header_layout.addWidget(add_item_button)
        
        main_layout.addLayout(header_layout)
        
        # Categories and menu items
        content_layout = QHBoxLayout()
        
        # Categories
        categories_group = QGroupBox("Danh mục")
        categories_layout = QVBoxLayout(categories_group)
        
        self.category_combo = QComboBox()
        self.category_combo.currentIndexChanged.connect(self.on_category_changed)
        categories_layout.addWidget(self.category_combo)
        
        categories_layout.addStretch()
        
        # Menu Items Table
        menu_items_group = QGroupBox("Danh sách món")
        menu_items_layout = QVBoxLayout(menu_items_group)
        
        self.menu_table = QTableWidget()
        self.menu_table.setColumnCount(5)
        self.menu_table.setHorizontalHeaderLabels(["ID", "Tên món", "Giá", "Danh mục", "Trạng thái"])
        self.menu_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.menu_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.menu_table.verticalHeader().setVisible(False)
        self.menu_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.menu_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.menu_table.doubleClicked.connect(self.on_item_double_clicked)
        
        menu_items_layout.addWidget(self.menu_table)
        
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.addWidget(categories_group)
        content_splitter.addWidget(menu_items_group)
        content_splitter.setSizes([200, 800])
        
        main_layout.addWidget(content_splitter)
    
    def load_categories(self):
        # Clear existing categories
        self.category_combo.clear()
        
        # Add "All" option
        self.category_combo.addItem("Tất cả", None)
        
        # Get categories from database
        categories = MenuController.get_all_categories()
        
        for category in categories:
            self.category_combo.addItem(category.name, category.id)
    
    def load_menu_items(self):
        # Clear search input
        self.search_input.clear()
        
        # Get selected category ID
        category_id = self.category_combo.currentData()
        
        # Get menu items
        if category_id is None:
            self.menu_items = MenuController.get_all_items()
        else:
            self.menu_items = MenuController.get_items_by_category(category_id)
        
        self.display_menu_items()
    
    def display_menu_items(self):
        # Clear existing items
        self.menu_table.setRowCount(0)
        
        # Add items to table
        for row, item in enumerate(self.menu_items):
            self.menu_table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(item.id))
            self.menu_table.setItem(row, 0, id_item)
            
            # Name
            name_item = QTableWidgetItem(item.name)
            self.menu_table.setItem(row, 1, name_item)
            
            # Price
            price_item = QTableWidgetItem(f"{item.price:,.0f} đ")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.menu_table.setItem(row, 2, price_item)
            
            # Category
            category_name = item.category.name if item.category else "Không phân loại"
            category_item = QTableWidgetItem(category_name)
            self.menu_table.setItem(row, 3, category_item)
            
            # Status
            status_text = "Có sẵn" if item.is_available else "Hết hàng"
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(Qt.green if item.is_available else Qt.red)
            self.menu_table.setItem(row, 4, status_item)
    
    def on_category_changed(self, index):
        self.load_menu_items()
    
    def search_items(self, keyword):
        if not keyword:
            self.load_menu_items()
            return
        
        self.menu_items = MenuController.search_items(keyword)
        self.display_menu_items()
    
    def on_item_double_clicked(self, index):
        row = index.row()
        item_id = int(self.menu_table.item(row, 0).text())
        
        # Find the item in our list
        selected_item = next((item for item in self.menu_items if item.id == item_id), None)
        
        if selected_item:
            self.show_edit_item_dialog(selected_item)
    
    def show_add_item_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Thêm món mới")
        dialog.setFixedWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        
        # Name
        name_input = QLineEdit()
        name_input.setPlaceholderText("Nhập tên món")
        form_layout.addRow("Tên món:", name_input)
        
        # Price
        price_input = QDoubleSpinBox()
        price_input.setRange(0, 1000000)
        price_input.setSingleStep(1000)
        price_input.setValue(30000)
        price_input.setSuffix(" đ")
        form_layout.addRow("Giá:", price_input)
        
        # Category
        category_combo = QComboBox()
        categories = MenuController.get_all_categories()
        for category in categories:
            category_combo.addItem(category.name, category.id)
        form_layout.addRow("Danh mục:", category_combo)
        
        # Description
        description_input = QTextEdit()
        description_input.setPlaceholderText("Mô tả món (không bắt buộc)")
        description_input.setMaximumHeight(100)
        form_layout.addRow("Mô tả:", description_input)
        
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
            price = price_input.value()
            category_id = category_combo.currentData()
            description = description_input.toPlainText().strip() or None
            
            if not name:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên món")
                return
            
            # Add item
            success = MenuController.add_item(name, price, category_id, description)
            
            if success:
                QMessageBox.information(self, "Thành công", f"Đã thêm món {name}")
                self.load_menu_items()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể thêm món mới")
    
    def show_edit_item_dialog(self, item):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Chỉnh sửa: {item.name}")
        dialog.setFixedWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        
        # Name
        name_input = QLineEdit(item.name)
        form_layout.addRow("Tên món:", name_input)
        
        # Price
        price_input = QDoubleSpinBox()
        price_input.setRange(0, 1000000)
        price_input.setSingleStep(1000)
        price_input.setValue(item.price)
        price_input.setSuffix(" đ")
        form_layout.addRow("Giá:", price_input)
        
        # Category
        category_combo = QComboBox()
        categories = MenuController.get_all_categories()
        selected_index = 0
        for i, category in enumerate(categories):
            category_combo.addItem(category.name, category.id)
            if category.id == item.category_id:
                selected_index = i
        category_combo.setCurrentIndex(selected_index)
        form_layout.addRow("Danh mục:", category_combo)
        
        # Description
        description_input = QTextEdit()
        description_input.setText(item.description or "")
        description_input.setMaximumHeight(100)
        form_layout.addRow("Mô tả:", description_input)
        
        # Status
        status_group = QGroupBox("Trạng thái")
        status_layout = QHBoxLayout(status_group)
        
        available_radio = QRadioButton("Có sẵn")
        unavailable_radio = QRadioButton("Hết hàng")
        
        if item.is_available:
            available_radio.setChecked(True)
        else:
            unavailable_radio.setChecked(True)
        
        status_layout.addWidget(available_radio)
        status_layout.addWidget(unavailable_radio)
        
        form_layout.addRow(status_group)
        
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
        delete_button.clicked.connect(lambda: self.delete_item(item, dialog))
        
        buttons_layout.addWidget(delete_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(save_button)
        
        layout.addLayout(buttons_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            name = name_input.text().strip()
            price = price_input.value()
            category_id = category_combo.currentData()
            description = description_input.toPlainText().strip() or None
            is_available = available_radio.isChecked()
            
            if not name:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên món")
                return
            
            # Update item
            success = MenuController.update_item(
                item.id,
                name=name,
                price=price,
                category_id=category_id,
                description=description,
                is_available=is_available
            )
            
            if success:
                QMessageBox.information(self, "Thành công", f"Đã cập nhật món {name}")
                self.load_menu_items()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể cập nhật món")
    
    def delete_item(self, item, parent_dialog=None):
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn xóa món '{item.name}'?\nHành động này không thể hoàn tác.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Delete item
            success = MenuController.delete_item(item.id)
            
            if success:
                QMessageBox.information(self, "Thành công", f"Đã xóa món {item.name}")
                if parent_dialog:
                    parent_dialog.reject()
                self.load_menu_items()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể xóa món") 