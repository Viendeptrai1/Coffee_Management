import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase, QFont

from app.views.login_view import LoginView
from app.database.init_db import init_db

def main():
    # Set environment variables
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    # Create application
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set application name and organization
    app.setApplicationName("Quản lý Quán Cafe")
    app.setOrganizationName("Coffee Management")
    
    # Set default font
    font_id = QFontDatabase.addApplicationFont(":/fonts/Roboto-Regular.ttf")
    if font_id != -1:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(font_family)
        app.setFont(font)
    
    # Initialize database
    try:
        init_db()
    except Exception as e:
        print(f"Error initializing database: {e}")
        return 1
    
    # Show login screen
    login = LoginView()
    login.show()
    
    # Run application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 