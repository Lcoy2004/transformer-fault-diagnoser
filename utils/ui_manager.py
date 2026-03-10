# utils/ui_manager.py
"""
UI管理器：负责处理界面相关的操作
"""

import logging
from datetime import datetime
from PySide6.QtCore import QTimer
from config import notify, get_notification

logger = logging.getLogger(__name__)

class UIManager:
    """UI管理器"""
    
    def __init__(self, main_window):
        """
        初始化UI管理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
        self.init_timers()
        self.init_connections()
    
    def init_timers(self):
        """初始化定时器"""
        # 创建通知更新定时器
        self.notification_timer = QTimer(self.main_window)
        self.notification_timer.timeout.connect(self.update_notification)
        self.notification_timer.start(1000)  # 每1秒更新一次
        
        # 创建时间更新定时器
        self.time_timer = QTimer(self.main_window)
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)  # 每1秒更新一次
    
    def init_connections(self):
        """初始化信号连接"""
        # 这里可以添加信号连接
        pass
    
    def update_notification(self):
        """更新通知标签"""
        message = get_notification()
        if message and hasattr(self.main_window.ui, 'notification_label'):
            self.main_window.ui.notification_label.setText(message)
    
    def update_time(self):
        """更新时间标签"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if hasattr(self.main_window.ui, 'showtime_label'):
            self.main_window.ui.showtime_label.setText(current_time)
    
    def update_progress(self, value):
        """更新进度条"""
        if hasattr(self.main_window.ui, 'progressBar'):
            self.main_window.ui.progressBar.setValue(value)
    
    def update_output(self, text):
        """更新输出文本"""
        if hasattr(self.main_window.ui, 'textEdit_output'):
            self.main_window.ui.textEdit_output.append(text)
    
    def clear_output(self):
        """清空输出文本"""
        if hasattr(self.main_window.ui, 'textEdit_output'):
            self.main_window.ui.textEdit_output.clear()