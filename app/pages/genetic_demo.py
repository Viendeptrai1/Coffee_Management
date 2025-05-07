import sys
import os
import json
import random
from pprint import pprint
import time
import matplotlib.pyplot as plt

# Đảm bảo có thể import từ thư mục app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.genetic_algorithm import MenuPriceGeneticOptimizer
from utils.local_search import MenuPriceOptimizer

def generate_sample_data():
    """Tạo dữ liệu mẫu cho việc minh họa"""
    # Tạo dữ liệu mẫu về menu
    menu_items = [
        {"id": 1, "name": "Cà phê đen", "price": 25000, "category_id": 1},
        {"id": 2, "name": "Cà phê sữa", "price": 30000, "category_id": 1},
        {"id": 3, "name": "Cappuccino", "price": 45000, "category_id": 1},
        {"id": 4, "name": "Latte", "price": 50000, "category_id": 1},
        {"id": 5, "name": "Trà đào", "price": 40000, "category_id": 2},
        {"id": 6, "name": "Trà sữa trân châu", "price": 45000, "category_id": 2},
        {"id": 7, "name": "Bánh mì que", "price": 15000, "category_id": 3},
        {"id": 8, "name": "Croissant", "price": 25000, "category_id": 3}
    ]
    
    # Tạo dữ liệu mẫu về sales
    sales_data = []
    
    # Mô phỏng 200 đơn hàng
    for order_id in range(1, 201):
        # Số lượng món trong đơn hàng
        num_items = random.randint(1, 4)
        # Chọn ngẫu nhiên các món
        selected_items = random.sample([item["id"] for item in menu_items], num_items)
        
        # Random date trong 30 ngày gần đây
        day = random.randint(1, 30)
        date = f"2023-06-{day:02d}"
        
        # Tạo các mục bán hàng
        for item_id in selected_items:
            quantity = random.randint(1, 3)
            sales_data.append({
                "menu_item_id": item_id,
                "quantity": quantity,
                "date": date,
                "order_id": order_id
            })
    
    # Tạo dữ liệu độ co giãn theo giá
    elasticity_data = {
        1: -1.2,  # Cà phê đen - ít co giãn vì khách hàng trung thành
        2: -1.3,  # Cà phê sữa
        3: -1.5,  # Cappuccino - co giãn hơn vì là đồ uống cao cấp
        4: -1.6,  # Latte - tương tự cappuccino
        5: -1.4,  # Trà đào
        6: -1.5,  # Trà sữa
        7: -1.8,  # Bánh mì que - co giãn cao vì có nhiều lựa chọn thay thế
        8: -1.7   # Croissant
    }
    
    return menu_items, sales_data, elasticity_data

def run_genetic_demo():
    """Chạy demo thuật toán di truyền cho tối ưu hóa giá menu"""
    print("===== MINH HỌA THUẬT TOÁN DI TRUYỀN TRONG TỐI ƯU HÓA GIÁ MENU =====")
    
    # Tạo dữ liệu mẫu
    menu_items, sales_data, elasticity_data = generate_sample_data()
    
    # In menu hiện tại
    print("\n----- MENU HIỆN TẠI -----")
    print(f"{'ID':<3} {'TÊN MÓN':<20} {'GIÁ (VNĐ)':<12}")
    for item in menu_items:
        print(f"{item['id']:<3} {item['name']:<20} {item['price']:<12,.0f}")
    
    # Khởi tạo trình tối ưu hóa di truyền
    ga_params = {
        "population_size": 50,
        "elite_size": 5,
        "mutation_rate": 0.1,
        "crossover_rate": 0.8
    }
    print("\n\n----- THUẬT TOÁN DI TRUYỀN (GENETIC ALGORITHM) -----")
    print("Tham số:", ga_params)
    
    genetic_optimizer = MenuPriceGeneticOptimizer(
        menu_items=menu_items,
        sales_data=sales_data,
        elasticity_data=elasticity_data,
        **ga_params
    )
    
    # Thực hiện tối ưu hóa với thuật toán di truyền
    print("Đang thực hiện tối ưu hóa...")
    start_time = time.time()
    
    optimize_params = {
        "max_generations": 100,
        "convergence_threshold": 20
    }
    print("Tham số tối ưu hóa:", optimize_params)
    
    ga_best_state, ga_best_value, ga_comparison = genetic_optimizer.optimize(**optimize_params)
    
    ga_time = time.time() - start_time
    
    # In kết quả
    print("\nKết quả thuật toán di truyền:")
    print(f"Doanh thu hiện tại: {ga_comparison['current_revenue']:,.0f} VNĐ")
    print(f"Doanh thu tối ưu:   {ga_comparison['optimized_revenue']:,.0f} VNĐ")
    print(f"Cải thiện:          {ga_comparison['improvement']:,.0f} VNĐ ({ga_comparison['improvement_percentage']:.2f}%)")
    print(f"Số thế hệ:          {ga_comparison['generations']}")
    print(f"Thời gian thực thi: {ga_comparison['execution_time']:.2f} giây")
    
    # In chi tiết thay đổi giá
    if ga_comparison['price_changes']:
        print("\nChi tiết thay đổi giá:")
        print(f"{'TÊN MÓN':<20} {'GIÁ CŨ':<12} {'GIÁ MỚI':<12} {'THAY ĐỔI':<12} {'%':<6}")
        for change in ga_comparison['price_changes']:
            print(f"{change['name']:<20} {change['old_price']:<12,.0f} {change['new_price']:<12,.0f} {change['change']:<12,.0f} {change['change_percentage']:<6.2f}%")
    
    # So sánh với Simulated Annealing
    print("\n\n----- SO SÁNH VỚI SIMULATED ANNEALING -----")
    sa_params = {
        "initial_temp": 1.0,
        "cooling_rate": 0.995,
        "min_temp": 0.01,
        "max_iterations": 10000,
        "step_size": 0.05
    }
    print("Tham số Simulated Annealing:", sa_params)
    
    # Khởi tạo trình tối ưu hóa với local search
    sa_optimizer = MenuPriceOptimizer(
        menu_items=menu_items,
        sales_data=sales_data,
        elasticity_data=elasticity_data
    )
    
    # Thực hiện tối ưu hóa với Simulated Annealing
    print("Đang thực hiện tối ưu hóa với Simulated Annealing...")
    start_time = time.time()
    
    sa_best_state, sa_best_value, sa_comparison = sa_optimizer.optimize_menu_prices(
        algorithm="simulated_annealing", **sa_params
    )
    
    sa_time = time.time() - start_time
    
    # In kết quả
    print("\nKết quả Simulated Annealing:")
    print(f"Doanh thu hiện tại: {sa_comparison['current_revenue']:,.0f} VNĐ")
    print(f"Doanh thu tối ưu:   {sa_comparison['optimized_revenue']:,.0f} VNĐ")
    print(f"Cải thiện:          {sa_comparison['improvement']:,.0f} VNĐ ({sa_comparison['improvement_percentage']:.2f}%)")
    print(f"Thời gian thực thi: {sa_time:.2f} giây")
    
    # Bảng so sánh thuật toán
    print("\n----- BẢNG SO SÁNH THUẬT TOÁN -----")
    print(f"{'Thuật toán':<20} {'Doanh thu':<15} {'Cải thiện':<15} {'Thời gian':<15}")
    print(f"{'Di truyền':<20} {ga_comparison['optimized_revenue']:,.0f} VNĐ {ga_comparison['improvement_percentage']:.2f}% {ga_comparison['execution_time']:.2f}s")
    print(f"{'Simulated Annealing':<20} {sa_comparison['optimized_revenue']:,.0f} VNĐ {sa_comparison['improvement_percentage']:.2f}% {sa_time:.2f}s")
    
    winner = "Di truyền" if ga_comparison['optimized_revenue'] > sa_comparison['optimized_revenue'] else "Simulated Annealing"
    if ga_comparison['optimized_revenue'] == sa_comparison['optimized_revenue']:
        winner = "Cả hai (kết quả bằng nhau)"
    print(f"\nThuật toán tốt hơn về doanh thu: {winner}")
    
    # Vẽ biểu đồ tiến hóa fitness qua các thế hệ
    if 'best_fitness_history' in ga_comparison:
        try:
            plt.figure(figsize=(10, 6))
            plt.plot(range(len(ga_comparison['best_fitness_history'])), ga_comparison['best_fitness_history'])
            plt.xlabel('Thế hệ')
            plt.ylabel('Doanh thu tốt nhất (VNĐ)')
            plt.title('Tiến hóa doanh thu qua các thế hệ (Thuật toán di truyền)')
            plt.grid(True)
            plt.tight_layout()
            
            # Lưu biểu đồ
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'img')
            os.makedirs(output_dir, exist_ok=True)
            plt.savefig(os.path.join(output_dir, 'genetic_evolution.png'))
            print(f"\nĐã lưu biểu đồ tiến hóa tại: {os.path.join(output_dir, 'genetic_evolution.png')}")
        except Exception as e:
            print(f"Không thể tạo biểu đồ: {e}")
    
if __name__ == "__main__":
    run_genetic_demo() 