"""
Genetic Algorithm
Triển khai thuật toán di truyền để tối ưu hóa giá menu
"""

import random
import numpy as np
from typing import Dict, List, Tuple, Callable, Any, Optional
import copy
import time

class MenuPriceGeneticOptimizer:
    """Tối ưu hóa giá menu sử dụng thuật toán di truyền (Genetic Algorithm)"""
    
    def __init__(self, 
                menu_items: List[Dict], 
                sales_data: List[Dict],
                price_bounds: Dict[int, Tuple[float, float]] = None,
                elasticity_data: Dict[int, float] = None,
                population_size: int = 50,
                elite_size: int = 5,
                mutation_rate: float = 0.1,
                crossover_rate: float = 0.8):
        """
        Khởi tạo bài toán tối ưu hóa giá menu với thuật toán di truyền
        
        Args:
            menu_items: Danh sách các món [{'id': id, 'name': name, 'price': price, 'category_id': category_id}]
            sales_data: Dữ liệu bán hàng [{'menu_item_id': id, 'quantity': qty, 'date': date}]
            price_bounds: Giới hạn giá cho mỗi món {menu_item_id: (min_price, max_price)}
            elasticity_data: Độ co giãn của cầu theo giá {menu_item_id: elasticity}
            population_size: Kích thước quần thể
            elite_size: Số lượng cá thể ưu tú được giữ lại qua các thế hệ
            mutation_rate: Tỷ lệ đột biến
            crossover_rate: Tỷ lệ lai ghép
        """
        self.menu_items = menu_items
        self.sales_data = sales_data
        self.population_size = population_size
        self.elite_size = elite_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        
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
        
        # Danh sách ID món để đảm bảo thứ tự nhất quán
        self.menu_ids = [item['id'] for item in menu_items]
    
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
    
    def _evaluate_individual(self, individual: Dict[int, float]) -> float:
        """
        Đánh giá một cá thể (một cấu hình giá) dựa trên doanh thu dự kiến
        
        Args:
            individual: Cá thể cần đánh giá {menu_item_id: price}
            
        Returns:
            float: Doanh thu dự kiến (fitness)
        """
        total_revenue = 0
        
        for item_id, new_price in individual.items():
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
            for other_id in individual.keys():
                if other_id != item_id:
                    cross_impact = self.cross_selling.get((item_id, other_id), 0)
                    other_price = individual[other_id]
                    other_quantity = self.item_sales.get(other_id, 0)
                    
                    # Tính doanh thu bổ sung từ cross-selling
                    quantity_change = new_quantity - original_quantity
                    if quantity_change != 0:
                        cross_quantity_change = quantity_change * cross_impact
                        cross_effect += cross_quantity_change * other_price
            
            total_revenue += item_revenue + cross_effect
        
        return total_revenue
    
    def _create_initial_population(self) -> List[Dict[int, float]]:
        """
        Tạo quần thể ban đầu
        
        Returns:
            List: Danh sách các cá thể (cấu hình giá)
        """
        population = []
        
        # Thêm giá hiện tại vào quần thể
        population.append(self.current_state.copy())
        
        # Tạo các cá thể ngẫu nhiên khác
        for _ in range(self.population_size - 1):
            individual = {}
            for item_id in self.menu_ids:
                min_price, max_price = self.price_bounds[item_id]
                # Làm tròn đến 1000 đồng
                random_price = round(random.uniform(min_price, max_price) / 1000) * 1000
                individual[item_id] = random_price
            
            population.append(individual)
            
        return population
    
    def _select_parents(self, population: List[Dict[int, float]], fitnesses: List[float]) -> List[Dict[int, float]]:
        """
        Chọn cha mẹ cho thế hệ tiếp theo sử dụng phương pháp tournament selection
        
        Args:
            population: Quần thể hiện tại
            fitnesses: Giá trị fitness của mỗi cá thể
            
        Returns:
            List: Danh sách cha mẹ được chọn
        """
        # Chọn số lượng cá thể ưu tú
        elite_indices = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)[:self.elite_size]
        elite = [population[i] for i in elite_indices]
        
        # Chọn phần còn lại sử dụng tournament selection
        tournament_size = 3
        selected = []
        
        while len(selected) < (self.population_size - self.elite_size):
            # Chọn ngẫu nhiên tournament_size cá thể
            tournament_indices = random.sample(range(len(population)), tournament_size)
            # Chọn cá thể có fitness tốt nhất từ tournament
            best_idx = max(tournament_indices, key=lambda i: fitnesses[i])
            selected.append(population[best_idx])
        
        return elite + selected
    
    def _crossover(self, parent1: Dict[int, float], parent2: Dict[int, float]) -> Tuple[Dict[int, float], Dict[int, float]]:
        """
        Thực hiện lai ghép giữa hai cá thể cha mẹ
        
        Args:
            parent1: Cá thể cha
            parent2: Cá thể mẹ
            
        Returns:
            Tuple: Hai cá thể con sau lai ghép
        """
        if random.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()
        
        child1 = {}
        child2 = {}
        
        # Chọn ngẫu nhiên điểm cắt
        crossover_point = random.randint(1, len(self.menu_ids) - 1)
        
        for i, item_id in enumerate(self.menu_ids):
            if i < crossover_point:
                child1[item_id] = parent1[item_id]
                child2[item_id] = parent2[item_id]
            else:
                child1[item_id] = parent2[item_id]
                child2[item_id] = parent1[item_id]
        
        return child1, child2
    
    def _mutate(self, individual: Dict[int, float]) -> Dict[int, float]:
        """
        Thực hiện đột biến trên một cá thể
        
        Args:
            individual: Cá thể cần đột biến
            
        Returns:
            Dict: Cá thể sau đột biến
        """
        mutated = individual.copy()
        
        for item_id in self.menu_ids:
            # Đột biến với xác suất mutation_rate
            if random.random() < self.mutation_rate:
                min_price, max_price = self.price_bounds[item_id]
                current_price = mutated[item_id]
                
                # Thay đổi giá ngẫu nhiên trong khoảng ±10%
                change_ratio = random.uniform(-0.1, 0.1)
                new_price = current_price * (1 + change_ratio)
                
                # Làm tròn đến 1000 đồng
                new_price = round(new_price / 1000) * 1000
                
                # Đảm bảo giá mới nằm trong giới hạn
                new_price = max(min_price, min(new_price, max_price))
                
                mutated[item_id] = new_price
        
        return mutated
    
    def optimize(self, 
                max_generations: int = 100, 
                convergence_threshold: int = 20, 
                time_limit: Optional[float] = None) -> Tuple[Dict[int, float], float, Dict]:
        """
        Thực hiện tối ưu hóa sử dụng thuật toán di truyền
        
        Args:
            max_generations: Số thế hệ tối đa
            convergence_threshold: Số thế hệ không cải thiện trước khi dừng
            time_limit: Giới hạn thời gian chạy (giây), None nếu không giới hạn
            
        Returns:
            Tuple: (trạng thái tối ưu, giá trị tối ưu, thông tin so sánh)
        """
        start_time = time.time()
        
        # Tạo quần thể ban đầu
        population = self._create_initial_population()
        
        # Tính fitness cho quần thể ban đầu
        fitnesses = [self._evaluate_individual(individual) for individual in population]
        
        # Theo dõi cá thể tốt nhất
        best_individual = max(zip(population, fitnesses), key=lambda x: x[1])
        best_fitness_history = [best_individual[1]]
        
        generations_without_improvement = 0
        
        for generation in range(max_generations):
            # Kiểm tra điều kiện dừng về thời gian
            if time_limit and (time.time() - start_time) > time_limit:
                break
                
            # Chọn cha mẹ
            parents = self._select_parents(population, fitnesses)
            
            # Tạo thế hệ mới thông qua lai ghép và đột biến
            new_population = []
            
            # Giữ lại các cá thể ưu tú
            elite_indices = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)[:self.elite_size]
            for i in elite_indices:
                new_population.append(population[i])
            
            # Tạo các cá thể mới từ lai ghép và đột biến
            while len(new_population) < self.population_size:
                # Chọn ngẫu nhiên hai cha mẹ
                parent1 = random.choice(parents)
                parent2 = random.choice(parents)
                
                # Lai ghép
                child1, child2 = self._crossover(parent1, parent2)
                
                # Đột biến
                child1 = self._mutate(child1)
                child2 = self._mutate(child2)
                
                # Thêm vào quần thể mới
                new_population.append(child1)
                if len(new_population) < self.population_size:
                    new_population.append(child2)
            
            # Cập nhật quần thể
            population = new_population
            
            # Tính fitness cho quần thể mới
            fitnesses = [self._evaluate_individual(individual) for individual in population]
            
            # Cập nhật cá thể tốt nhất
            current_best = max(zip(population, fitnesses), key=lambda x: x[1])
            
            if current_best[1] > best_individual[1]:
                best_individual = current_best
                generations_without_improvement = 0
            else:
                generations_without_improvement += 1
            
            best_fitness_history.append(best_individual[1])
            
            # Kiểm tra điều kiện hội tụ
            if generations_without_improvement >= convergence_threshold:
                break
        
        # Kết quả cuối cùng
        best_state = best_individual[0]
        best_value = best_individual[1]
        
        # Tính doanh thu với giá hiện tại làm cơ sở so sánh
        current_value = self._evaluate_individual(self.current_state)
        
        # Tạo bảng so sánh
        comparison = {
            "current_revenue": current_value,
            "optimized_revenue": best_value,
            "improvement": best_value - current_value,
            "improvement_percentage": (best_value - current_value) / current_value * 100 if current_value > 0 else 0,
            "generations": generation + 1,
            "best_fitness_history": best_fitness_history,
            "execution_time": time.time() - start_time,
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