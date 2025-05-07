# Thuật toán di truyền (Genetic Algorithm) cho tối ưu hóa giá menu

Mô-đun này triển khai thuật toán di truyền để tối ưu hóa giá menu của quán cà phê, với mục tiêu tối đa hóa doanh thu dựa trên dữ liệu bán hàng, độ co giãn của cầu theo giá và mối quan hệ cross-selling giữa các món.

## Giới thiệu về thuật toán di truyền

Thuật toán di truyền là một phương pháp tìm kiếm dựa trên các nguyên lý của quá trình tiến hóa tự nhiên. Thuật toán mô phỏng quá trình chọn lọc tự nhiên, nơi các cá thể tốt nhất được chọn để sinh sản, kết hợp với lai ghép và đột biến để tạo ra thế hệ mới tốt hơn.

Các thành phần chính của thuật toán di truyền:

1. **Quần thể (Population)**: Tập hợp các giải pháp tiềm năng (cá thể)
2. **Cá thể (Individual)**: Một giải pháp tiềm năng (trong trường hợp này là một cấu hình giá)
3. **Fitness**: Hàm đánh giá mức độ tốt của một cá thể (doanh thu dự kiến)
4. **Chọn lọc (Selection)**: Quá trình chọn cá thể tốt để sinh sản
5. **Lai ghép (Crossover)**: Kết hợp hai cá thể để tạo ra con cái
6. **Đột biến (Mutation)**: Thay đổi ngẫu nhiên trong cá thể để đảm bảo đa dạng

## Triển khai trong bài toán tối ưu hóa giá menu

Trong bài toán tối ưu hóa giá menu:

- **Cá thể**: Một bộ giá cụ thể cho tất cả các món {item_id: price}
- **Quần thể**: Tập hợp nhiều cấu hình giá khác nhau
- **Fitness**: Doanh thu dự kiến dựa trên mô hình độ co giãn và cross-selling
- **Chọn lọc**: Tournament selection - chọn cá thể có fitness cao hơn từ một tập con
- **Elitism**: Giữ lại một số cá thể tốt nhất cho thế hệ tiếp theo
- **Lai ghép**: Single-point crossover - hoán đổi một phần giá giữa hai cá thể
- **Đột biến**: Thay đổi ngẫu nhiên giá của một số món với xác suất nhất định

## Ưu điểm của thuật toán di truyền

1. **Tìm kiếm song song**: Khám phá nhiều điểm trong không gian tìm kiếm cùng lúc
2. **Khả năng thoát khỏi tối ưu cục bộ**: Nhờ vào cơ chế đột biến và lai ghép
3. **Hiệu quả cho không gian tìm kiếm lớn**: Khi số lượng món và các ràng buộc tăng lên
4. **Dễ triển khai các ràng buộc phức tạp**: Có thể thêm các ràng buộc về cấu trúc giá, marketing, tâm lý,...
5. **Thể hiện tiến trình tối ưu hóa**: Có thể theo dõi sự cải thiện qua các thế hệ

## Cách sử dụng

### 1. Chạy demo dòng lệnh:

```bash
python3 pages/genetic_demo.py
```

Demo này sẽ:
1. Tạo dữ liệu mẫu về menu và lịch sử bán hàng
2. Chạy thuật toán di truyền để tối ưu hóa giá
3. So sánh kết quả với thuật toán Simulated Annealing
4. Hiển thị biểu đồ tiến hóa fitness qua các thế hệ

### 2. Tích hợp vào ứng dụng:

```python
from utils.genetic_algorithm import MenuPriceGeneticOptimizer

# Khởi tạo trình tối ưu hóa
optimizer = MenuPriceGeneticOptimizer(
    menu_items=menu_items,        # Danh sách các món
    sales_data=sales_data,        # Dữ liệu bán hàng
    elasticity_data=elasticity_data,  # (Tùy chọn) Độ co giãn của cầu theo giá
    population_size=50,           # Kích thước quần thể
    elite_size=5,                 # Số lượng cá thể ưu tú giữ lại
    mutation_rate=0.1,            # Tỷ lệ đột biến
    crossover_rate=0.8            # Tỷ lệ lai ghép
)

# Thực hiện tối ưu hóa
best_state, best_value, comparison = optimizer.optimize(
    max_generations=100,          # Số thế hệ tối đa
    convergence_threshold=20,     # Số thế hệ không cải thiện trước khi dừng
    time_limit=None               # Giới hạn thời gian chạy (giây), None nếu không giới hạn
)

# Kết quả
print(f"Doanh thu hiện tại: {comparison['current_revenue']}")
print(f"Doanh thu tối ưu: {comparison['optimized_revenue']}")
print(f"Cải thiện: {comparison['improvement_percentage']}%")
print(f"Số thế hệ: {comparison['generations']}")
print(f"Thời gian thực thi: {comparison['execution_time']} giây")

# Chi tiết thay đổi giá
for change in comparison["price_changes"]:
    print(f"{change['name']}: {change['old_price']} -> {change['new_price']} ({change['change_percentage']}%)")

# Theo dõi tiến trình tối ưu hóa
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 6))
plt.plot(comparison['best_fitness_history'])
plt.xlabel('Thế hệ')
plt.ylabel('Doanh thu tốt nhất (VNĐ)')
plt.title('Tiến hóa doanh thu qua các thế hệ')
plt.grid(True)
plt.show()
```

## Các tham số thuật toán

### Tham số khởi tạo:
- `population_size`: Kích thước quần thể (số lượng cấu hình giá trong mỗi thế hệ)
- `elite_size`: Số lượng cá thể tốt nhất được giữ nguyên qua các thế hệ
- `mutation_rate`: Xác suất xảy ra đột biến trên một gene (giá của một món)
- `crossover_rate`: Xác suất hai cá thể cha mẹ lai ghép (thay vì sao chép trực tiếp)

### Tham số tối ưu hóa:
- `max_generations`: Số thế hệ tối đa trước khi dừng
- `convergence_threshold`: Số thế hệ liên tiếp không cải thiện trước khi dừng
- `time_limit`: Giới hạn thời gian chạy (giây)

## Kết quả và so sánh với các thuật toán khác

Kết quả từ thuật toán bao gồm:
1. **Trạng thái tối ưu** - Giá mới cho từng món
2. **Giá trị tối ưu** - Doanh thu dự kiến với giá mới
3. **Thông tin chi tiết**:
   - Doanh thu hiện tại vs. doanh thu tối ưu
   - Mức cải thiện (giá trị và phần trăm)
   - Chi tiết thay đổi giá cho từng món
   - Số thế hệ đã chạy
   - Lịch sử fitness qua các thế hệ
   - Thời gian thực thi

### So sánh với các thuật toán khác:

1. **So với Hill Climbing**:
   - GA tìm kiếm song song, HC tìm kiếm tuần tự
   - GA ít bị kẹt ở tối ưu cục bộ hơn
   - GA thường cho kết quả tốt hơn nhưng tốn nhiều tính toán hơn

2. **So với Simulated Annealing**:
   - GA mở rộng quy mô tốt hơn với không gian tìm kiếm lớn
   - SA thường nhanh hơn với không gian tìm kiếm nhỏ
   - Cả hai đều có khả năng thoát khỏi tối ưu cục bộ

Trong thực tế, GA thường cho kết quả tốt nhất với các bài toán tối ưu hóa giá phức tạp, đặc biệt khi số lượng món lớn và có nhiều ràng buộc về mối quan hệ giữa các món. 