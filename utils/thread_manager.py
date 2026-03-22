"""
线程管理模块
"""

import logging
from typing import Callable, Any, Optional
from PySide6.QtCore import QThread, Signal

logger = logging.getLogger(__name__)


class WorkerThread(QThread):
    """工作线程"""
    
    finished = Signal(object)
    error = Signal(str)
    progress = Signal(str)
    progress_value = Signal(int)
    
    def __init__(self, func: Callable, *args: Any, **kwargs: Any):
        """
        初始化工作线程
        
        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数
        """
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        
        # 注入进度回调
        self.kwargs.setdefault('progress_callback', self._on_progress)
        self.kwargs.setdefault('progress_value_callback', self._on_progress_value)
    
    def run(self) -> None:
        """执行线程任务"""
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            logger.error(f"线程执行失败: {e}")
            self.error.emit(str(e))
    
    def _on_progress(self, message: str) -> None:
        """进度回调"""
        self.progress.emit(message)
    
    def _on_progress_value(self, value: int) -> None:
        """进度值回调"""
        self.progress_value.emit(value)


class ThreadManager:
    """线程管理器"""
    
    def __init__(self):
        self._worker: Optional[WorkerThread] = None
    
    def start(self, func: Callable, *args: Any, **kwargs: Any) -> WorkerThread:
        """
        启动任务
        
        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            WorkerThread: 工作线程实例
        """
        self.stop()
        self._worker = WorkerThread(func, *args, **kwargs)
        return self._worker
    
    def stop(self) -> None:
        """停止当前任务"""
        if self._worker and self._worker.isRunning():
            self._worker.quit()
            if not self._worker.wait(5000):  # 等待5秒
                self._worker.terminate()
                self._worker.wait()
            self._worker = None
    
    @property
    def is_running(self) -> bool:
        """检查是否有任务在运行"""
        return self._worker is not None and self._worker.isRunning()
