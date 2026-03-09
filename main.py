import logging
import sys
from datetime import datetime
from database.db_manager import DatabaseManager
from PySide6.QtWidgets import QApplication, QWidget
from config import setup_logging


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    setup_logging()  # 配置日志系统
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    logger = logging.getLogger(__name__)
    logger.info("++=============窗口初始化完成，最近启动时间：%s=============++", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    db_manager = DatabaseManager()
    sys.exit(app.exec())