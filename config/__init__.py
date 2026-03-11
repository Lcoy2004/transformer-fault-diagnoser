# config/__init__.py
"""
配置模块：包含日志配置和通知功能
"""

from .logging import setup_logging
from .notification import (
    notify,
    get_notification,
    get_notification_with_time,
    clear_notification
)

__all__ = [
    'setup_logging',
    'notify',
    'get_notification',
    'get_notification_with_time',
    'clear_notification'
]
