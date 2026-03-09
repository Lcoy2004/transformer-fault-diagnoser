import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logging():
    """
    配置全局日志系统
    功能：
    - 创建 logs 目录
    - 配置文件日志处理器（轮转，5MB，保留3个备份）：eg:20260401.log
    - 配置控制台日志处理器（INFO级别）
    - 设置日志格式：%(asctime)s - %(name)s - %(levelname)s - %(message)s
    - 调用方式：在项目入口（如main.py）中调用setup_logging()，然后使用
    logging.getLogger(__name__)获取日志记录器，最后logging.(对应level)("消息")记录日志
    例如：logger.debug("调试swbug")
    """
    pass
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f'{datetime.now().strftime("%Y%m%d")}.log')

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    ## 配置文件日志处理器
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    ## 配置控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
