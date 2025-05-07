# Tối ưu hóa giá menu với thuật toán Local Search

Mô-đun này triển khai các thuật toán local search để tối ưu hóa giá menu của quán cà phê, nhằm tối đa hóa doanh thu dựa trên dữ liệu bán hàng và độ co giãn của cầu theo giá.

## Giới thiệu

Thuật toán local search trong ứng dụng này giải quyết bài toán tối ưu hóa giá menu nhằm tối đa hóa doanh thu. Việc tối ưu hóa dựa trên:

1. **Dữ liệu bán hàng hiện tại** - Số lượng từng món đã bán
2. **Độ co giãn của cầu theo giá** - Mô tả mức độ thay đổi của số lượng bán ra khi giá thay đổi
3. **Hiệu ứng cross-selling** - Tác động của việc thay đổi giá một món đến doanh số của các món khác

## Các thuật toán được triển khai

### 1. Hill Climbing

Thuật toán Hill Climbing là một thuật toán tối ưu hóa đơn giản:
- Bắt đầu từ một trạng thái (giá hiện tại)
- Tạo các trạng thái lân cận ngẫu nhiên (thay đổi giá một món)
- Chuyển đến trạng thái lân cận nếu nó tốt hơn trạng thái hiện tại
- Dừng khi không thể cải thiện thêm

Ưu điểm:
- Đơn giản, dễ triển khai
- Hiệu quả trong không gian tìm kiếm "trơn tru"

Nhược điểm:
- Có thể bị kẹt ở tối ưu cục bộ
- Không hiệu quả trong không gian tìm kiếm phức tạp

### 2. Simulated Annealing

Thuật toán Simulated Annealing là một cải tiến của Hill Climbing:
- Bắt đầu từ một trạng thái (giá hiện tại)
- Tạo các trạng thái lân cận ngẫu nhiên (thay đổi giá một món)
- **Luôn chấp nhận** trạng thái lân cận nếu nó tốt hơn
- **Đôi khi chấp nhận** trạng thái lân cận kém hơn với một xác suất nhất định
- Xác suất chấp nhận trạng thái kém hơn giảm dần theo thời gian ("nhiệt độ" giảm)

Ưu điểm:
- Có khả năng thoát khỏi tối ưu cục bộ
- Hiệu quả trong không gian tìm kiếm phức tạp
- Thường tìm được giải pháp tốt hơn Hill Climbing

Nhược điểm:
- Phức tạp hơn trong việc điều chỉnh tham số
- Có thể mất nhiều thời gian hơn để hội tụ

## Mô hình hóa

### 1. Độ co giãn của cầu theo giá

Độ co giãn của cầu theo giá mô tả mối quan hệ giữa sự thay đổi giá và sự thay đổi số lượng:

```
% Thay đổi số lượng = Độ co giãn × % Thay đổi giá
```

- Độ co giãn thường là số âm (giá tăng → số lượng giảm)
- Đối với đồ uống, độ co giãn thường nằm trong khoảng từ -1 đến -2
- Ví dụ: Độ co giãn -1.5 nghĩa là khi giá tăng 10%, số lượng bán ra giảm 15%

### 2. Hiệu ứng cross-selling

Mô hình còn tính đến mối quan hệ giữa các món:
- Một số món thường được mua cùng nhau (ví dụ: cà phê và bánh)
- Khi giá một món thay đổi, có thể ảnh hưởng đến doanh số của các món khác
- Mối quan hệ này được tính toán từ dữ liệu đơn hàng (các món xuất hiện cùng nhau trong đơn hàng)

## Cách sử dụng

### Chạy demo dòng lệnh:

```bash
python3 pages/price_optimizer_demo.py
```

Demo này sẽ:
1. Tạo dữ liệu mẫu về menu và lịch sử bán hàng
2. Chạy thuật toán Hill Climbing
3. Chạy thuật toán Simulated Annealing
4. So sánh kết quả của hai thuật toán

### Sử dụng thông qua giao diện:

```bash
streamlit run pages/price_optimizer.py
```

Giao diện cho phép:
1. Xem menu hiện tại
2. Chọn thuật toán và điều chỉnh tham số
3. Thực hiện tối ưu hóa
4. Xem kết quả trực quan qua bảng và biểu đồ

### Tích hợp vào ứng dụng:

```python
from utils.local_search import MenuPriceOptimizer

# Khởi tạo trình tối ưu hóa
optimizer = MenuPriceOptimizer(
    menu_items=menu_items,        # Danh sách các món
    sales_data=sales_data,        # Dữ liệu bán hàng
    elasticity_data=elasticity_data  # (Tùy chọn) Độ co giãn của cầu theo giá
)

# Thực hiện tối ưu hóa với Hill Climbing
best_state, best_value, comparison = optimizer.optimize_menu_prices(
    algorithm="hill_climbing",
    max_iterations=1000,
    step_size=0.05,
    plateau_iterations=100
)

# HOẶC thực hiện tối ưu hóa với Simulated Annealing
best_state, best_value, comparison = optimizer.optimize_menu_prices(
    algorithm="simulated_annealing",
    initial_temp=1.0,
    cooling_rate=0.995,
    min_temp=0.01,
    max_iterations=10000,
    step_size=0.05
)

# Kết quả
print(f"Doanh thu hiện tại: {comparison['current_revenue']}")
print(f"Doanh thu tối ưu: {comparison['optimized_revenue']}")
print(f"Cải thiện: {comparison['improvement_percentage']}%")

# Chi tiết thay đổi giá
for change in comparison["price_changes"]:
    print(f"{change['name']}: {change['old_price']} -> {change['new_price']} ({change['change_percentage']}%)")
```

## Các tham số thuật toán

### Hill Climbing:
- `max_iterations`: Số lần lặp tối đa
- `step_size`: Kích thước bước thay đổi giá (tỷ lệ phần trăm)
- `plateau_iterations`: Số lần lặp tối đa khi không có cải thiện

### Simulated Annealing:
- `initial_temp`: Nhiệt độ ban đầu (cao = nhiều khả năng chấp nhận giải pháp kém hơn)
- `cooling_rate`: Tỷ lệ làm mát (gần 1 = làm mát chậm)
- `min_temp`: Nhiệt độ tối thiểu (ngưỡng dừng)
- `max_iterations`: Số lần lặp tối đa
- `step_size`: Kích thước bước thay đổi giá (tỷ lệ phần trăm)

## Kết quả và phân tích

Kết quả từ thuật toán bao gồm:
1. **Trạng thái tối ưu** - Giá mới cho từng món
2. **Giá trị tối ưu** - Doanh thu dự kiến với giá mới
3. **Bảng so sánh chi tiết**:
   - Doanh thu hiện tại vs. doanh thu tối ưu
   - Mức cải thiện (giá trị và phần trăm)
   - Chi tiết thay đổi giá cho từng món

Trong nhiều trường hợp, Simulated Annealing thường cho kết quả tốt hơn Hill Climbing, đặc biệt với bài toán phức tạp. 