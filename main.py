import logging
import sys
import time
from datetime import datetime
from database.db_manager import DatabaseManager
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from config import setup_logging, notify, get_notification
from ui import mainui_ui

logger = logging.getLogger(__name__)
class WorkerThread(QThread):
    """工作线程，用于执行耗时操作"""
    # 定义信号
    finished = Signal(object)  # 完成信号，传递结果
    error = Signal(str)        # 错误信号，传递错误信息
    progress = Signal(str)     # 进度信号，传递进度信息
    progress_value = Signal(int)  # 进度值信号，传递进度百分比
    
    def __init__(self, func, *args, **kwargs):
        """
        初始化工作线程
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
        """
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        # 将进度回调函数传递给被执行的函数
        if 'progress_callback' not in self.kwargs:
            self.kwargs['progress_callback'] = self.on_progress
        if 'progress_value_callback' not in self.kwargs:
            self.kwargs['progress_value_callback'] = self.on_progress_value
    
    def run(self):
        """线程运行函数"""
        try:
            # 执行耗时操作
            result = self.func(*self.args, **self.kwargs)
            # 发送完成信号
            self.finished.emit(result)
        except Exception as e:
            # 发送错误信号
            self.error.emit(str(e))
    
    def on_progress(self, message):
        """进度回调函数"""
        # 发送进度信号
        self.progress.emit(message)
    
    def on_progress_value(self, value):
        """进度值回调函数"""
        # 发送进度值信号
        self.progress_value.emit(value)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = mainui_ui.Ui_widget()
        self.ui.setupUi(self)
        self.setWindowTitle("变压器故障诊断系统")

        # 重置进度条
        self.ui.progressBar.setValue(0)
        
        # 创建定时器，用于更新通知标签
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_notification)
        self.timer.start(1000)  # 每1秒更新一次
    
    def update_notification(self):
        """更新通知标签"""
        message = get_notification()
        if message:
            self.ui.notification_label.setText(message)
    
    def update_progress_value(self, value):
        """更新进度条"""
        self.ui.progressBar.setValue(value)


if __name__ == "__main__":
    setup_logging()  # 配置日志系统
    app = QApplication(sys.argv)
    # 发送启动通知
    notify("程序已启动")
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    logger.info("++=============窗口初始化完成，最近启动时间：%s=============++", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))    
    sys.exit(app.exec())