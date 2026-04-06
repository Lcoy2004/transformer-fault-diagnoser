"""
UI 管理模块
"""

import logging
from datetime import datetime
from typing import Optional
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMainWindow
from config import get_notification

logger = logging.getLogger(__name__)


class UIManager:
    """UI 管理器"""
    
    def __init__(self, main_window: QMainWindow):
        """
        初始化 UI 管理器
        
        Args:
            main_window: 主窗口实例
        """
        self._window = main_window
        self._ui = main_window.ui
        self._init_timers()
    
    def _init_timers(self) -> None:
        """初始化定时器"""
        # 通知更新定时器
        self._notification_timer = QTimer(self._window)
        self._notification_timer.timeout.connect(self._update_notification)
        self._notification_timer.start(1000)
        
        # 时间更新定时器
        self._time_timer = QTimer(self._window)
        self._time_timer.timeout.connect(self._update_time)
        self._time_timer.start(1000)
        
        # 窗口关闭时停止定时器
        self._window.destroyed.connect(self._stop_timers)
    
    def _stop_timers(self) -> None:
        """停止定时器"""
        if hasattr(self, '_notification_timer') and self._notification_timer:
            self._notification_timer.stop()
        if hasattr(self, '_time_timer') and self._time_timer:
            self._time_timer.stop()
    
    def _update_notification(self) -> None:
        """更新通知标签"""
        message = get_notification()
        if message and hasattr(self._ui, 'notification_label'):
            self._ui.notification_label.setText(message)
    
    def _update_time(self) -> None:
        """更新时间标签"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if hasattr(self._ui, 'showtime_label'):
            self._ui.showtime_label.setText(current_time)
    
    def update_progress(self, value: int) -> None:
        """更新进度条"""
        if hasattr(self._ui, 'progressBar'):
            self._ui.progressBar.setValue(value)
    
    def update_output(self, text: str) -> None:
        """更新输出文本（支持HTML格式）"""
        if hasattr(self._ui, 'textEdit_output'):
            self._ui.textEdit_output.append(text)
    
    def update_output_html(self, html: str) -> None:
        """使用HTML格式更新输出"""
        if hasattr(self._ui, 'textEdit_output'):
            self._ui.textEdit_output.append(html)
    
    def clear_output(self) -> None:
        """清空输出文本"""
        if hasattr(self._ui, 'textEdit_output'):
            self._ui.textEdit_output.clear()
    
    def set_status(self, text: str) -> None:
        """设置状态文本"""
        if hasattr(self._ui, 'status_label'):
            self._ui.status_label.setText(text)
