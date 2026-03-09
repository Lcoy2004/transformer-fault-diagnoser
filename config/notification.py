import time
from typing import Optional

class NotificationManager:
    """通知管理器，用于管理软件实时处理状态"""
    
    def __init__(self):
        """初始化通知管理器"""
        self.current_message: Optional[str] = None
        self.timestamp: float = 0
    
    def add_notification(self, message: str) -> None:
        """
        添加新通知
        
        Args:
            message: 通知消息内容
        """
        self.current_message = message
        self.timestamp = time.time()
    
    def get_current_notification(self) -> Optional[str]:
        """
        获取当前通知
        
        Returns:
            当前通知消息，如果没有则返回None
        """
        return self.current_message
    
    def get_notification_with_timestamp(self) -> Optional[str]:
        """
        获取带时间戳的当前通知
        
        Returns:
            带时间戳的当前通知消息，如果没有则返回None
        """
        if self.current_message:
            return f"[{time.strftime('%H:%M:%S')}] {self.current_message}"
        return None
    
    def clear_notification(self) -> None:
        """
        清空当前通知
        """
        self.current_message = None
        self.timestamp = 0

# 创建全局通知管理器实例
notification_manager = NotificationManager()

# 便捷函数
def notify(message: str) -> None:
    """
    发送通知的便捷函数
    
    Args:
        message: 通知消息内容
    """
    notification_manager.add_notification(message)

def get_notification() -> Optional[str]:
    """
    获取当前通知的便捷函数
    
    Returns:
        当前通知消息，如果没有则返回None
    """
    return notification_manager.get_current_notification()

def get_notification_with_time() -> Optional[str]:
    """
    获取带时间戳的当前通知的便捷函数
    
    Returns:
        带时间戳的当前通知消息，如果没有则返回None
    """
    return notification_manager.get_notification_with_timestamp()

def clear_notification() -> None:
    """
    清空当前通知的便捷函数
    """
    notification_manager.clear_notification()
