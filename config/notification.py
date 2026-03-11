"""
通知管理模块
"""

import time
from typing import Optional


class NotificationManager:
    """通知管理器，用于管理软件实时处理状态"""
    
    def __init__(self):
        self._message: Optional[str] = None
        self._timestamp: float = 0.0
    
    def add(self, message: str) -> None:
        """添加新通知"""
        self._message = message
        self._timestamp = time.time()
    
    def get(self) -> Optional[str]:
        """获取当前通知"""
        return self._message
    
    def get_with_time(self) -> Optional[str]:
        """获取带时间戳的当前通知"""
        if self._message:
            return f"[{time.strftime('%H:%M:%S')}] {self._message}"
        return None
    
    def clear(self) -> None:
        """清空当前通知"""
        self._message = None
        self._timestamp = 0.0


# 全局通知管理器实例
_manager = NotificationManager()

# 便捷函数
notify = _manager.add
get_notification = _manager.get
get_notification_with_time = _manager.get_with_time
clear_notification = _manager.clear
