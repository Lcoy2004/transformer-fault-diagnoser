import logging
import sys
from database.db_manager import DatabaseManager
from PySide6.QtWidgets import QApplication, QWidget
from config import setup_logging



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()






if __name__ == "__main__":
    setup_logging()### 配置日志系统
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    logger = logging.getLogger(__name__)
    logger.info("主窗口启动")
    db_manager = DatabaseManager() 
    sys.exit(app.exec())