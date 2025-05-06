from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLabel, QHeaderView,
                             QMessageBox, QDialog, QLineEdit, QFormLayout, QComboBox,
                             QDoubleSpinBox, QSpinBox, QGroupBox, QTabWidget, QCheckBox)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QIcon, QColor, QFont, QBrush

from app.controllers.inventory_controller import InventoryController
from app.controllers.menu_controller import MenuController

class AddEditInventoryDialog(QDialog):
    def __init__(self, parent=None, inventory_item=None):
        super().__init__(parent)
        self.inventory_item = inventory_item
        self.setWindowTitle("Thêm nguyên liệu mới" if not inventory_item else "Chỉnh sửa nguyên liệu")
        self.setMinimumWidth(400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Tên nguyên liệu
        self.name_input = QLineEdit()
        if self.inventory_item:
            self.name_input.setText(self.inventory_item.name)
        form_layout.addRow("Tên nguyên liệu:", self.name_input)
        
        # Số lượng
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setRange(0, 10000)
        self.quantity_input.setDecimals(2)
        if self.inventory_item:
            self.quantity_input.setValue(self.inventory_item.quantity)
        form_layout.addRow("Số lượng:", self.quantity_input)
        
        # Đơn vị
        self.unit_input = QComboBox()
        units = ["g", "kg", "ml", "l", "cái", "hộp", "chai", "gói"]
        self.unit_input.addItems(units)
        if self.inventory_item and self.inventory_item.unit in units:
            self.unit_input.setCurrentText(self.inventory_item.unit)
        form_layout.addRow("Đơn vị:", self.unit_input)
        
        # Nhà cung cấp
        self.supplier_input = QLineEdit()
        if self.inventory_item and self.inventory_item.supplier:
            self.supplier_input.setText(self.inventory_item.supplier)
        form_layout.addRow("Nhà cung cấp:", self.supplier_input)
        
        # Số lượng tối thiểu
        self.min_quantity_input = QDoubleSpinBox()
        self.min_quantity_input.setRange(0, 1000)
        self.min_quantity_input.setDecimals(2)
        if self.inventory_item:
            self.min_quantity_input.setValue(self.inventory_item.min_quantity)
        form_layout.addRow("Số lượng tối thiểu:", self.min_quantity_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("Hủy")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Lưu")
        self.save_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.save_btn.clicked.connect(self.save_inventory)
        
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.save_btn)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def save_inventory(self):
        name = self.name_input.text().strip()
        quantity = self.quantity_input.value()
        unit = self.unit_input.currentText()
        supplier = self.supplier_input.text().strip()
        min_quantity = self.min_quantity_input.value()
        
        if not name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên nguyên liệu")
            return
        
        if not self.inventory_item:
            # Thêm mới
            InventoryController.add_inventory_item(
                name=name,
                quantity=quantity,
                unit=unit,
                supplier=supplier if supplier else None,
                min_quantity=min_quantity
            )
        else:
            # Cập nhật
            InventoryController.update_inventory_item(
                self.inventory_item.id,
                name=name,
                quantity=quantity,
                unit=unit,
                supplier=supplier if supplier else None,
                min_quantity=min_quantity
            )
        
        self.accept()

class InventoryView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_inventory()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Tab widget cho các phần khác nhau
        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # Tab 1: Quản lý kho
        self.inventory_tab = QWidget()
        inventory_layout = QVBoxLayout(self.inventory_tab)
        
        # Tiêu đề và nút chức năng
        header_layout = QHBoxLayout()
        
        title_label = QLabel("QUẢN LÝ KHO HÀNG")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        
        self.add_btn = QPushButton("Thêm nguyên liệu")
        self.add_btn.setIcon(QIcon.fromTheme("list-add"))
        self.add_btn.clicked.connect(self.add_inventory)
        
        self.refresh_btn = QPushButton("Làm mới")
        self.refresh_btn.setIcon(QIcon.fromTheme("view-refresh"))
        self.refresh_btn.clicked.connect(self.load_inventory)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.add_btn)
        header_layout.addWidget(self.refresh_btn)
        
        inventory_layout.addLayout(header_layout)
        
        # Bảng hiển thị kho
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(7)
        self.inventory_table.setHorizontalHeaderLabels(["ID", "Tên nguyên liệu", "Số lượng", "Đơn vị", "Nhà cung cấp", "Cập nhật lần cuối", "Trạng thái"])
        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.inventory_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Context menu hoặc các nút điều khiển
        button_layout = QHBoxLayout()
        
        self.edit_btn = QPushButton("Sửa")
        self.edit_btn.clicked.connect(self.edit_inventory)
        
        self.delete_btn = QPushButton("Xóa")
        self.delete_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.delete_btn.clicked.connect(self.delete_inventory)
        
        self.update_quantity_btn = QPushButton("Cập nhật số lượng")
        self.update_quantity_btn.clicked.connect(self.update_quantity)
        
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.update_quantity_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.delete_btn)
        
        inventory_layout.addWidget(self.inventory_table)
        inventory_layout.addLayout(button_layout)
        
        # Tab 2: Cảnh báo số lượng
        self.alerts_tab = QWidget()
        alerts_layout = QVBoxLayout(self.alerts_tab)
        
        alerts_header = QLabel("CẢNH BÁO NGUYÊN LIỆU SẮP HẾT")
        alerts_header.setFont(QFont("Arial", 16, QFont.Bold))
        alerts_layout.addWidget(alerts_header)
        
        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(5)
        self.alerts_table.setHorizontalHeaderLabels(["Tên nguyên liệu", "Hiện có", "Tối thiểu", "Đơn vị", "Trạng thái"])
        self.alerts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        alerts_layout.addWidget(self.alerts_table)
        
        self.load_alerts_btn = QPushButton("Kiểm tra nguyên liệu sắp hết")
        self.load_alerts_btn.clicked.connect(self.load_alerts)
        alerts_layout.addWidget(self.load_alerts_btn)
        
        # Tab 3: Nguyên liệu cho món
        self.recipe_tab = QWidget()
        recipe_layout = QVBoxLayout(self.recipe_tab)
        
        recipe_header = QLabel("NGUYÊN LIỆU CHO MÓN")
        recipe_header.setFont(QFont("Arial", 16, QFont.Bold))
        recipe_layout.addWidget(recipe_header)
        
        form_layout = QFormLayout()
        
        self.menu_combo = QComboBox()
        self.menu_combo.currentIndexChanged.connect(self.load_recipe)
        form_layout.addRow("Chọn món:", self.menu_combo)
        
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 100)
        self.quantity_spin.setValue(1)
        self.quantity_spin.valueChanged.connect(self.calculate_ingredients)
        form_layout.addRow("Số lượng:", self.quantity_spin)
        
        recipe_layout.addLayout(form_layout)
        
        # Thêm nguyên liệu vào công thức
        add_recipe_group = QGroupBox("Thêm/Sửa nguyên liệu vào công thức")
        add_recipe_layout = QVBoxLayout(add_recipe_group)
        
        add_form = QFormLayout()
        
        self.ingredient_combo = QComboBox()
        add_form.addRow("Nguyên liệu:", self.ingredient_combo)
        
        self.ingredient_quantity = QDoubleSpinBox()
        self.ingredient_quantity.setRange(0.01, 1000)
        self.ingredient_quantity.setDecimals(2)
        self.ingredient_quantity.setValue(1)
        add_form.addRow("Số lượng:", self.ingredient_quantity)
        
        add_recipe_layout.addLayout(add_form)
        
        add_button = QPushButton("Thêm vào công thức")
        add_button.clicked.connect(self.add_to_recipe)
        add_recipe_layout.addWidget(add_button)
        
        recipe_layout.addWidget(add_recipe_group)
        
        # Bảng hiển thị công thức hiện tại
        recipe_header = QLabel("Công thức hiện tại")
        recipe_header.setFont(QFont("Arial", 12, QFont.Bold))
        recipe_layout.addWidget(recipe_header)
        
        self.recipe_table = QTableWidget()
        self.recipe_table.setColumnCount(4)
        self.recipe_table.setHorizontalHeaderLabels(["Nguyên liệu", "Số lượng", "Đơn vị", ""])
        self.recipe_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        recipe_layout.addWidget(self.recipe_table)
        
        # Bảng hiển thị nguyên liệu cần dùng
        ingredients_header = QLabel("Nguyên liệu cần dùng cho đơn hàng")
        ingredients_header.setFont(QFont("Arial", 12, QFont.Bold))
        recipe_layout.addWidget(ingredients_header)
        
        self.ingredients_table = QTableWidget()
        self.ingredients_table.setColumnCount(4)
        self.ingredients_table.setHorizontalHeaderLabels(["Nguyên liệu", "Số lượng", "Đơn vị", "Tình trạng"])
        self.ingredients_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        recipe_layout.addWidget(self.ingredients_table)
        
        # Tab 4: Phân tích sử dụng
        self.usage_tab = QWidget()
        usage_layout = QVBoxLayout(self.usage_tab)
        
        usage_header = QLabel("PHÂN TÍCH SỬ DỤNG NGUYÊN LIỆU")
        usage_header.setFont(QFont("Arial", 16, QFont.Bold))
        usage_layout.addWidget(usage_header)
        
        # Chức năng phân tích sẽ được phát triển sau
        usage_layout.addWidget(QLabel("Tính năng đang được phát triển..."))
        
        # Thêm các tab vào tab widget
        self.tab_widget.addTab(self.inventory_tab, "Quản lý kho")
        self.tab_widget.addTab(self.alerts_tab, "Cảnh báo nguyên liệu")
        self.tab_widget.addTab(self.recipe_tab, "Công thức")
        self.tab_widget.addTab(self.usage_tab, "Phân tích sử dụng")
        
        main_layout.addWidget(self.tab_widget)
        
        # Tải dữ liệu kho hàng
        self.load_inventory()
        
        # Nạp danh sách nguyên liệu cho combobox
        self.load_inventory_items()
        
        # Tải menu items (chỉ tải sau khi đã tạo xong recipe_table)
        self.load_menu_items()
    
    def load_inventory(self):
        """Tải dữ liệu kho hàng vào bảng"""
        self.inventory_table.setRowCount(0)
        
        inventory_items = InventoryController.get_all_inventory_items()
        
        for row, item in enumerate(inventory_items):
            self.inventory_table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(item.id))
            self.inventory_table.setItem(row, 0, id_item)
            
            # Tên
            name_item = QTableWidgetItem(item.name)
            self.inventory_table.setItem(row, 1, name_item)
            
            # Số lượng
            quantity_item = QTableWidgetItem(f"{item.quantity:.2f}")
            self.inventory_table.setItem(row, 2, quantity_item)
            
            # Đơn vị
            unit_item = QTableWidgetItem(item.unit)
            self.inventory_table.setItem(row, 3, unit_item)
            
            # Nhà cung cấp
            supplier_item = QTableWidgetItem(item.supplier if item.supplier else "")
            self.inventory_table.setItem(row, 4, supplier_item)
            
            # Thời gian cập nhật
            last_update = item.last_update.strftime("%d/%m/%Y %H:%M") if item.last_update else ""
            update_item = QTableWidgetItem(last_update)
            self.inventory_table.setItem(row, 5, update_item)
            
            # Trạng thái
            status_text = "Đủ hàng"
            status_color = QColor("#4CAF50")  # Xanh lá
            
            if item.quantity <= 0:
                status_text = "Hết hàng"
                status_color = QColor("#f44336")  # Đỏ
            elif item.quantity <= item.min_quantity:
                status_text = "Sắp hết"
                status_color = QColor("#FFC107")  # Vàng
            
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(QBrush(status_color))
            status_item.setTextAlignment(Qt.AlignCenter)
            self.inventory_table.setItem(row, 6, status_item)
    
    def add_inventory(self):
        """Mở dialog thêm nguyên liệu mới"""
        dialog = AddEditInventoryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_inventory()
    
    def edit_inventory(self):
        """Chỉnh sửa nguyên liệu đã chọn"""
        selected_row = self.inventory_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một nguyên liệu để chỉnh sửa")
            return
        
        inventory_id = int(self.inventory_table.item(selected_row, 0).text())
        inventory_item = InventoryController.get_inventory_item(inventory_id)
        
        if not inventory_item:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy nguyên liệu này")
            return
        
        dialog = AddEditInventoryDialog(self, inventory_item)
        if dialog.exec_() == QDialog.Accepted:
            self.load_inventory()
    
    def delete_inventory(self):
        """Xóa nguyên liệu đã chọn"""
        selected_row = self.inventory_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một nguyên liệu để xóa")
            return
        
        inventory_id = int(self.inventory_table.item(selected_row, 0).text())
        
        reply = QMessageBox.question(self, "Xác nhận xóa", 
                                     "Bạn có chắc chắn muốn xóa nguyên liệu này?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if InventoryController.delete_inventory_item(inventory_id):
                self.load_inventory()
                QMessageBox.information(self, "Thành công", "Đã xóa nguyên liệu")
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể xóa nguyên liệu")
    
    def update_quantity(self):
        """Cập nhật số lượng nguyên liệu"""
        selected_row = self.inventory_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một nguyên liệu để cập nhật")
            return
        
        inventory_id = int(self.inventory_table.item(selected_row, 0).text())
        current_quantity = float(self.inventory_table.item(selected_row, 2).text())
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Cập nhật số lượng")
        layout = QVBoxLayout()
        
        form = QFormLayout()
        quantity_input = QDoubleSpinBox()
        quantity_input.setRange(0, 10000)
        quantity_input.setDecimals(2)
        quantity_input.setValue(current_quantity)
        form.addRow("Số lượng mới:", quantity_input)
        
        layout.addLayout(form)
        
        buttons = QHBoxLayout()
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(dialog.reject)
        
        save_btn = QPushButton("Lưu")
        save_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        save_btn.clicked.connect(dialog.accept)
        
        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)
        
        layout.addLayout(buttons)
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            new_quantity = quantity_input.value()
            if InventoryController.update_inventory_quantity(inventory_id, new_quantity):
                self.load_inventory()
                QMessageBox.information(self, "Thành công", "Đã cập nhật số lượng")
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể cập nhật số lượng")
    
    def load_alerts(self):
        """Tải danh sách cảnh báo nguyên liệu sắp hết"""
        self.alerts_table.setRowCount(0)
        
        low_stock_items = InventoryController.get_low_stock_items()
        
        for row, item in enumerate(low_stock_items):
            self.alerts_table.insertRow(row)
            
            # Tên
            name_item = QTableWidgetItem(item.name)
            self.alerts_table.setItem(row, 0, name_item)
            
            # Hiện có
            quantity_item = QTableWidgetItem(f"{item.quantity:.2f}")
            self.alerts_table.setItem(row, 1, quantity_item)
            
            # Tối thiểu
            min_quantity_item = QTableWidgetItem(f"{item.min_quantity:.2f}")
            self.alerts_table.setItem(row, 2, min_quantity_item)
            
            # Đơn vị
            unit_item = QTableWidgetItem(item.unit)
            self.alerts_table.setItem(row, 3, unit_item)
            
            # Trạng thái
            status_text = "Sắp hết"
            status_color = QColor("#FFC107")  # Vàng
            
            if item.quantity <= 0:
                status_text = "Hết hàng"
                status_color = QColor("#f44336")  # Đỏ
            
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(QBrush(status_color))
            status_item.setTextAlignment(Qt.AlignCenter)
            self.alerts_table.setItem(row, 4, status_item)
    
    def load_menu_items(self):
        """Tải danh sách các món vào combobox"""
        self.menu_combo.clear()
        
        # Dùng phương thức get_all_menu_items mới thêm vào MenuController
        menu_items = MenuController.get_all_menu_items()
        
        if menu_items:
            for item in menu_items:
                self.menu_combo.addItem(item.name, item.id)
            
            # Kích hoạt sự kiện currentIndexChanged sau khi đã thêm tất cả items
            if self.menu_combo.count() > 0:
                # Chắc chắn có kết nối với hàm load_recipe
                try:
                    self.menu_combo.currentIndexChanged.disconnect()
                except:
                    pass
                self.menu_combo.currentIndexChanged.connect(self.load_recipe)
                
                # Chọn item đầu tiên và load recipe
                self.menu_combo.setCurrentIndex(0)
                self.load_recipe()
        else:
            print("Không tìm thấy món nào trong menu")
    
    def load_recipe(self):
        """Tải danh sách nguyên liệu cho món đã chọn"""
        # Kiểm tra xem recipe_table đã được khởi tạo chưa
        if not hasattr(self, 'recipe_table'):
            print("Warning: recipe_table chưa được khởi tạo")
            return
            
        self.recipe_table.setRowCount(0)
        
        if self.menu_combo.count() == 0:
            return
            
        menu_item_id = self.menu_combo.currentData()
        if menu_item_id is None:
            return
            
        # Lấy công thức hiện tại
        recipe = InventoryController.get_recipe(menu_item_id)
        
        # Hiển thị lên bảng
        for row, item in enumerate(recipe):
            self.recipe_table.insertRow(row)
            
            # Tên nguyên liệu
            name_item = QTableWidgetItem(item["name"])
            self.recipe_table.setItem(row, 0, name_item)
            
            # Số lượng
            quantity_item = QTableWidgetItem(f"{item['quantity']:.2f}")
            self.recipe_table.setItem(row, 1, quantity_item)
            
            # Đơn vị
            unit_item = QTableWidgetItem(item["unit"])
            self.recipe_table.setItem(row, 2, unit_item)
            
            # Xóa nút
            delete_btn = QPushButton("Xóa")
            delete_btn.setStyleSheet("background-color: #f44336; color: white;")
            
            # Sử dụng closure để giữ giá trị hiện tại của menu_item_id và inventory_id
            def create_remove_callback(m_id, i_id):
                return lambda: self.remove_from_recipe(m_id, i_id)
                
            delete_btn.clicked.connect(create_remove_callback(menu_item_id, item["inventory_id"]))
            self.recipe_table.setCellWidget(row, 3, delete_btn)
        
        # Cập nhật bảng nguyên liệu cần dùng
        self.calculate_ingredients()
    
    def remove_from_recipe(self, menu_item_id, inventory_id):
        """Xóa nguyên liệu khỏi công thức"""
        reply = QMessageBox.question(self, "Xác nhận xóa", 
                                    "Bạn có chắc chắn muốn xóa nguyên liệu này khỏi công thức?",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if InventoryController.remove_recipe_ingredient(menu_item_id, inventory_id):
                self.load_recipe()
                QMessageBox.information(self, "Thành công", "Đã xóa nguyên liệu khỏi công thức")
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể xóa nguyên liệu khỏi công thức")
    
    def calculate_ingredients(self):
        """Tính toán nguyên liệu cần dùng cho món đã chọn"""
        # Kiểm tra xem ingredients_table đã được khởi tạo chưa
        if not hasattr(self, 'ingredients_table'):
            print("Warning: ingredients_table chưa được khởi tạo")
            return
            
        self.ingredients_table.setRowCount(0)
        
        if self.menu_combo.count() == 0:
            return
            
        menu_item_id = self.menu_combo.currentData()
        if menu_item_id is None:
            return
            
        quantity = self.quantity_spin.value()
        
        # Lấy danh sách nguyên liệu cần dùng
        ingredients = InventoryController.calculate_required_ingredients(menu_item_id, quantity)
        
        # Hiển thị lên bảng
        for row, item in enumerate(ingredients):
            self.ingredients_table.insertRow(row)
            
            # Tên nguyên liệu
            name_item = QTableWidgetItem(item["name"])
            self.ingredients_table.setItem(row, 0, name_item)
            
            # Số lượng
            quantity_item = QTableWidgetItem(f"{item['quantity']:.2f}")
            self.ingredients_table.setItem(row, 1, quantity_item)
            
            # Đơn vị
            unit_item = QTableWidgetItem(item["unit"])
            self.ingredients_table.setItem(row, 2, unit_item)
            
            # Kiểm tra tình trạng tồn kho
            inventory_items = InventoryController.get_all_inventory_items()
            inventory_map = {inv.name: inv for inv in inventory_items}
            
            # Tình trạng
            status_text = "Đủ hàng"
            status_color = QColor("#4CAF50")  # Xanh lá
            
            if item["name"] in inventory_map:
                inventory = inventory_map[item["name"]]
                if inventory.quantity <= 0:
                    status_text = "Hết hàng"
                    status_color = QColor("#f44336")  # Đỏ
                elif inventory.quantity < item["quantity"]:
                    status_text = "Thiếu hàng"
                    status_color = QColor("#f44336")  # Đỏ
                elif inventory.quantity <= inventory.min_quantity:
                    status_text = "Sắp hết"
                    status_color = QColor("#FFC107")  # Vàng
            else:
                status_text = "Không có"
                status_color = QColor("#f44336")  # Đỏ
            
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(QBrush(status_color))
            status_item.setTextAlignment(Qt.AlignCenter)
            self.ingredients_table.setItem(row, 3, status_item)
    
    def load_inventory_items(self):
        """Tải danh sách nguyên liệu vào combobox"""
        self.ingredient_combo.clear()
        
        inventory_items = InventoryController.get_all_inventory_items()
        
        for item in inventory_items:
            self.ingredient_combo.addItem(item.name, item.id)
    
    def add_to_recipe(self):
        """Thêm nguyên liệu vào công thức"""
        menu_item_id = self.menu_combo.currentData()
        inventory_id = self.ingredient_combo.currentData()
        quantity = self.ingredient_quantity.value()
        
        if not menu_item_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một món từ menu")
            return
        
        if not inventory_id:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một nguyên liệu")
            return
        
        if InventoryController.add_recipe_ingredient(menu_item_id, inventory_id, quantity):
            QMessageBox.information(self, "Thành công", "Đã thêm nguyên liệu vào công thức")
            self.load_recipe()
        else:
            QMessageBox.warning(self, "Lỗi", "Không thể thêm nguyên liệu vào công thức")
    
    def on_tab_changed(self, index):
        """Xử lý khi chuyển tab"""
        # Nếu chuyển đến tab công thức (index 2)
        if index == 2:
            # Kiểm tra xem các thuộc tính cần thiết đã được khởi tạo chưa
            if hasattr(self, 'menu_combo') and hasattr(self, 'ingredient_combo') and \
               hasattr(self, 'recipe_table') and hasattr(self, 'ingredients_table'):
                self.load_menu_items()
                self.load_inventory_items()
            else:
                print("Warning: Một số thành phần UI chưa được khởi tạo khi chuyển tab")
        # Nếu chuyển đến tab cảnh báo (index 1) 
        elif index == 1:
            if hasattr(self, 'alerts_table'):
                self.load_alerts()
            else:
                print("Warning: alerts_table chưa được khởi tạo khi chuyển tab") 