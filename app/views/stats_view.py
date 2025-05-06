from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTabWidget, QDateEdit, QComboBox,
                             QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView,
                             QFormLayout, QFrame, QSplitter, QProgressBar, QScrollArea, QTextBrowser)
from PyQt5.QtCore import Qt, QDate, QDateTime
from PyQt5.QtGui import QIcon, QFont, QColor, QPainter, QPixmap
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
from app.controllers.inventory_controller import InventoryController
from app.controllers.feedback_controller import FeedbackController

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
        
        title_label = QLabel("BÁO CÁO & THỐNG KÊ")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        
        # Date range selection
        date_range_layout = QHBoxLayout()
        
        date_range_layout.addWidget(QLabel("Từ:"))
        
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addDays(-7))  # Default to 7 days ago
        date_range_layout.addWidget(self.start_date_edit)
        
        date_range_layout.addWidget(QLabel("Đến:"))
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())  # Default to today
        date_range_layout.addWidget(self.end_date_edit)
        
        refresh_button = QPushButton("Làm mới")
        refresh_button.setFixedSize(100, 30)
        refresh_button.clicked.connect(self.refresh_stats)
        
        date_range_layout.addWidget(refresh_button)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addLayout(date_range_layout)
        
        main_layout.addLayout(header_layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Tạo các tabs
        sales_tab = self.create_revenue_tab()
        popular_tab = self.create_products_tab()
        prediction_tab = self.create_prediction_tab()
        feedback_tab = self.create_feedback_tab()
        
        # Thêm tabs
        self.tab_widget.addTab(sales_tab, "Doanh thu")
        self.tab_widget.addTab(popular_tab, "Món phổ biến")
        self.tab_widget.addTab(prediction_tab, "Dự báo")
        self.tab_widget.addTab(feedback_tab, "Đánh giá khách hàng")
        
        main_layout.addWidget(self.tab_widget)
        
        # Initialize
        self.on_date_range_changed(0)
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
        
        # Chỉ cập nhật tab hiện tại để tránh lỗi
        tab_index = self.tab_widget.currentIndex()
        if tab_index == 0:  # Doanh thu
            self.update_revenue_tab(start_date, end_date)
        elif tab_index == 1:  # Món phổ biến
            self.update_products_tab(start_date, end_date)
        elif tab_index == 2:  # Dự báo
            self.update_prediction_tab()
        elif tab_index == 3:  # Đánh giá
            self.update_feedback_stats()
        
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
    
    def create_feedback_tab(self):
        """Tạo tab hiển thị thống kê đánh giá khách hàng"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Lấy thống kê đánh giá
        feedback_stats = FeedbackController.get_feedback_stats() or {
            'total_count': 0,
            'rating_distribution': {},
            'avg_rating': 0,
            'avg_service': 0,
            'avg_food': 0,
            'avg_ambience': 0,
            'recent_count': 0
        }
        
        # Split layout
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Stats summary
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        
        # Summaries
        summary_frame = QFrame()
        summary_frame.setFrameShape(QFrame.StyledPanel)
        summary_frame.setStyleSheet("background-color: #f8f9fa; border-radius: 5px;")
        summary_layout = QFormLayout(summary_frame)
        
        total_count = feedback_stats.get('total_count', 0)
        avg_rating = feedback_stats.get('avg_rating', 0)
        recent_count = feedback_stats.get('recent_count', 0)
        
        # Tổng số đánh giá
        total_label = QLabel(f"<b>{total_count}</b>")
        total_label.setFont(QFont("Arial", 14))
        summary_layout.addRow("Tổng số đánh giá:", total_label)
        
        # Đánh giá trung bình
        avg_rating_label = QLabel(f"<b>{avg_rating}/5</b>")
        avg_rating_label.setFont(QFont("Arial", 14))
        if avg_rating >= 4:
            avg_rating_label.setStyleSheet("color: #4CAF50;")  # Green
        elif avg_rating >= 3:
            avg_rating_label.setStyleSheet("color: #FF9800;")  # Orange
        else:
            avg_rating_label.setStyleSheet("color: #f44336;")  # Red
            
        summary_layout.addRow("Đánh giá trung bình:", avg_rating_label)
        
        # Đánh giá gần đây
        recent_label = QLabel(f"<b>{recent_count}</b>")
        recent_label.setFont(QFont("Arial", 14))
        summary_layout.addRow("Đánh giá trong 30 ngày qua:", recent_label)
        
        stats_layout.addWidget(summary_frame)
        
        # Star ratings
        ratings_group = QGroupBox("Phân bố đánh giá")
        ratings_layout = QVBoxLayout(ratings_group)
        
        for i in range(5, 0, -1):
            rating_layout = QHBoxLayout()
            star_label = QLabel(f"{i} sao:")
            count = feedback_stats.get('rating_distribution', {}).get(i, 0)
            
            # Tính phần trăm
            percent = 0
            if total_count > 0:
                percent = round(count / total_count * 100)
            
            # Progress bar
            progress = QProgressBar()
            progress.setRange(0, 100)
            progress.setValue(percent)
            
            # Màu sắc dựa trên số sao
            if i >= 4:
                progress.setStyleSheet("QProgressBar::chunk { background-color: #4CAF50; }")
            elif i == 3:
                progress.setStyleSheet("QProgressBar::chunk { background-color: #FFC107; }")
            else:
                progress.setStyleSheet("QProgressBar::chunk { background-color: #f44336; }")
            
            value_label = QLabel(f"{count} ({percent}%)")
            
            rating_layout.addWidget(star_label, 1)
            rating_layout.addWidget(progress, 4)
            rating_layout.addWidget(value_label, 1)
            
            ratings_layout.addLayout(rating_layout)
        
        stats_layout.addWidget(ratings_group)
        
        # Detailed ratings
        details_group = QGroupBox("Đánh giá chi tiết")
        details_layout = QVBoxLayout(details_group)
        
        # Món ăn
        food_layout = QHBoxLayout()
        food_label = QLabel("Chất lượng món ăn:")
        food_value = QLabel(f"{feedback_stats.get('avg_food', 0)}/5")
        food_value.setFont(QFont("Arial", 12, QFont.Bold))
        
        food_layout.addWidget(food_label)
        food_layout.addStretch()
        food_layout.addWidget(food_value)
        
        # Dịch vụ
        service_layout = QHBoxLayout()
        service_label = QLabel("Chất lượng dịch vụ:")
        service_value = QLabel(f"{feedback_stats.get('avg_service', 0)}/5")
        service_value.setFont(QFont("Arial", 12, QFont.Bold))
        
        service_layout.addWidget(service_label)
        service_layout.addStretch()
        service_layout.addWidget(service_value)
        
        # Không khí
        ambience_layout = QHBoxLayout()
        ambience_label = QLabel("Không gian/môi trường:")
        ambience_value = QLabel(f"{feedback_stats.get('avg_ambience', 0)}/5")
        ambience_value.setFont(QFont("Arial", 12, QFont.Bold))
        
        ambience_layout.addWidget(ambience_label)
        ambience_layout.addStretch()
        ambience_layout.addWidget(ambience_value)
        
        details_layout.addLayout(food_layout)
        details_layout.addLayout(service_layout)
        details_layout.addLayout(ambience_layout)
        
        stats_layout.addWidget(details_group)
        
        # Right side - Recent feedbacks
        feedbacks_widget = QWidget()
        feedbacks_layout = QVBoxLayout(feedbacks_widget)
        
        # Title
        feedbacks_layout.addWidget(QLabel("Đánh giá gần đây:"))
        
        # Get recent feedbacks
        recent_feedbacks = FeedbackController.get_all_feedbacks(limit=10)
        
        # Create feedback list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        if recent_feedbacks:
            for feedback in recent_feedbacks:
                # Create feedback card
                feedback_frame = QFrame()
                feedback_frame.setFrameShape(QFrame.StyledPanel)
                feedback_frame.setStyleSheet("background-color: white; border-radius: 5px; margin-bottom: 10px;")
                
                feedback_layout = QVBoxLayout(feedback_frame)
                
                # Header
                header_layout = QHBoxLayout()
                
                # Order info
                order_info = QLabel(f"Đơn #{feedback.order_id}")
                order_info.setFont(QFont("Arial", 10, QFont.Bold))
                
                # Date
                date_label = QLabel(feedback.created_at.strftime("%d/%m/%Y"))
                
                header_layout.addWidget(order_info)
                header_layout.addStretch()
                header_layout.addWidget(date_label)
                
                feedback_layout.addLayout(header_layout)
                
                # Rating
                star_layout = QHBoxLayout()
                star_label = QLabel(f"Đánh giá: {feedback.rating}/5")
                star_layout.addWidget(star_label)
                star_layout.addStretch()
                
                feedback_layout.addLayout(star_layout)
                
                # Comment if exists
                if feedback.comment:
                    comment_browser = QTextBrowser()
                    comment_browser.setPlainText(feedback.comment)
                    comment_browser.setMaximumHeight(100)
                    feedback_layout.addWidget(comment_browser)
                
                scroll_layout.addWidget(feedback_frame)
        else:
            no_data = QLabel("Chưa có đánh giá nào")
            no_data.setAlignment(Qt.AlignCenter)
            scroll_layout.addWidget(no_data)
            
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        
        feedbacks_layout.addWidget(scroll_area)
        
        # Add widgets to splitter
        splitter.addWidget(stats_widget)
        splitter.addWidget(feedbacks_widget)
        
        # Set sizes
        splitter.setSizes([300, 400])
        
        layout.addWidget(splitter)
        
        return widget 

    def refresh_stats(self):
        """Cập nhật dữ liệu thống kê dựa trên tab đang được chọn"""
        tab_index = self.tab_widget.currentIndex()
        
        if tab_index == 0:  # Doanh thu
            self.update_revenue_tab(self.start_date_edit.date().toPyDate(), 
                                 self.end_date_edit.date().toPyDate() + timedelta(days=1))
        elif tab_index == 1:  # Món phổ biến
            self.update_products_tab(self.start_date_edit.date().toPyDate(), 
                                 self.end_date_edit.date().toPyDate() + timedelta(days=1))
        elif tab_index == 2:  # Dự báo
            self.update_prediction_tab()
        elif tab_index == 3:  # Đánh giá khách hàng
            self.update_feedback_stats()
    
    def update_feedback_stats(self):
        """Cập nhật thống kê đánh giá"""
        # Xóa tab hiện tại
        index = self.tab_widget.indexOf(self.tab_widget.findChild(QWidget, "feedback_tab"))
        if index >= 0:
            self.tab_widget.removeTab(index)
        
        # Thêm tab mới với dữ liệu đã cập nhật
        self.tab_widget.insertTab(3, self.create_feedback_tab(), "Đánh giá khách hàng")
        self.tab_widget.setCurrentIndex(3) 

    def create_revenue_tab(self):
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
        
        return revenue_tab
    
    def create_products_tab(self):
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
        
        return products_tab
    
    def create_prediction_tab(self):
        prediction_tab = QWidget()
        prediction_layout = QVBoxLayout(prediction_tab)
        
        # Revenue prediction
        prediction_group = QGroupBox("Dự báo doanh thu 7 ngày tới")
        prediction_layout_inner = QVBoxLayout(prediction_group)
        
        self.prediction_chart = MatplotlibCanvas(self, width=5, height=4, dpi=100)
        prediction_layout_inner.addWidget(self.prediction_chart)
        
        prediction_layout.addWidget(prediction_group)
        
        return prediction_tab 