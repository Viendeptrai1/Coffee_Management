#!/usr/bin/env python3
import os
import sys
import subprocess

# Thêm thư mục gốc vào Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.db_config import Base, engine

def init_database():
    """Khởi tạo cấu trúc cơ sở dữ liệu"""
    # Tạo tất cả các bảng trong cơ sở dữ liệu
    Base.metadata.create_all(bind=engine)
    print("Đã khởi tạo cấu trúc cơ sở dữ liệu!")

def run_script(script_name):
    """Chạy một script Python"""
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    print(f"Đang chạy script: {script_name}")
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"Lỗi: {result.stderr}")

def main():
    """Hàm chính để chạy tất cả các script khởi tạo"""
    print("===== BẮT ĐẦU KHỞI TẠO DỮ LIỆU MẪU =====")
    
    # Khởi tạo cấu trúc cơ sở dữ liệu
    init_database()
    
    # Chạy script tạo dữ liệu menu
    run_script("generate_menu_data.py")
    
    # Chạy script tạo dữ liệu kho hàng và công thức
    run_script("generate_inventory_data.py")
    
    print("===== HOÀN THÀNH KHỞI TẠO DỮ LIỆU MẪU =====")

if __name__ == "__main__":
    main() 