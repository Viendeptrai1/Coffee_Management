"""
Local Search Algorithms
Triển khai các thuật toán Local Search để tối ưu hóa giá menu
"""

import random
import math
import numpy as np
from typing import Dict, List, Tuple, Callable, Any

class MenuPriceOptimizer:
    """Tối ưu hóa giá menu sử dụng các thuật toán local search"""
    
    def __init__(self, 
                menu_items: List[Dict], 
                sales_data: List[Dict],
                price_bounds: Dict[int, Tuple[float, float]] = None,
                elasticity_data: Dict[int, float] = None):
        """
        Khởi tạo bài toán tối ưu hóa giá menu
        
        Args:
            menu_items: Danh sách các món [{'id': id, 'name': name, 'price': price, 'category_id': category_id}]
            sales_data: Dữ liệu bán hàng [{'menu_item_id': id, 'quantity': qty, 'date': date}]
            price_bounds: Giới hạn giá cho mỗi món {menu_item_id: (min_price, max_price)}
            elasticity_data: Độ co giãn của cầu theo giá {menu_item_id: elasticity}
        """
        self.menu_items = menu_items
        self.sales_data = sales_data
        
        # Lấy giá hiện tại làm trạng thái khởi đầu
        self.current_state = {item['id']: item['price'] for item in menu_items}
        
        # Thiết lập giới hạn giá (min, max) cho mỗi món nếu không được cung cấp
        if price_bounds is None:
            self.price_bounds = {}
            for item in menu_items:
                current_price = item['price']
                min_price = max(current_price * 0.7, 1000)  # Không giảm quá 30% và tối thiểu 1.000 đồng
                max_price = current_price * 1.5  # Không tăng quá 50%
                self.price_bounds[item['id']] = (min_price, max_price)
        else:
            self.price_bounds = price_bounds
            
        # Thiết lập độ co giãn của cầu theo giá mặc định nếu không được cung cấp
        if elasticity_data is None:
            # Độ co giãn mặc định: -1.3 (cà phê và thức uống thường có độ co giãn từ -1 đến -1.5)
            self.elasticity_data = {item['id']: -1.3 for item in menu_items}
        else:
            self.elasticity_data = elasticity_data
            
        # Khởi tạo dữ liệu bán hàng theo món
        self.item_sales = self._process_sales_data()
        
        # Bảng phân bổ chéo (cross-selling) giữa các món
        self.cross_selling = self._calculate_cross_selling()
    
    def _process_sales_data(self) -> Dict[int, int]:
        """Xử lý dữ liệu bán hàng theo món"""
        item_sales = {}
        for item in self.menu_items:
            item_id = item['id']
            # Tính tổng số lượng đã bán cho mỗi món
            quantity = sum(sale['quantity'] for sale in self.sales_data 
                          if sale['menu_item_id'] == item_id)
            item_sales[item_id] = quantity
        return item_sales
    
    def _calculate_cross_selling(self) -> Dict[Tuple[int, int], float]:
        """Tính toán phân bổ chéo giữa các món"""
        # Nhóm dữ liệu bán hàng theo đơn hàng
        orders = {}
        for sale in self.sales_data:
            order_id = sale.get('order_id')
            if order_id not in orders:
                orders[order_id] = []
            orders[order_id].append(sale['menu_item_id'])
        
        # Tính tần suất xuất hiện cùng nhau
        cross_selling = {}
        menu_ids = [item['id'] for item in self.menu_items]
        
        for id1 in menu_ids:
            for id2 in menu_ids:
                if id1 != id2:
                    # Đếm số lần hai món xuất hiện cùng nhau
                    count = sum(1 for items in orders.values() 
                               if id1 in items and id2 in items)
                    # Chuẩn hóa theo số lượng đơn hàng
                    cross_selling[(id1, id2)] = count / max(1, len(orders))
        
        return cross_selling
    
    def _get_random_neighbor(self, state: Dict[int, float], step_size: float = 0.05) -> Dict[int, float]:
        """
        Tạo một trạng thái lân cận ngẫu nhiên bằng cách thay đổi giá một món
        
        Args:
            state: Trạng thái hiện tại {menu_item_id: price}
            step_size: Kích thước bước thay đổi giá (tỷ lệ phần trăm)
            
        Returns:
            Dict: Trạng thái mới
        """
        new_state = state.copy()
        
        # Chọn ngẫu nhiên một món để thay đổi giá
        item_id = random.choice(list(state.keys()))
        current_price = state[item_id]
        
        # Tính khoảng thay đổi dựa trên step_size
        price_range = current_price * step_size
        
        # Thay đổi giá ngẫu nhiên trong khoảng ±step_size%
        change = random.uniform(-price_range, price_range)
        new_price = current_price + change
        
        # Làm tròn đến 1000 đồng
        new_price = round(new_price / 1000) * 1000
        
        # Đảm bảo giá mới nằm trong giới hạn đã cho
        min_price, max_price = self.price_bounds[item_id]
        new_price = max(min_price, min(new_price, max_price))
        
        new_state[item_id] = new_price
        return new_state
    
    def _evaluate(self, state: Dict[int, float]) -> float:
        """
        Đánh giá một trạng thái dựa trên doanh thu dự kiến
        
        Args:
            state: Trạng thái cần đánh giá {menu_item_id: price}
            
        Returns:
            float: Doanh thu dự kiến
        """
        total_revenue = 0
        
        for item_id, new_price in state.items():
            # Lấy giá và số lượng ban đầu
            old_price = self.current_state[item_id]
            original_quantity = self.item_sales.get(item_id, 0)
            
            if original_quantity == 0:
                continue
                
            # Tính tỷ lệ thay đổi giá
            price_ratio = new_price / old_price if old_price > 0 else 1.0
            
            # Lấy độ co giãn của cầu theo giá
            elasticity = self.elasticity_data.get(item_id, -1.3)
            
            # Tính số lượng mới dựa trên độ co giãn
            # Công thức: %ΔQuantity = Elasticity * %ΔPrice
            quantity_ratio = 1 + elasticity * (price_ratio - 1)
            
            # Giới hạn tỷ lệ thay đổi số lượng để tránh kết quả phi thực tế
            quantity_ratio = max(0.5, min(quantity_ratio, 1.5))
            
            new_quantity = original_quantity * quantity_ratio
            
            # Tính doanh thu cho món này
            item_revenue = new_price * new_quantity
            
            # Xem xét tác động chéo với các món khác (cross-selling effect)
            cross_effect = 0
            for other_id in state.keys():
                if other_id != item_id:
                    cross_impact = self.cross_selling.get((item_id, other_id), 0)
                    other_price = state[other_id]
                    other_quantity = self.item_sales.get(other_id, 0)
                    
                    # Tính doanh thu bổ sung từ cross-selling
                    # Nếu số lượng món này tăng/giảm, các món liên quan cũng bị ảnh hưởng
                    quantity_change = new_quantity - original_quantity
                    if quantity_change != 0:
                        cross_quantity_change = quantity_change * cross_impact
                        cross_effect += cross_quantity_change * other_price
            
            total_revenue += item_revenue + cross_effect
        
        return total_revenue
    
    def hill_climbing(self, 
                    max_iterations: int = 1000, 
                    step_size: float = 0.05, 
                    plateau_iterations: int = 100) -> Tuple[Dict[int, float], float]:
        """
        Thuật toán Hill Climbing để tối ưu hóa giá menu
        
        Args:
            max_iterations: Số lần lặp tối đa
            step_size: Kích thước bước thay đổi giá (tỷ lệ phần trăm)
            plateau_iterations: Số lần lặp tối đa khi không cải thiện
            
        Returns:
            Tuple: (trạng thái tối ưu, giá trị tối ưu)
        """
        current_state = self.current_state.copy()
        current_value = self._evaluate(current_state)
        
        iterations_without_improvement = 0
        
        for i in range(max_iterations):
            # Tạo một trạng thái lân cận
            neighbor = self._get_random_neighbor(current_state, step_size)
            neighbor_value = self._evaluate(neighbor)
            
            # Nếu trạng thái lân cận tốt hơn, di chuyển đến đó
            if neighbor_value > current_value:
                current_state = neighbor
                current_value = neighbor_value
                iterations_without_improvement = 0
            else:
                iterations_without_improvement += 1
            
            # Nếu không có cải thiện sau một số lần lặp, dừng
            if iterations_without_improvement >= plateau_iterations:
                break
        
        return current_state, current_value
    
    def simulated_annealing(self, 
                          initial_temp: float = 1.0, 
                          cooling_rate: float = 0.995,
                          min_temp: float = 0.01,
                          max_iterations: int = 10000,
                          step_size: float = 0.05) -> Tuple[Dict[int, float], float]:
        """
        Thuật toán Simulated Annealing để tối ưu hóa giá menu
        
        Args:
            initial_temp: Nhiệt độ ban đầu
            cooling_rate: Tỷ lệ làm mát
            min_temp: Nhiệt độ tối thiểu
            max_iterations: Số lần lặp tối đa
            step_size: Kích thước bước thay đổi giá (tỷ lệ phần trăm)
            
        Returns:
            Tuple: (trạng thái tối ưu, giá trị tối ưu)
        """
        current_state = self.current_state.copy()
        current_value = self._evaluate(current_state)
        
        best_state = current_state.copy()
        best_value = current_value
        
        temp = initial_temp
        
        for i in range(max_iterations):
            # Nếu nhiệt độ quá thấp, dừng
            if temp < min_temp:
                break
                
            # Tạo một trạng thái lân cận
            neighbor = self._get_random_neighbor(current_state, step_size)
            neighbor_value = self._evaluate(neighbor)
            
            # Tính Delta E
            delta = neighbor_value - current_value
            
            # Nếu trạng thái mới tốt hơn hoặc chấp nhận xác suất
            if delta > 0 or random.random() < math.exp(delta / temp):
                current_state = neighbor
                current_value = neighbor_value
                
                # Cập nhật trạng thái tốt nhất nếu cần
                if current_value > best_value:
                    best_state = current_state.copy()
                    best_value = current_value
            
            # Giảm nhiệt độ
            temp *= cooling_rate
        
        return best_state, best_value
    
    def optimize_menu_prices(self, 
                            algorithm: str = "simulated_annealing", 
                            **params) -> Tuple[Dict[int, float], float, Dict]:
        """
        Tối ưu hóa giá menu sử dụng thuật toán đã chọn
        
        Args:
            algorithm: Thuật toán sử dụng ("hill_climbing" hoặc "simulated_annealing")
            **params: Tham số cho thuật toán
            
        Returns:
            Tuple: (trạng thái tối ưu, giá trị tối ưu, so sánh với giá hiện tại)
        """
        if algorithm == "hill_climbing":
            best_state, best_value = self.hill_climbing(**params)
        else:  # simulated_annealing
            best_state, best_value = self.simulated_annealing(**params)
            
        # Tính doanh thu với giá hiện tại làm cơ sở so sánh
        current_value = self._evaluate(self.current_state)
        
        # Tạo bảng so sánh
        comparison = {
            "current_revenue": current_value,
            "optimized_revenue": best_value,
            "improvement": best_value - current_value,
            "improvement_percentage": (best_value - current_value) / current_value * 100 if current_value > 0 else 0,
            "price_changes": []
        }
        
        # Chi tiết thay đổi giá
        for item in self.menu_items:
            item_id = item['id']
            old_price = self.current_state[item_id]
            new_price = best_state[item_id]
            
            if old_price != new_price:
                comparison["price_changes"].append({
                    "item_id": item_id,
                    "name": item['name'],
                    "old_price": old_price,
                    "new_price": new_price,
                    "change": new_price - old_price,
                    "change_percentage": (new_price - old_price) / old_price * 100
                })
        
        # Sắp xếp theo phần trăm thay đổi
        comparison["price_changes"].sort(key=lambda x: abs(x["change_percentage"]), reverse=True)
        
        return best_state, best_value, comparison 