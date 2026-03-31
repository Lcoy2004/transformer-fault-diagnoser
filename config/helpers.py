"""
通用工具函数模块
"""

import os
import sys
from typing import Callable, Optional

from config import notify


def get_models_dir() -> str:
    """
    获取模型目录路径（兼容打包环境）
    
    Returns:
        模型目录路径
    """
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), 'models')
    else:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(root_dir, 'models')


def ensure_models_dir() -> str:
    """
    确保模型目录存在
    
    Returns:
        模型目录路径
    """
    models_dir = get_models_dir()
    os.makedirs(models_dir, exist_ok=True)
    return models_dir


class ProgressHelper:
    """进度回调辅助类"""
    
    def __init__(
        self,
        progress_callback: Optional[Callable[[str], None]] = None,
        progress_value_callback: Optional[Callable[[int], None]] = None,
        use_notify: bool = True
    ):
        """
        初始化进度辅助器
        
        Args:
            progress_callback: 进度消息回调
            progress_value_callback: 进度值回调
            use_notify: 是否使用全局通知
        """
        self._callback = progress_callback
        self._value_callback = progress_value_callback
        self._use_notify = use_notify
    
    def send(self, message: str) -> None:
        """发送进度消息"""
        if self._callback:
            self._callback(message)
        elif self._use_notify:
            notify(message)
    
    def update(self, value: int) -> None:
        """更新进度值"""
        if self._value_callback:
            self._value_callback(value)
    
    def send_and_update(self, message: str, value: int) -> None:
        """发送消息并更新进度"""
        self.send(message)
        self.update(value)
