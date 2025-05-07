import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import random
import json
import sys
import os
import time

# Đảm bảo có thể import từ thư mục app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.local_search import MenuPriceOptimizer
from utils.genetic_algorithm import MenuPriceGeneticOptimizer

def generate_sample_data():
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

def display_algorithm_info(algorithm):
    """Hiển thị thông tin về thuật toán được chọn"""
    if algorithm == "hill_climbing":
        st.info("""
        **Hill Climbing** là thuật toán tối ưu hóa đơn giản:
        - Bắt đầu từ một trạng thái (giá hiện tại)
        - Tạo các trạng thái lân cận ngẫu nhiên (thay đổi giá một món)
        - Chuyển đến trạng thái lân cận nếu nó tốt hơn trạng thái hiện tại
        - Dừng khi không thể cải thiện thêm
        
        Ưu điểm: Đơn giản, nhanh chóng
        Nhược điểm: Có thể bị kẹt ở tối ưu cục bộ
        """)
    elif algorithm == "simulated_annealing":
        st.info("""
        **Simulated Annealing** là thuật toán cải tiến từ Hill Climbing:
        - Bắt đầu từ một trạng thái (giá hiện tại)
        - Tạo các trạng thái lân cận ngẫu nhiên
        - **Luôn chấp nhận** trạng thái lân cận nếu nó tốt hơn
        - **Đôi khi chấp nhận** trạng thái lân cận kém hơn với một xác suất nhất định
        - Xác suất chấp nhận trạng thái kém hơn giảm dần theo thời gian ("nhiệt độ" giảm)
        
        Ưu điểm: Có khả năng thoát khỏi tối ưu cục bộ
        Nhược điểm: Phức tạp hơn, cần điều chỉnh tham số nhiệt độ và làm mát
        """)
    else:  # genetic_algorithm
        st.info("""
        **Thuật toán di truyền (Genetic Algorithm)** là phương pháp tối ưu hóa dựa trên tiến hóa tự nhiên:
        - Làm việc với một quần thể các giải pháp thay vì một giải pháp duy nhất
        - Sử dụng các phép toán chọn lọc, lai ghép và đột biến
        - Các giải pháp tốt hơn có xu hướng sống sót và sinh sản
        - Quá trình tiến hóa dần dần cải thiện quần thể
        
        Ưu điểm: 
        - Tìm kiếm song song nhiều điểm trong không gian giải pháp
        - Khả năng thoát khỏi tối ưu cục bộ cao
        - Hiệu quả cho không gian tìm kiếm lớn và phức tạp
        
        Nhược điểm: 
        - Phức tạp nhất trong 3 thuật toán
        - Có nhiều tham số cần điều chỉnh
        - Có thể tốn nhiều tài nguyên tính toán hơn
        """)

def run_price_optimization():
    st.title("Tối ưu hóa giá menu")
    st.write("Ứng dụng minh họa các thuật toán AI để tối ưu hóa giá menu")
    
    # Tạo hoặc lấy dữ liệu mẫu
    if 'menu_items' not in st.session_state:
        menu_items, sales_data, elasticity_data = generate_sample_data()
        st.session_state['menu_items'] = menu_items
        st.session_state['sales_data'] = sales_data
        st.session_state['elasticity_data'] = elasticity_data
    
    # Hiển thị menu hiện tại
    st.subheader("Menu hiện tại")
    menu_df = pd.DataFrame(st.session_state['menu_items'])
    st.dataframe(menu_df[["id", "name", "price", "category_id"]])
    
    # Chọn thuật toán
    col1, col2 = st.columns(2)
    
    with col1:
        algorithm = st.selectbox(
            "Chọn thuật toán",
            ["hill_climbing", "simulated_annealing", "genetic_algorithm"],
            index=1,
            format_func=lambda x: {
                "hill_climbing": "Hill Climbing", 
                "simulated_annealing": "Simulated Annealing",
                "genetic_algorithm": "Genetic Algorithm"
            }.get(x, x)
        )
    
    # Hiển thị thông tin về thuật toán
    display_algorithm_info(algorithm)
    
    # Tham số thuật toán
    st.subheader("Tham số thuật toán")
    
    if algorithm == "hill_climbing":
        col1, col2 = st.columns(2)
        with col1:
            max_iterations = st.slider("Số lần lặp tối đa", 100, 2000, 1000, 100)
            step_size = st.slider("Kích thước bước", 0.01, 0.20, 0.05, 0.01)
        with col2:
            plateau_iterations = st.slider("Số lần lặp tối đa khi không cải thiện", 10, 300, 100, 10)
        
        params = {
            "max_iterations": max_iterations,
            "step_size": step_size,
            "plateau_iterations": plateau_iterations
        }
        
    elif algorithm == "simulated_annealing":
        col1, col2 = st.columns(2)
        with col1:
            initial_temp = st.slider("Nhiệt độ ban đầu", 0.1, 5.0, 1.0, 0.1)
            cooling_rate = st.slider("Tỷ lệ làm mát", 0.95, 0.999, 0.995, 0.001)
            min_temp = st.slider("Nhiệt độ tối thiểu", 0.001, 0.1, 0.01, 0.001)
        with col2:
            max_iterations = st.slider("Số lần lặp tối đa", 1000, 20000, 10000, 1000)
            step_size = st.slider("Kích thước bước", 0.01, 0.20, 0.05, 0.01)
        
        params = {
            "initial_temp": initial_temp,
            "cooling_rate": cooling_rate,
            "min_temp": min_temp,
            "max_iterations": max_iterations,
            "step_size": step_size
        }
        
    else:  # genetic_algorithm
        col1, col2 = st.columns(2)
        with col1:
            population_size = st.slider("Kích thước quần thể", 10, 100, 50, 5)
            elite_size = st.slider("Số lượng cá thể ưu tú", 1, 10, 5, 1)
            mutation_rate = st.slider("Tỷ lệ đột biến", 0.01, 0.3, 0.1, 0.01)
        with col2:
            crossover_rate = st.slider("Tỷ lệ lai ghép", 0.5, 1.0, 0.8, 0.05)
            max_generations = st.slider("Số thế hệ tối đa", 10, 200, 100, 10)
            convergence_threshold = st.slider("Ngưỡng hội tụ", 5, 50, 20, 5)
        
        ga_init_params = {
            "population_size": population_size,
            "elite_size": elite_size,
            "mutation_rate": mutation_rate,
            "crossover_rate": crossover_rate
        }
        
        ga_optimize_params = {
            "max_generations": max_generations,
            "convergence_threshold": convergence_threshold
        }
    
    # Nút tối ưu
    if st.button("Tối ưu hóa giá menu"):
        with st.spinner("Đang thực hiện tối ưu hóa..."):
            start_time = time.time()
            
            if algorithm in ["hill_climbing", "simulated_annealing"]:
                # Khởi tạo trình tối ưu hóa local search
                optimizer = MenuPriceOptimizer(
                    menu_items=st.session_state['menu_items'],
                    sales_data=st.session_state['sales_data'],
                    elasticity_data=st.session_state['elasticity_data']
                )
                
                # Thực hiện tối ưu hóa
                best_state, best_value, comparison = optimizer.optimize_menu_prices(
                    algorithm=algorithm, **params
                )
                
            else:  # genetic_algorithm
                # Khởi tạo trình tối ưu hóa di truyền
                optimizer = MenuPriceGeneticOptimizer(
                    menu_items=st.session_state['menu_items'],
                    sales_data=st.session_state['sales_data'],
                    elasticity_data=st.session_state['elasticity_data'],
                    **ga_init_params
                )
                
                # Thực hiện tối ưu hóa
                best_state, best_value, comparison = optimizer.optimize(**ga_optimize_params)
            
            execution_time = time.time() - start_time
            
            # Thêm thời gian thực thi nếu chưa có
            if 'execution_time' not in comparison:
                comparison['execution_time'] = execution_time
            
            # Lưu kết quả
            st.session_state['optimization_result'] = {
                "algorithm": algorithm,
                "best_state": best_state,
                "best_value": best_value,
                "comparison": comparison
            }
    
    # Hiển thị kết quả nếu có
    if 'optimization_result' in st.session_state:
        result = st.session_state['optimization_result']
        comparison = result["comparison"]
        used_algorithm = result["algorithm"]
        
        st.subheader("Kết quả tối ưu hóa")
        
        # Hiển thị thuật toán sử dụng
        algorithm_names = {
            "hill_climbing": "Hill Climbing",
            "simulated_annealing": "Simulated Annealing",
            "genetic_algorithm": "Genetic Algorithm"
        }
        st.write(f"Thuật toán sử dụng: **{algorithm_names.get(used_algorithm, used_algorithm)}**")
        
        # Hiển thị tóm tắt
        current_revenue = comparison["current_revenue"]
        optimized_revenue = comparison["optimized_revenue"]
        improvement = comparison["improvement"]
        improvement_percentage = comparison["improvement_percentage"]
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Doanh thu hiện tại", f"{current_revenue:,.0f} VNĐ")
        col2.metric("Doanh thu tối ưu", f"{optimized_revenue:,.0f} VNĐ")
        col3.metric("Cải thiện", f"{improvement:,.0f} VNĐ", f"{improvement_percentage:.2f}%")
        
        # Hiển thị thời gian thực thi và thông tin bổ sung
        st.write(f"Thời gian thực thi: {comparison.get('execution_time', 0):.2f} giây")
        
        # Hiển thị số thế hệ nếu là thuật toán di truyền
        if used_algorithm == "genetic_algorithm" and "generations" in comparison:
            st.write(f"Số thế hệ: {comparison['generations']}")
        
        # Hiển thị bảng thay đổi giá
        st.subheader("Chi tiết thay đổi giá")
        
        if comparison['price_changes']:
            price_changes_df = pd.DataFrame(comparison['price_changes'])
            
            # Format để hiển thị đẹp hơn
            price_changes_df["old_price"] = price_changes_df["old_price"].apply(lambda x: f"{x:,.0f} VNĐ")
            price_changes_df["new_price"] = price_changes_df["new_price"].apply(lambda x: f"{x:,.0f} VNĐ")
            price_changes_df["change"] = price_changes_df["change"].apply(lambda x: f"{x:,.0f} VNĐ")
            price_changes_df["change_percentage"] = price_changes_df["change_percentage"].apply(lambda x: f"{x:.2f}%")
            
            st.dataframe(price_changes_df[["name", "old_price", "new_price", "change", "change_percentage"]])
            
            # Trực quan hóa thay đổi giá
            orig_changes_df = pd.DataFrame(comparison['price_changes'])
            fig = px.bar(
                orig_changes_df, 
                x="name", 
                y="change_percentage",
                color="change_percentage",
                labels={"name": "Món", "change_percentage": "Thay đổi (%)"},
                title="Phần trăm thay đổi giá theo món"
            )
            st.plotly_chart(fig)
            
            # Hiển thị biểu đồ tiến hóa nếu là thuật toán di truyền
            if used_algorithm == "genetic_algorithm" and "best_fitness_history" in comparison:
                st.subheader("Tiến hóa doanh thu qua các thế hệ")
                
                history_df = pd.DataFrame({
                    "Thế hệ": range(len(comparison["best_fitness_history"])),
                    "Doanh thu tốt nhất": comparison["best_fitness_history"]
                })
                
                fig2 = px.line(
                    history_df,
                    x="Thế hệ",
                    y="Doanh thu tốt nhất",
                    title="Tiến hóa doanh thu qua các thế hệ (Genetic Algorithm)"
                )
                fig2.update_layout(xaxis_title="Thế hệ", yaxis_title="Doanh thu (VNĐ)")
                st.plotly_chart(fig2)
                
        else:
            st.info("Không có thay đổi giá nào được đề xuất.")
            
        # Thêm nút để so sánh các thuật toán
        if st.button("So sánh tất cả thuật toán"):
            with st.spinner("Đang so sánh các thuật toán..."):
                # Chạy cả 3 thuật toán và so sánh
                compare_algorithms(st.session_state['menu_items'], 
                                    st.session_state['sales_data'], 
                                    st.session_state['elasticity_data'])

def compare_algorithms(menu_items, sales_data, elasticity_data):
    """So sánh các thuật toán tối ưu hóa giá"""
    st.subheader("So sánh các thuật toán tối ưu hóa giá")
    
    # Tham số cho mỗi thuật toán
    hc_params = {
        "max_iterations": 1000,
        "step_size": 0.05,
        "plateau_iterations": 100
    }
    
    sa_params = {
        "initial_temp": 1.0,
        "cooling_rate": 0.995,
        "min_temp": 0.01,
        "max_iterations": 10000,
        "step_size": 0.05
    }
    
    ga_init_params = {
        "population_size": 50,
        "elite_size": 5,
        "mutation_rate": 0.1,
        "crossover_rate": 0.8
    }
    
    ga_optimize_params = {
        "max_generations": 100,
        "convergence_threshold": 20
    }
    
    # Khởi tạo trình tối ưu hóa local search
    local_optimizer = MenuPriceOptimizer(
        menu_items=menu_items,
        sales_data=sales_data,
        elasticity_data=elasticity_data
    )
    
    # Khởi tạo trình tối ưu hóa di truyền
    genetic_optimizer = MenuPriceGeneticOptimizer(
        menu_items=menu_items,
        sales_data=sales_data,
        elasticity_data=elasticity_data,
        **ga_init_params
    )
    
    # Chạy Hill Climbing
    start_time = time.time()
    hc_best_state, hc_best_value, hc_comparison = local_optimizer.optimize_menu_prices(
        algorithm="hill_climbing", **hc_params
    )
    hc_time = time.time() - start_time
    hc_comparison['execution_time'] = hc_time
    
    # Chạy Simulated Annealing
    start_time = time.time()
    sa_best_state, sa_best_value, sa_comparison = local_optimizer.optimize_menu_prices(
        algorithm="simulated_annealing", **sa_params
    )
    sa_time = time.time() - start_time
    sa_comparison['execution_time'] = sa_time
    
    # Chạy Genetic Algorithm
    start_time = time.time()
    ga_best_state, ga_best_value, ga_comparison = genetic_optimizer.optimize(**ga_optimize_params)
    ga_time = time.time() - start_time
    if 'execution_time' not in ga_comparison:
        ga_comparison['execution_time'] = ga_time
    
    # Tạo bảng so sánh
    comparison_data = {
        "Thuật toán": ["Hill Climbing", "Simulated Annealing", "Genetic Algorithm"],
        "Doanh thu tối ưu": [hc_comparison['optimized_revenue'], 
                            sa_comparison['optimized_revenue'], 
                            ga_comparison['optimized_revenue']],
        "Cải thiện (%)": [hc_comparison['improvement_percentage'], 
                        sa_comparison['improvement_percentage'], 
                        ga_comparison['improvement_percentage']],
        "Thời gian thực thi (giây)": [hc_comparison['execution_time'], 
                                    sa_comparison['execution_time'], 
                                    ga_comparison['execution_time']]
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    
    # Format để hiển thị đẹp hơn
    df_comparison["Doanh thu tối ưu"] = df_comparison["Doanh thu tối ưu"].apply(lambda x: f"{x:,.0f} VNĐ")
    df_comparison["Cải thiện (%)"] = df_comparison["Cải thiện (%)"].apply(lambda x: f"{x:.2f}%")
    df_comparison["Thời gian thực thi (giây)"] = df_comparison["Thời gian thực thi (giây)"].apply(lambda x: f"{x:.4f}s")
    
    st.table(df_comparison)
    
    # Hiển thị biểu đồ so sánh
    comparison_chart_data = {
        "Thuật toán": ["Hill Climbing", "Simulated Annealing", "Genetic Algorithm"],
        "Doanh thu tối ưu": [hc_comparison['optimized_revenue'], 
                            sa_comparison['optimized_revenue'], 
                            ga_comparison['optimized_revenue']],
        "Thời gian thực thi (giây)": [hc_comparison['execution_time'], 
                                    sa_comparison['execution_time'], 
                                    ga_comparison['execution_time']]
    }
    
    df_chart = pd.DataFrame(comparison_chart_data)
    
    # Biểu đồ so sánh doanh thu
    fig1 = px.bar(
        df_chart,
        x="Thuật toán",
        y="Doanh thu tối ưu",
        title="So sánh doanh thu tối ưu giữa các thuật toán",
        color="Thuật toán"
    )
    st.plotly_chart(fig1)
    
    # Biểu đồ so sánh thời gian thực thi
    fig2 = px.bar(
        df_chart,
        x="Thuật toán",
        y="Thời gian thực thi (giây)",
        title="So sánh thời gian thực thi giữa các thuật toán",
        color="Thuật toán"
    )
    st.plotly_chart(fig2)
    
    # Hiển thị kết luận
    best_revenue_idx = df_chart["Doanh thu tối ưu"].argmax()
    best_time_idx = df_chart["Thời gian thực thi (giây)"].argmin()
    
    st.markdown(f"""
    ### Kết luận:
    
    - **Thuật toán tốt nhất về doanh thu**: {df_chart["Thuật toán"][best_revenue_idx]}
    - **Thuật toán nhanh nhất**: {df_chart["Thuật toán"][best_time_idx]}
    
    #### Nhận xét:
    
    - Hill Climbing là thuật toán đơn giản nhất, thường nhanh nhưng có thể bị kẹt ở tối ưu cục bộ
    - Simulated Annealing cân bằng tốt giữa tốc độ và chất lượng kết quả, có khả năng thoát khỏi tối ưu cục bộ
    - Genetic Algorithm mạnh mẽ hơn với không gian tìm kiếm lớn và phức tạp, nhưng có thể tốn nhiều tài nguyên hơn
    
    Tùy thuộc vào yêu cầu cụ thể, bạn có thể chọn thuật toán phù hợp: nếu cần kết quả nhanh, chọn Hill Climbing; nếu cần cân bằng, chọn Simulated Annealing; nếu cần kết quả tốt nhất có thể và thời gian không phải vấn đề quan trọng, chọn Genetic Algorithm.
    """)

if __name__ == "__main__":
    run_price_optimization() 