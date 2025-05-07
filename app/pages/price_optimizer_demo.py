import sys
import os
import json
import random
from pprint import pprint

# Đảm bảo có thể import từ thư mục app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

def run_demo():
    """Chạy demo thuật toán local search"""
    print("===== MINH HỌA THUẬT TOÁN LOCAL SEARCH TRONG TỐI ƯU HÓA GIÁ MENU =====")
    
    # Tạo dữ liệu mẫu
    menu_items, sales_data, elasticity_data = generate_sample_data()
    
    # In menu hiện tại
    print("\n----- MENU HIỆN TẠI -----")
    print(f"{'ID':<3} {'TÊN MÓN':<20} {'GIÁ (VNĐ)':<12}")
    for item in menu_items:
        print(f"{item['id']:<3} {item['name']:<20} {item['price']:<12,.0f}")
    
    # Khởi tạo trình tối ưu hóa
    optimizer = MenuPriceOptimizer(
        menu_items=menu_items,
        sales_data=sales_data,
        elasticity_data=elasticity_data
    )
    
    # Demo Hill Climbing
    print("\n\n----- THUẬT TOÁN HILL CLIMBING -----")
    hill_climbing_params = {
        "max_iterations": 1000,
        "step_size": 0.05,
        "plateau_iterations": 100
    }
    print("Tham số:", hill_climbing_params)
    
    # Thực hiện tối ưu hóa với Hill Climbing
    print("Đang thực hiện tối ưu hóa...")
    hc_best_state, hc_best_value, hc_comparison = optimizer.optimize_menu_prices(
        algorithm="hill_climbing", **hill_climbing_params
    )
    
    # In kết quả
    print("\nKết quả Hill Climbing:")
    print(f"Doanh thu hiện tại: {hc_comparison['current_revenue']:,.0f} VNĐ")
    print(f"Doanh thu tối ưu:   {hc_comparison['optimized_revenue']:,.0f} VNĐ")
    print(f"Cải thiện:          {hc_comparison['improvement']:,.0f} VNĐ ({hc_comparison['improvement_percentage']:.2f}%)")
    
    # In chi tiết thay đổi giá
    if hc_comparison['price_changes']:
        print("\nChi tiết thay đổi giá:")
        print(f"{'TÊN MÓN':<20} {'GIÁ CŨ':<12} {'GIÁ MỚI':<12} {'THAY ĐỔI':<12} {'%':<6}")
        for change in hc_comparison['price_changes']:
            print(f"{change['name']:<20} {change['old_price']:<12,.0f} {change['new_price']:<12,.0f} {change['change']:<12,.0f} {change['change_percentage']:<6.2f}%")
    
    # Demo Simulated Annealing
    print("\n\n----- THUẬT TOÁN SIMULATED ANNEALING -----")
    sa_params = {
        "initial_temp": 1.0,
        "cooling_rate": 0.995,
        "min_temp": 0.01,
        "max_iterations": 10000,
        "step_size": 0.05
    }
    print("Tham số:", sa_params)
    
    # Thực hiện tối ưu hóa với Simulated Annealing
    print("Đang thực hiện tối ưu hóa...")
    sa_best_state, sa_best_value, sa_comparison = optimizer.optimize_menu_prices(
        algorithm="simulated_annealing", **sa_params
    )
    
    # In kết quả
    print("\nKết quả Simulated Annealing:")
    print(f"Doanh thu hiện tại: {sa_comparison['current_revenue']:,.0f} VNĐ")
    print(f"Doanh thu tối ưu:   {sa_comparison['optimized_revenue']:,.0f} VNĐ")
    print(f"Cải thiện:          {sa_comparison['improvement']:,.0f} VNĐ ({sa_comparison['improvement_percentage']:.2f}%)")
    
    # In chi tiết thay đổi giá
    if sa_comparison['price_changes']:
        print("\nChi tiết thay đổi giá:")
        print(f"{'TÊN MÓN':<20} {'GIÁ CŨ':<12} {'GIÁ MỚI':<12} {'THAY ĐỔI':<12} {'%':<6}")
        for change in sa_comparison['price_changes']:
            print(f"{change['name']:<20} {change['old_price']:<12,.0f} {change['new_price']:<12,.0f} {change['change']:<12,.0f} {change['change_percentage']:<6.2f}%")
    
    # So sánh hai thuật toán
    print("\n\n----- SO SÁNH HAI THUẬT TOÁN -----")
    print(f"Hill Climbing:       {hc_comparison['optimized_revenue']:,.0f} VNĐ (+{hc_comparison['improvement_percentage']:.2f}%)")
    print(f"Simulated Annealing: {sa_comparison['optimized_revenue']:,.0f} VNĐ (+{sa_comparison['improvement_percentage']:.2f}%)")
    
    winner = "Simulated Annealing" if sa_comparison['optimized_revenue'] > hc_comparison['optimized_revenue'] else "Hill Climbing"
    print(f"\nThuật toán tốt hơn: {winner}")

if __name__ == "__main__":
    run_demo() 