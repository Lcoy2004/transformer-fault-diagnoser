# utils/thread_manager.py
"""
线程管理器：负责处理耗时操作的线程管理
"""

import logging
from PySide6.QtCore import QThread, Signal

logger = logging.getLogger(__name__)

class WorkerThread(QThread):
    """工作线程"""
    # 定义信号
    finished = Signal(object)  # 完成信号，传递结果
    error = Signal(str)        # 错误信号，传递错误信息
    progress = Signal(str)     # 进度信号，传递进度信息
    progress_value = Signal(int)  # 进度值信号，传递进度百分比
    
    def __init__(self, func, *args, **kwargs):
        """
        初始化工作线程
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
        """
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        # 将进度回调函数传递给被执行的函数
        if 'progress_callback' not in self.kwargs:
            self.kwargs['progress_callback'] = self.on_progress
        if 'progress_value_callback' not in self.kwargs:
            self.kwargs['progress_value_callback'] = self.on_progress_value
    
    def run(self):
        """线程运行函数"""
        try:
            # 执行耗时操作
            result = self.func(*self.args, **self.kwargs)
            # 发送完成信号
            self.finished.emit(result)
        except Exception as e:
            # 发送错误信号
            self.error.emit(str(e))
    
    def on_progress(self, message):
        """进度回调函数"""
        # 发送进度信号
        self.progress.emit(message)
    
    def on_progress_value(self, value):
        """进度值回调函数"""
        # 发送进度值信号
        self.progress_value.emit(value)

class ThreadManager:
    """线程管理器"""
    
    def __init__(self):
        """初始化线程管理器"""
        self.worker = None
    
    def start_task(self, func, *args, **kwargs):
        """
        开始任务
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
        
        Returns:
            WorkerThread: 工作线程实例
        """
        # 停止之前的任务
        self.stop_task()
        
        # 创建新的工作线程
        self.worker = WorkerThread(func, *args, **kwargs)
        
        return self.worker
    
    def stop_task(self):
        """停止任务"""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            self.worker = None