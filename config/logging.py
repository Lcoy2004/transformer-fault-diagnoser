"""
日志配置模块
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logging(log_dir: str = 'logs', level: int = logging.DEBUG) -> None:
    """
    配置全局日志系统
    
    Args:
        log_dir: 日志目录，默认为 'logs'
        level: 日志级别，默认为 DEBUG
    """
    # 创建日志目录
    os.makedirs(log_dir, exist_ok=True)
    
    # 日志文件路径
    log_file = os.path.join(log_dir, f'{datetime.now():%Y%m%d}.log')
    
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
    
    # 添加处理器
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    logging.getLogger(__name__).info(f"日志系统初始化完成: {log_file}")
