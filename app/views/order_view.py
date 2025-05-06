from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                             QComboBox, QLineEdit, QDialog, QSpinBox, QGroupBox,
                             QMessageBox, QSplitter, QTabWidget, QTreeWidget, QTreeWidgetItem,
                             QFormLayout, QDoubleSpinBox, QTextEdit, QFrame)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QColor, QPixmap

from app.controllers.order_controller import OrderController
from app.controllers.table_controller import TableController
from app.controllers.menu_controller import MenuController
from datetime import datetime

class OrderView(QWidget):
    def __init__(self, current_staff=None):
        super().__init__()
        
        self.current_staff = current_staff
        self.current_orders = []
        self.selected_order_id = None
        self.selected_order_details = None
        
        self.setup_ui()
        self.load_orders()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("QUẢN LÝ ĐƠN HÀNG")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        
        refresh_button = QPushButton("Làm mới")
        refresh_button.setFixedSize(100, 30)
        refresh_button.clicked.connect(self.load_orders)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(refresh_button)
        
        main_layout.addLayout(header_layout)
        
        # Main content splitter
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Order list
        order_list_widget = QWidget()
        order_list_layout = QVBoxLayout(order_list_widget)
        
        # Order table
        self.order_table = QTableWidget()
        self.order_table.setColumnCount(5)
        self.order_table.setHorizontalHeaderLabels(["ID", "Bàn", "Thời gian", "Trạng thái", "Tổng tiền"])
        self.order_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.order_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.order_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.order_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.order_table.verticalHeader().setVisible(False)
        self.order_table.clicked.connect(self.on_order_selected)
        
        order_list_layout.addWidget(QLabel("Danh sách đơn hàng đang hoạt động:"))
        order_list_layout.addWidget(self.order_table)
        
        # Right side - Order details
        order_details_widget = QWidget()
        order_details_layout = QVBoxLayout(order_details_widget)
        
        # Order info
        self.order_info_group = QGroupBox("Thông tin đơn hàng")
        order_info_layout = QFormLayout(self.order_info_group)
        
        self.order_id_label = QLabel("--")
        self.table_label = QLabel("--")
        self.time_label = QLabel("--")
        self.staff_label = QLabel("--")
        self.status_label = QLabel("--")
        
        order_info_layout.addRow("Mã đơn hàng:", self.order_id_label)
        order_info_layout.addRow("Bàn:", self.table_label)
        order_info_layout.addRow("Thời gian:", self.time_label)
        order_info_layout.addRow("Nhân viên:", self.staff_label)
        order_info_layout.addRow("Trạng thái:", self.status_label)
        
        # Order items
        self.order_items_group = QGroupBox("Chi tiết đơn hàng")
        order_items_layout = QVBoxLayout(self.order_items_group)
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(["Tên món", "Giá", "Số lượng", "Thành tiền", "Ghi chú"])
        self.items_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.items_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.items_table.verticalHeader().setVisible(False)
        
        # Buttons for managing items
        items_button_layout = QHBoxLayout()
        
        self.add_item_button = QPushButton("Thêm món")
        self.add_item_button.clicked.connect(self.show_add_item_dialog)
        
        self.edit_item_button = QPushButton("Sửa số lượng")
        self.edit_item_button.clicked.connect(self.show_edit_item_dialog)
        
        items_button_layout.addWidget(self.add_item_button)
        items_button_layout.addWidget(self.edit_item_button)
        
        order_items_layout.addWidget(self.items_table)
        order_items_layout.addLayout(items_button_layout)
        
        # Order total and actions
        self.order_total_group = QGroupBox("Tổng cộng")
        order_total_layout = QFormLayout(self.order_total_group)
        
        self.subtotal_label = QLabel("0 đ")
        self.discount_label = QLabel("0 đ")
        self.total_label = QLabel("0 đ")
        self.total_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        order_total_layout.addRow("Tạm tính:", self.subtotal_label)
        order_total_layout.addRow("Giảm giá:", self.discount_label)
        order_total_layout.addRow("Tổng cộng:", self.total_label)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.complete_button = QPushButton("Thanh toán")
        self.complete_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.complete_button.clicked.connect(self.show_payment_dialog)
        
        self.cancel_button = QPushButton("Hủy đơn")
        self.cancel_button.setStyleSheet("background-color: #f44336; color: white;")
        self.cancel_button.clicked.connect(self.cancel_order)
        
        action_layout.addWidget(self.cancel_button)
        action_layout.addStretch()
        action_layout.addWidget(self.complete_button)
        
        # Add all widgets to order details layout
        order_details_layout.addWidget(self.order_info_group)
        order_details_layout.addWidget(self.order_items_group)
        order_details_layout.addWidget(self.order_total_group)
        order_details_layout.addLayout(action_layout)
        
        # Add to splitter
        content_splitter.addWidget(order_list_widget)
        content_splitter.addWidget(order_details_widget)
        content_splitter.setSizes([400, 600])
        
        main_layout.addWidget(content_splitter)
        
        # Disable details initially
        self.toggle_details_enabled(False)
    
    def load_orders(self):
        # Get all active orders
        self.current_orders = OrderController.get_current_orders()
        
        # Clear table
        self.order_table.setRowCount(0)
        
        # Add orders to table
        for row, order in enumerate(self.current_orders):
            self.order_table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(order.id))
            self.order_table.setItem(row, 0, id_item)
            
            # Table
            table_name = order.table.name if order.table else "--"
            table_item = QTableWidgetItem(table_name)
            self.order_table.setItem(row, 1, table_item)
            
            # Time
            time_str = order.order_time.strftime("%H:%M:%S %d/%m/%Y")
            time_item = QTableWidgetItem(time_str)
            self.order_table.setItem(row, 2, time_item)
            
            # Status
            status_item = QTableWidgetItem(order.status)
            if order.status == "chờ xử lý":
                status_item.setForeground(QColor("#FF9800"))  # Orange
            elif order.status == "đang phục vụ":
                status_item.setForeground(QColor("#2196F3"))  # Blue
            elif order.status == "đã thanh toán":
                status_item.setForeground(QColor("#4CAF50"))  # Green
            else:  # Cancelled
                status_item.setForeground(QColor("#f44336"))  # Red
            self.order_table.setItem(row, 3, status_item)
            
            # Total
            total_item = QTableWidgetItem(f"{order.final_amount:,.0f} đ")
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.order_table.setItem(row, 4, total_item)
        
        # Clear current selection
        self.selected_order_id = None
        self.selected_order_details = None
        self.clear_order_details()
        self.toggle_details_enabled(False)
    
    def on_order_selected(self, index):
        row = index.row()
        order_id = int(self.order_table.item(row, 0).text())
        
        self.selected_order_id = order_id
        self.load_order_details()
    
    def load_order_details(self):
        if not self.selected_order_id:
            return
        
        # Get order details
        self.selected_order_details = OrderController.get_order_details(self.selected_order_id)
        
        if not self.selected_order_details:
            self.clear_order_details()
            self.toggle_details_enabled(False)
            return
        
        # Enable details
        self.toggle_details_enabled(True)
        
        # Update order info
        self.order_id_label.setText(str(self.selected_order_details['order_id']))
        self.table_label.setText(self.selected_order_details['table_name'] or "--")
        
        time_str = self.selected_order_details['order_time'].strftime("%H:%M:%S %d/%m/%Y")
        self.time_label.setText(time_str)
        
        self.staff_label.setText(self.selected_order_details['staff_name'] or "--")
        self.status_label.setText(self.selected_order_details['status'])
        
        # Update items table
        self.items_table.setRowCount(0)
        
        for row, item in enumerate(self.selected_order_details['items']):
            self.items_table.insertRow(row)
            
            # Name
            name_item = QTableWidgetItem(item['name'])
            self.items_table.setItem(row, 0, name_item)
            
            # Price
            price_item = QTableWidgetItem(f"{item['price']:,.0f} đ")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.items_table.setItem(row, 1, price_item)
            
            # Quantity
            quantity_item = QTableWidgetItem(str(item['quantity']))
            quantity_item.setTextAlignment(Qt.AlignCenter)
            self.items_table.setItem(row, 2, quantity_item)
            
            # Subtotal
            subtotal_item = QTableWidgetItem(f"{item['subtotal']:,.0f} đ")
            subtotal_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.items_table.setItem(row, 3, subtotal_item)
            
            # Note
            note_item = QTableWidgetItem(item['note'] or "")
            self.items_table.setItem(row, 4, note_item)
        
        # Update totals
        self.subtotal_label.setText(f"{self.selected_order_details['total_amount']:,.0f} đ")
        self.discount_label.setText(f"{self.selected_order_details['discount']:,.0f} đ")
        self.total_label.setText(f"{self.selected_order_details['final_amount']:,.0f} đ")
        
        # Special handling for completed orders
        if self.selected_order_details['status'] == "đã thanh toán":
            self.complete_button.setEnabled(False)
            self.add_item_button.setEnabled(False)
            self.edit_item_button.setEnabled(False)
            self.cancel_button.setEnabled(False)
        else:
            self.complete_button.setEnabled(True)
            self.add_item_button.setEnabled(True)
            self.edit_item_button.setEnabled(True)
            self.cancel_button.setEnabled(True)
    
    def clear_order_details(self):
        # Clear order info
        self.order_id_label.setText("--")
        self.table_label.setText("--")
        self.time_label.setText("--")
        self.staff_label.setText("--")
        self.status_label.setText("--")
        
        # Clear items table
        self.items_table.setRowCount(0)
        
        # Clear totals
        self.subtotal_label.setText("0 đ")
        self.discount_label.setText("0 đ")
        self.total_label.setText("0 đ")
    
    def toggle_details_enabled(self, enabled):
        self.order_info_group.setEnabled(enabled)
        self.order_items_group.setEnabled(enabled)
        self.order_total_group.setEnabled(enabled)
        self.complete_button.setEnabled(enabled)
        self.cancel_button.setEnabled(enabled)
    
    def show_add_item_dialog(self):
        if not self.selected_order_id:
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Thêm món")
        dialog.setFixedWidth(500)
        
        layout = QVBoxLayout(dialog)
        
        # Category and menu items
        filter_layout = QHBoxLayout()
        
        category_label = QLabel("Danh mục:")
        self.dialog_category_combo = QComboBox()
        
        # Add "All" option
        self.dialog_category_combo.addItem("Tất cả", None)
        
        # Get categories
        categories = MenuController.get_all_categories()
        for category in categories:
            self.dialog_category_combo.addItem(category.name, category.id)
        
        self.dialog_category_combo.currentIndexChanged.connect(self.on_dialog_category_changed)
        
        search_label = QLabel("Tìm kiếm:")
        self.dialog_search_input = QLineEdit()
        self.dialog_search_input.textChanged.connect(self.on_dialog_search_changed)
        
        filter_layout.addWidget(category_label)
        filter_layout.addWidget(self.dialog_category_combo)
        filter_layout.addWidget(search_label)
        filter_layout.addWidget(self.dialog_search_input)
        
        layout.addLayout(filter_layout)
        
        # Menu items table
        self.dialog_menu_table = QTableWidget()
        self.dialog_menu_table.setColumnCount(3)
        self.dialog_menu_table.setHorizontalHeaderLabels(["ID", "Tên món", "Giá"])
        self.dialog_menu_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.dialog_menu_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.dialog_menu_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.dialog_menu_table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.dialog_menu_table)
        
        # Quantity
        quantity_layout = QHBoxLayout()
        
        quantity_label = QLabel("Số lượng:")
        self.dialog_quantity_spin = QSpinBox()
        self.dialog_quantity_spin.setRange(1, 100)
        self.dialog_quantity_spin.setValue(1)
        
        note_label = QLabel("Ghi chú:")
        self.dialog_note_input = QLineEdit()
        self.dialog_note_input.setPlaceholderText("Không đường, ít đá,...")
        
        quantity_layout.addWidget(quantity_label)
        quantity_layout.addWidget(self.dialog_quantity_spin)
        quantity_layout.addWidget(note_label)
        quantity_layout.addWidget(self.dialog_note_input)
        
        layout.addLayout(quantity_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Hủy")
        cancel_button.clicked.connect(dialog.reject)
        
        add_button = QPushButton("Thêm")
        add_button.setStyleSheet("background-color: #4CAF50; color: white;")
        add_button.clicked.connect(dialog.accept)
        
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(add_button)
        
        layout.addLayout(buttons_layout)
        
        # Load menu items
        self.load_dialog_menu_items()
        
        if dialog.exec_() == QDialog.Accepted:
            # Get selected menu item
            selected_rows = self.dialog_menu_table.selectedItems()
            
            if not selected_rows:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn món cần thêm")
                return
            
            selected_row = selected_rows[0].row()
            menu_item_id = int(self.dialog_menu_table.item(selected_row, 0).text())
            
            # Get quantity and note
            quantity = self.dialog_quantity_spin.value()
            note = self.dialog_note_input.text().strip() or None
            
            # Add item to order
            success = OrderController.add_item_to_order(
                self.selected_order_id, 
                menu_item_id, 
                quantity,
                note
            )
            
            if success:
                # Reload order details
                self.load_order_details()
                self.load_orders()  # Refresh total in order list
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể thêm món vào đơn hàng")
    
    def load_dialog_menu_items(self, category_id=None, search_text=None):
        self.dialog_menu_table.setRowCount(0)
        
        # Get menu items
        if category_id is not None:
            items = MenuController.get_items_by_category(category_id)
        elif search_text:
            items = MenuController.search_items(search_text)
        else:
            items = MenuController.get_all_items()
        
        # Add to table
        for row, item in enumerate(items):
            self.dialog_menu_table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(item.id))
            self.dialog_menu_table.setItem(row, 0, id_item)
            
            # Name
            name_item = QTableWidgetItem(item.name)
            self.dialog_menu_table.setItem(row, 1, name_item)
            
            # Price
            price_item = QTableWidgetItem(f"{item.price:,.0f} đ")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.dialog_menu_table.setItem(row, 2, price_item)
    
    def on_dialog_category_changed(self, index):
        category_id = self.dialog_category_combo.currentData()
        self.dialog_search_input.clear()
        self.load_dialog_menu_items(category_id=category_id)
    
    def on_dialog_search_changed(self, text):
        if text:
            self.dialog_category_combo.setCurrentIndex(0)  # Select "All"
            self.load_dialog_menu_items(search_text=text)
        else:
            category_id = self.dialog_category_combo.currentData()
            self.load_dialog_menu_items(category_id=category_id)
    
    def show_edit_item_dialog(self):
        if not self.selected_order_id:
            return
        
        # Get selected item from table
        selected_items = self.items_table.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn món cần sửa")
            return
        
        selected_row = selected_items[0].row()
        item = self.selected_order_details['items'][selected_row]
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Sửa: {item['name']}")
        dialog.setFixedWidth(300)
        
        layout = QVBoxLayout(dialog)
        
        # Item info
        layout.addWidget(QLabel(f"Món: {item['name']}"))
        layout.addWidget(QLabel(f"Giá: {item['price']:,.0f} đ"))
        
        # Quantity
        quantity_layout = QHBoxLayout()
        
        quantity_label = QLabel("Số lượng:")
        quantity_spin = QSpinBox()
        quantity_spin.setRange(0, 100)  # 0 to remove item
        quantity_spin.setValue(item['quantity'])
        
        quantity_layout.addWidget(quantity_label)
        quantity_layout.addWidget(quantity_spin)
        
        layout.addLayout(quantity_layout)
        
        # Note
        layout.addWidget(QLabel("Ghi chú:"))
        note_input = QLineEdit()
        note_input.setText(item['note'] or "")
        
        layout.addWidget(note_input)
        
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
            # Get new quantity and note
            quantity = quantity_spin.value()
            note = note_input.text().strip() or None
            
            # Update item
            success = OrderController.update_order_item(
                self.selected_order_id,
                item['id'],
                quantity,
                note
            )
            
            if success:
                # Reload order details
                self.load_order_details()
                self.load_orders()  # Refresh total in order list
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể cập nhật món")
    
    def show_payment_dialog(self):
        if not self.selected_order_id or not self.selected_order_details:
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Thanh toán đơn hàng")
        dialog.setFixedWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Order info
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_layout = QFormLayout(info_frame)
        
        info_layout.addRow("Mã đơn hàng:", QLabel(str(self.selected_order_details['order_id'])))
        info_layout.addRow("Bàn:", QLabel(self.selected_order_details['table_name'] or "--"))
        
        time_str = self.selected_order_details['order_time'].strftime("%H:%M:%S %d/%m/%Y")
        info_layout.addRow("Thời gian:", QLabel(time_str))
        
        layout.addWidget(info_frame)
        
        # Payment details
        payment_frame = QFrame()
        payment_frame.setFrameShape(QFrame.StyledPanel)
        payment_layout = QFormLayout(payment_frame)
        
        subtotal_label = QLabel(f"{self.selected_order_details['total_amount']:,.0f} đ")
        payment_layout.addRow("Tạm tính:", subtotal_label)
        
        discount_spin = QDoubleSpinBox()
        discount_spin.setRange(0, self.selected_order_details['total_amount'])
        discount_spin.setValue(self.selected_order_details['discount'])
        discount_spin.setSingleStep(1000)
        discount_spin.setSuffix(" đ")
        payment_layout.addRow("Giảm giá:", discount_spin)
        
        total_label = QLabel(f"{self.selected_order_details['final_amount']:,.0f} đ")
        total_label.setFont(QFont("Arial", 12, QFont.Bold))
        payment_layout.addRow("Tổng cộng:", total_label)
        
        # Update total when discount changes
        def update_total():
            discount = discount_spin.value()
            total = self.selected_order_details['total_amount'] - discount
            total_label.setText(f"{total:,.0f} đ")
        
        discount_spin.valueChanged.connect(update_total)
        
        # Payment method
        payment_layout.addRow(QLabel("Phương thức thanh toán:"))
        
        payment_method_combo = QComboBox()
        payment_method_combo.addItems(["Tiền mặt", "Chuyển khoản", "Thẻ tín dụng", "Khác"])
        payment_layout.addRow(payment_method_combo)
        
        layout.addWidget(payment_frame)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Hủy")
        cancel_button.clicked.connect(dialog.reject)
        
        complete_button = QPushButton("Hoàn tất thanh toán")
        complete_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        complete_button.clicked.connect(dialog.accept)
        
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(complete_button)
        
        layout.addLayout(buttons_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            # Get payment details
            discount = discount_spin.value()
            payment_method = payment_method_combo.currentText()
            
            # Complete order
            success = OrderController.complete_order(
                self.selected_order_id,
                payment_method,
                discount
            )
            
            if success:
                # Show success message
                QMessageBox.information(self, "Thành công", 
                                     f"Đơn hàng #{self.selected_order_id} đã được thanh toán")
                
                # Reload orders
                self.load_orders()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể hoàn tất thanh toán")
    
    def cancel_order(self):
        if not self.selected_order_id:
            return
        
        # Confirm cancellation
        reply = QMessageBox.question(
            self, 
            "Xác nhận hủy",
            f"Bạn có chắc chắn muốn hủy đơn hàng #{self.selected_order_id}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Cancel order
            success = OrderController.cancel_order(self.selected_order_id)
            
            if success:
                QMessageBox.information(self, "Thành công", 
                                     f"Đơn hàng #{self.selected_order_id} đã được hủy")
                self.load_orders()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể hủy đơn hàng") 