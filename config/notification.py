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


_manager = NotificationManager()
notify = _manager.add
get_notification = _manager.get
