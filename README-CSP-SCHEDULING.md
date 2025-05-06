# Lập lịch Ca làm việc Tự động dùng Thuật toán CSP

## Giới thiệu

Hệ thống lập lịch ca làm việc tự động sử dụng thuật toán Constraint Satisfaction Problem (CSP) là một tính năng mới được triển khai trong ứng dụng quản lý quán cà phê. Tính năng này giúp người quản lý tạo lịch làm việc tối ưu cho nhân viên, đảm bảo đáp ứng các ràng buộc về thời gian và nguồn lực.

## Thuật toán Constraint Satisfaction Problem (CSP)

CSP là một kỹ thuật trí tuệ nhân tạo được sử dụng để giải quyết các bài toán với các ràng buộc. Một bài toán CSP bao gồm:

1. **Các biến (Variables)**: Đối tượng cần gán giá trị
2. **Miền giá trị (Domains)**: Tập các giá trị có thể gán cho mỗi biến
3. **Các ràng buộc (Constraints)**: Các điều kiện mà assignment phải thỏa mãn

Trong trường hợp lập lịch ca làm việc:
- **Biến**: (nhân_viên, ngày, ca) - đại diện cho việc phân công nhân viên vào một ca cụ thể
- **Miền giá trị**: {0, 1} - 0: không làm, 1: làm
- **Ràng buộc**:
  - Một nhân viên không làm việc nhiều hơn X ca trong một tuần
  - Một nhân viên không làm hai ca trùng thời gian
  - Mỗi ngày phải có ít nhất Y nhân viên làm việc
  - Không phân công ca tối và ca sáng liên tiếp cho cùng một nhân viên

## Kỹ thuật triển khai

Chúng tôi đã triển khai thuật toán Backtracking Search kết hợp với các heuristics để tìm kiếm lời giải hiệu quả:

### 1. Backtracking Search

Thuật toán này tìm kiếm lời giải bằng cách gán giá trị cho từng biến theo chiều sâu, và quay lui khi gặp vi phạm ràng buộc.

```python
def backtrack(assignment):
    if assignment is complete:
        return assignment
    
    var = select_unassigned_variable(variables, assignment)
    for value in order_domain_values(var, assignment):
        if value is consistent with assignment:
            assignment[var] = value
            result = backtrack(assignment)
            if result is not None:
                return result
            del assignment[var]  # Backtrack
    
    return None
```

### 2. Variable Selection Heuristics

Sử dụng heuristic Minimum Remaining Values (MRV) để chọn biến có ít giá trị hợp lệ nhất, kết hợp với việc ưu tiên ngày có ít nhân viên làm việc nhất.

### 3. Value Ordering Heuristics

Sử dụng heuristic Least Constraining Value (LCV) để thử giá trị ít ảnh hưởng đến các biến khác trước.

## Cách sử dụng

1. Trong giao diện Quản lý Ca làm việc, nhấn nút "Tạo lịch tự động"
2. Cấu hình các tham số:
   - Số nhân viên tối thiểu mỗi ngày
   - Số ca tối đa mỗi nhân viên một tuần
3. Xác nhận để hệ thống tạo lịch tự động

## Lợi ích

1. **Tiết kiệm thời gian**: Tạo lịch tự động trong vài giây thay vì mất hàng giờ phân công thủ công
2. **Công bằng**: Đảm bảo sự phân bổ ca làm việc hợp lý giữa các nhân viên
3. **Tối ưu hoá**: Tạo lịch đáp ứng các ràng buộc nghiệp vụ
4. **Linh hoạt**: Dễ dàng điều chỉnh các tham số và ràng buộc

## Phân tích khối lượng công việc

Hệ thống cũng cung cấp tính năng phân tích khối lượng công việc của nhân viên:
- Số ca làm việc mỗi nhân viên
- Tổng số giờ làm việc
- Tỷ lệ phân bổ công việc

Sử dụng nút "Xem khối lượng công việc" để xem thống kê.

## Mở rộng trong tương lai

Hệ thống có thể được mở rộng với các ràng buộc phức tạp hơn như:
- Ưu tiên theo kỹ năng của nhân viên
- Tính toán chi phí và tối ưu hóa lương
- Tích hợp dự báo nhu cầu để phân bổ nhân viên hiệu quả hơn
- Kết hợp với thuật toán học tăng cường (Reinforcement Learning) để cải thiện lịch làm việc dựa trên phản hồi 