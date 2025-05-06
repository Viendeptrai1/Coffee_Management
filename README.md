# Ứng dụng Quản lý Quán Cafe

Ứng dụng quản lý quán cafe được xây dựng bằng Python và PyQt5, cung cấp các chức năng quản lý cơ bản cho quán cafe.

## Các tính năng chính

- Quản lý món ăn/đồ uống
- Quản lý bàn
- Quản lý hóa đơn
- Quản lý nhân viên
- Thống kê doanh thu
- Dự đoán xu hướng bán hàng

## Quy trình hoạt động

1. Khách đến quán
2. Nhân viên chọn bàn → tạo hóa đơn
3. Nhập món ăn/đồ uống → chọn số lượng
4. Gửi hóa đơn đến quầy (hoặc bếp)
5. Khi khách thanh toán → in hóa đơn → chuyển bàn về trạng thái trống
6. Dữ liệu lưu lại để thống kê / phân tích / học máy

## Cài đặt

1. Cài đặt các thư viện cần thiết:
   ```
   pip install -r requirements.txt
   ```

2. Chạy ứng dụng:
   ```
   python app/main.py
   ``` 