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
    """获取日志目录的绝对路径"""
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), 'logs')
    return os.path.join(os.getcwd(), 'logs')


def _clean_old_logs(log_dir: str, days: int = 30) -> int:
    """清理过期的日志文件"""
    if not os.path.exists(log_dir):
        return 0
    
    cutoff_date = datetime.now() - timedelta(days=days)
    deleted_count = 0
    
    for log_file in glob.glob(os.path.join(log_dir, '*.log')):
        try:
            file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
            if file_time < cutoff_date:
                os.remove(log_file)
                deleted_count += 1
        except Exception:
            pass
    
    return deleted_count


def setup_logging(log_dir: str = 'logs', level: int = logging.DEBUG) -> None:
    """配置全局日志系统"""
    actual_log_dir = get_logs_dir() if log_dir == 'logs' else log_dir
    os.makedirs(actual_log_dir, exist_ok=True)
    
    log_file = os.path.join(actual_log_dir, f'{datetime.now():%Y%m%d}.log')
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    if root_logger.handlers:
        root_logger.handlers.clear()
    
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    _clean_old_logs(actual_log_dir, days=30)
    root_logger.addHandler(file_handler)
    
    logging.getLogger(__name__).info(f"日志系统初始化完成: {log_file}")
