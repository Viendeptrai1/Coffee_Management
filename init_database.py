#!/usr/bin/env python3

import sys
import os

# Thêm thư mục gốc vào Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.init_db import init_db

if __name__ == "__main__":
    print("Đang khởi tạo cơ sở dữ liệu...")
    init_db()
    print("Khởi tạo cơ sở dữ liệu thành công!")
    print("Các tài khoản mẫu đã được tạo:")
    print("- Admin: username=admin, password=admin123")
    print("- Nhân viên phục vụ: username=nguyenvana, password=123456")
    print("- Nhân viên pha chế: username=tranthib, password=123456") 