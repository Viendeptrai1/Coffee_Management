# Tính năng Quản lý Ca làm việc

## Mô tả
Tính năng quản lý ca làm việc cho phép người quản lý lập lịch và theo dõi ca làm việc của nhân viên. Giao diện dạng lịch tuần giúp dễ dàng xem và quản lý ca làm việc.

## Các chức năng chính
1. **Xem lịch làm việc** theo tuần với các nhân viên và ca làm việc của họ
2. **Thêm ca làm việc mới** cho nhân viên với ngày, giờ bắt đầu và kết thúc 
3. **Chỉnh sửa ca làm việc** đã tồn tại
4. **Xóa ca làm việc** không cần thiết
5. **Đánh dấu trạng thái** ca làm việc (lịch, đang làm, đã làm, vắng)
6. **Điều hướng thời gian** dễ dàng (tuần trước, tuần sau, trở về tuần hiện tại)
7. **Phân biệt ca làm việc bằng màu sắc** theo trạng thái

## Cách sử dụng

1. **Xem lịch làm việc**: 
   - Chọn tab "Quản lý ca làm việc" trong giao diện quản lý
   - Dùng nút điều hướng (◀, ▶, Tuần này) để thay đổi tuần hiện tại

2. **Thêm ca làm việc mới**:
   - Click chuột phải vào ô tương ứng với nhân viên và ngày muốn thêm ca
   - Chọn "Thêm ca làm việc" và nhập thông tin ca làm việc

3. **Chỉnh sửa/Xóa/Đánh dấu ca làm việc**:
   - Click chuột phải vào ca làm việc đã tồn tại
   - Chọn hành động tương ứng từ menu

## Cấu trúc của tính năng

1. **Model**: `Shift` trong `app/models/models.py`
   - Các trường: staff_id, date, start_time, end_time, status

2. **Controller**: `ShiftController` trong `app/controllers/shift_controller.py`
   - Các phương thức: get_all_shifts, get_shifts_by_staff, get_shifts_by_week, add_shift, update_shift, delete_shift

3. **View**: `ShiftView` và `WeeklyShiftTable` trong `app/views/shift_view.py`
   - Giao diện người dùng cho quản lý ca làm việc
   - Bảng hiển thị ca làm việc theo tuần
   - Dialog thêm/sửa ca làm việc

## Các trạng thái của ca làm việc

1. **Lịch** (màu vàng nhạt): Ca làm việc đã được lên lịch
2. **Đang làm** (màu xanh lá nhạt): Nhân viên đang trong ca làm việc
3. **Đã làm** (màu xanh dương nhạt): Ca làm việc đã hoàn thành
4. **Vắng** (màu đỏ nhạt): Nhân viên vắng mặt trong ca làm việc 