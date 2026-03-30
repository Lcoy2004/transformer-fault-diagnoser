"""
日志配置模块
"""

import glob
import logging
import os
import sys
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler


def get_logs_dir() -> str:
    """
    获取日志目录的绝对路径
    
    Returns:
        str: 日志目录的绝对路径
    """
    if getattr(sys, 'frozen', False):
        # 打包后：从可执行文件所在目录找
        return os.path.join(os.path.dirname(sys.executable), 'logs')
    else:
        # 开发时：从当前工作目录找
        return os.path.join(os.getcwd(), 'logs')


def clean_old_logs(log_dir: str = 'logs', days: int = 30) -> int:
    """
    清理过期的日志文件
    
    Args:
        log_dir: 日志目录
        days: 保留天数，默认30天
    
    Returns:
        int: 删除的文件数量
    """
    actual_log_dir = get_logs_dir() if log_dir == 'logs' else log_dir
    
    if not os.path.exists(actual_log_dir):
        return 0
    
    cutoff_date = datetime.now() - timedelta(days=days)
    deleted_count = 0
    
    pattern = os.path.join(actual_log_dir, '*.log')
    for log_file in glob.glob(pattern):
        try:
            file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
            if file_time < cutoff_date:
                os.remove(log_file)
                deleted_count += 1
        except Exception:
            pass
    
    return deleted_count


def setup_logging(log_dir: str = 'logs', level: int = logging.DEBUG) -> None:
    """
    配置全局日志系统
    
    Args:
        log_dir: 日志目录，默认为 'logs'
        level: 日志级别，默认为 DEBUG
    """
    actual_log_dir = get_logs_dir() if log_dir == 'logs' else log_dir
    os.makedirs(actual_log_dir, exist_ok=True)
    
    log_file = os.path.join(actual_log_dir, f'{datetime.now():%Y%m%d}.log')
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 清除已有处理器（避免重复）
    if root_logger.handlers:
        root_logger.handlers.clear()
    
    # 文件处理器（轮转，5MB，保留3个备份）
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=5*1024*1024, 
        backupCount=3, 
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 统一格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 清理30天前的日志
    clean_old_logs(log_dir, days=30)
    
    # 添加处理器
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logging.getLogger(__name__).info(f"日志系统初始化完成: {log_file}")
