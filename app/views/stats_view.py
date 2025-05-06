from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTabWidget, QDateEdit, QComboBox,
                             QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
                             QFormLayout, QFrame, QSplitter)
from PyQt5.QtCore import Qt, QDate, QDateTime
from PyQt5.QtGui import QIcon, QFont, QColor
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from app.controllers.stats_controller import StatsController
from app.controllers.order_controller import OrderController
from app.controllers.menu_controller import MenuController

class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MatplotlibCanvas, self).__init__(self.fig)

class StatsView(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("THỐNG KÊ DOANH THU")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        
        # Date range
        date_range_layout = QHBoxLayout()
        
        self.date_range_combo = QComboBox()
        self.date_range_combo.addItems(["Hôm nay", "7 ngày qua", "30 ngày qua", "Tháng này", "Năm nay", "Tùy chọn"])
        self.date_range_combo.currentIndexChanged.connect(self.on_date_range_changed)
        
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate().addDays(-7))
        self.start_date_edit.setEnabled(False)
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setEnabled(False)
        
        date_range_layout.addWidget(QLabel("Khoảng thời gian:"))
        date_range_layout.addWidget(self.date_range_combo)
        date_range_layout.addWidget(QLabel("Từ:"))
        date_range_layout.addWidget(self.start_date_edit)
        date_range_layout.addWidget(QLabel("Đến:"))
        date_range_layout.addWidget(self.end_date_edit)
        
        refresh_button = QPushButton("Cập nhật")
        refresh_button.setFixedSize(100, 30)
        refresh_button.clicked.connect(self.update_stats)
        
        date_range_layout.addWidget(refresh_button)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addLayout(date_range_layout)
        
        main_layout.addLayout(header_layout)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Revenue tab
        revenue_tab = QWidget()
        revenue_layout = QVBoxLayout(revenue_tab)
        
        # Revenue summary
        revenue_summary_layout = QHBoxLayout()
        
        # Total revenue
        total_revenue_group = QGroupBox("Tổng doanh thu")
        total_revenue_layout = QVBoxLayout(total_revenue_group)
        
        self.total_revenue_label = QLabel("0 đ")
        self.total_revenue_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.total_revenue_label.setAlignment(Qt.AlignCenter)
        
        total_revenue_layout.addWidget(self.total_revenue_label)
        
        # Total orders
        total_orders_group = QGroupBox("Tổng số đơn hàng")
        total_orders_layout = QVBoxLayout(total_orders_group)
        
        self.total_orders_label = QLabel("0")
        self.total_orders_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.total_orders_label.setAlignment(Qt.AlignCenter)
        
        total_orders_layout.addWidget(self.total_orders_label)
        
        # Average order value
        avg_order_group = QGroupBox("Giá trị trung bình mỗi đơn")
        avg_order_layout = QVBoxLayout(avg_order_group)
        
        self.avg_order_label = QLabel("0 đ")
        self.avg_order_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.avg_order_label.setAlignment(Qt.AlignCenter)
        
        avg_order_layout.addWidget(self.avg_order_label)
        
        revenue_summary_layout.addWidget(total_revenue_group)
        revenue_summary_layout.addWidget(total_orders_group)
        revenue_summary_layout.addWidget(avg_order_group)
        
        revenue_layout.addLayout(revenue_summary_layout)
        
        # Revenue chart
        revenue_chart_group = QGroupBox("Biểu đồ doanh thu")
        revenue_chart_layout = QVBoxLayout(revenue_chart_group)
        
        self.revenue_chart = MatplotlibCanvas(self, width=5, height=4, dpi=100)
        revenue_chart_layout.addWidget(self.revenue_chart)
        
        revenue_layout.addWidget(revenue_chart_group)
        
        # Products tab
        products_tab = QWidget()
        products_layout = QVBoxLayout(products_tab)
        
        # Top products
        top_products_group = QGroupBox("Sản phẩm bán chạy")
        top_products_layout = QVBoxLayout(top_products_group)
        
        self.top_products_table = QTableWidget()
        self.top_products_table.setColumnCount(4)
        self.top_products_table.setHorizontalHeaderLabels(["STT", "Tên món", "Số lượng", "Doanh thu"])
        self.top_products_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.top_products_table.verticalHeader().setVisible(False)
        self.top_products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        top_products_layout.addWidget(self.top_products_table)
        
        # Products chart
        products_chart_group = QGroupBox("Biểu đồ phân bố sản phẩm")
        products_chart_layout = QVBoxLayout(products_chart_group)
        
        self.products_chart = MatplotlibCanvas(self, width=5, height=4, dpi=100)
        products_chart_layout.addWidget(self.products_chart)
        
        products_splitter = QSplitter(Qt.Vertical)
        products_splitter.addWidget(top_products_group)
        products_splitter.addWidget(products_chart_group)
        
        products_layout.addWidget(products_splitter)
        
        # Staff tab
        staff_tab = QWidget()
        staff_layout = QVBoxLayout(staff_tab)
        
        # Staff performance
        staff_performance_group = QGroupBox("Hiệu suất nhân viên")
        staff_performance_layout = QVBoxLayout(staff_performance_group)
        
        self.staff_table = QTableWidget()
        self.staff_table.setColumnCount(4)
        self.staff_table.setHorizontalHeaderLabels(["ID", "Tên nhân viên", "Số đơn hàng", "Doanh thu"])
        self.staff_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.staff_table.verticalHeader().setVisible(False)
        self.staff_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        staff_performance_layout.addWidget(self.staff_table)
        
        staff_layout.addWidget(staff_performance_group)
        
        # Prediction tab
        prediction_tab = QWidget()
        prediction_layout = QVBoxLayout(prediction_tab)
        
        # Revenue prediction
        prediction_group = QGroupBox("Dự báo doanh thu 7 ngày tới")
        prediction_layout_inner = QVBoxLayout(prediction_group)
        
        self.prediction_chart = MatplotlibCanvas(self, width=5, height=4, dpi=100)
        prediction_layout_inner.addWidget(self.prediction_chart)
        
        prediction_layout.addWidget(prediction_group)
        
        # Add tabs
        self.tabs.addTab(revenue_tab, "Doanh thu")
        self.tabs.addTab(products_tab, "Sản phẩm")
        self.tabs.addTab(staff_tab, "Nhân viên")
        self.tabs.addTab(prediction_tab, "Dự báo")
        
        main_layout.addWidget(self.tabs)
        
        # Initialize
        self.on_date_range_changed(0)  # Default to today
        self.update_stats()
    
    def on_date_range_changed(self, index):
        today = QDate.currentDate()
        
        if index == 0:  # Today
            self.start_date_edit.setDate(today)
            self.end_date_edit.setDate(today)
            self.start_date_edit.setEnabled(False)
            self.end_date_edit.setEnabled(False)
        elif index == 1:  # Last 7 days
            self.start_date_edit.setDate(today.addDays(-6))
            self.end_date_edit.setDate(today)
            self.start_date_edit.setEnabled(False)
            self.end_date_edit.setEnabled(False)
        elif index == 2:  # Last 30 days
            self.start_date_edit.setDate(today.addDays(-29))
            self.end_date_edit.setDate(today)
            self.start_date_edit.setEnabled(False)
            self.end_date_edit.setEnabled(False)
        elif index == 3:  # This month
            self.start_date_edit.setDate(QDate(today.year(), today.month(), 1))
            self.end_date_edit.setDate(today)
            self.start_date_edit.setEnabled(False)
            self.end_date_edit.setEnabled(False)
        elif index == 4:  # This year
            self.start_date_edit.setDate(QDate(today.year(), 1, 1))
            self.end_date_edit.setDate(today)
            self.start_date_edit.setEnabled(False)
            self.end_date_edit.setEnabled(False)
        else:  # Custom
            self.start_date_edit.setEnabled(True)
            self.end_date_edit.setEnabled(True)
    
    def update_stats(self):
        # Get date range
        start_date = self.start_date_edit.date().toPyDate()
        end_date = self.end_date_edit.date().toPyDate()
        
        # Add a day to end_date to include the full day
        end_date = end_date + timedelta(days=1)
        
        # Update each tab based on selected date range
        self.update_revenue_tab(start_date, end_date)
        self.update_products_tab(start_date, end_date)
        self.update_staff_tab(start_date, end_date)
        self.update_prediction_tab()
    
    def update_revenue_tab(self, start_date, end_date):
        # Get revenue data
        revenue_data = StatsController.get_revenue_by_date_range(start_date, end_date)
        
        # Update summary
        total_revenue = revenue_data['revenue'].sum()
        self.total_revenue_label.setText(f"{total_revenue:,.0f} đ")
        
        # We need to query for the order count separately
        total_orders = len(revenue_data[revenue_data['revenue'] > 0])
        self.total_orders_label.setText(str(total_orders))
        
        avg_order = total_revenue / total_orders if total_orders > 0 else 0
        self.avg_order_label.setText(f"{avg_order:,.0f} đ")
        
        # Update chart
        ax = self.revenue_chart.axes
        ax.clear()
        
        dates = revenue_data.index
        values = revenue_data['revenue']
        
        ax.bar(range(len(dates)), values, color='#4CAF50')
        ax.set_xticks(range(len(dates)))
        
        # Format date labels based on range length
        if len(dates) > 14:
            # For longer ranges, show fewer tick labels
            step = len(dates) // 7
            ax.set_xticks(range(0, len(dates), step))
            ax.set_xticklabels([date.strftime('%d/%m') for date in dates[::step]], rotation=45)
        else:
            ax.set_xticklabels([date.strftime('%d/%m') for date in dates], rotation=45)
        
        ax.set_title('Doanh thu theo ngày')
        ax.set_ylabel('Doanh thu (đồng)')
        
        self.revenue_chart.fig.tight_layout()
        self.revenue_chart.draw()
    
    def update_products_tab(self, start_date, end_date):
        # Get top selling products
        top_products = StatsController.get_top_selling_items(start_date, end_date)
        
        # Update table
        self.top_products_table.setRowCount(0)
        
        for row, product in enumerate(top_products):
            self.top_products_table.insertRow(row)
            
            # Rank
            rank_item = QTableWidgetItem(str(row + 1))
            self.top_products_table.setItem(row, 0, rank_item)
            
            # Name
            name_item = QTableWidgetItem(product.name)
            self.top_products_table.setItem(row, 1, name_item)
            
            # Quantity
            quantity_item = QTableWidgetItem(str(product.quantity))
            self.top_products_table.setItem(row, 2, quantity_item)
            
            # Revenue
            revenue_item = QTableWidgetItem(f"{product.revenue:,.0f} đ")
            revenue_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.top_products_table.setItem(row, 3, revenue_item)
        
        # Update chart
        ax = self.products_chart.axes
        ax.clear()
        
        # Create pie chart
        if top_products:
            labels = [product.name for product in top_products[:5]]
            sizes = [product.quantity for product in top_products[:5]]
            
            # Add "Others" if there are more than 5 products
            if len(top_products) > 5:
                labels.append("Khác")
                sizes.append(sum(product.quantity for product in top_products[5:]))
            
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=False, startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            ax.set_title('Phân bố sản phẩm bán chạy')
        
        self.products_chart.fig.tight_layout()
        self.products_chart.draw()
    
    def update_staff_tab(self, start_date, end_date):
        # Get staff performance
        staff_performance = StatsController.get_staff_performance(start_date, end_date)
        
        # Update table
        self.staff_table.setRowCount(0)
        
        for row, staff in enumerate(staff_performance):
            self.staff_table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(staff.id))
            self.staff_table.setItem(row, 0, id_item)
            
            # Name
            name_item = QTableWidgetItem(staff.name)
            self.staff_table.setItem(row, 1, name_item)
            
            # Orders count
            orders_item = QTableWidgetItem(str(staff.orders_count))
            orders_item.setTextAlignment(Qt.AlignCenter)
            self.staff_table.setItem(row, 2, orders_item)
            
            # Revenue
            revenue_item = QTableWidgetItem(f"{staff.total_revenue:,.0f} đ")
            revenue_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.staff_table.setItem(row, 3, revenue_item)
    
    def update_prediction_tab(self):
        # Get prediction data
        predictions = StatsController.predict_revenue()
        
        # Update chart
        ax = self.prediction_chart.axes
        ax.clear()
        
        days = 7
        today = datetime.now().date()
        
        # Generate dates for the next 7 days
        dates = [today + timedelta(days=i) for i in range(days)]
        
        # Plot prediction
        ax.bar(range(days), predictions, color='#FF9800')
        ax.set_xticks(range(days))
        ax.set_xticklabels([date.strftime('%d/%m') for date in dates], rotation=45)
        
        ax.set_title('Dự báo doanh thu 7 ngày tới')
        ax.set_ylabel('Doanh thu dự kiến (đồng)')
        
        self.prediction_chart.fig.tight_layout()
        self.prediction_chart.draw() 