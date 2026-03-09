#!/usr/bin/env python3
"""
测试main文件的功能，包括所有操作、通知系统、异步线程和日志
"""

import sys
import os
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QTextEdit
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from config import setup_logging, notify, get_notification
from database.db_manager import DatabaseManager
from utils.train_pca import train_pca_model
from utils.random_forest import train_random_forest

# 配置日志
setup_logging()
logger = logging.getLogger(__name__)

class WorkerThread(QThread):
    """工作线程，用于执行耗时操作"""
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

class MainTestApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main功能测试")
        self.setGeometry(100, 100, 800, 600)
        
        # 数据库管理器实例
        self.db_manager = None
        
        # 创建主布局
        main_layout = QVBoxLayout()
        
        # 创建通知标签
        self.notification_label = QLabel("系统就绪")
        self.notification_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.notification_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 12px;
                font-size: 14px;
                color: #333;
                min-height: 60px;
            }
        """)
        main_layout.addWidget(self.notification_label)
        
        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)
        
        # 创建操作按钮布局
        button_layout = QVBoxLayout()
        
        # 创建操作按钮
        self.btn_import = QPushButton("1. 导入数据")
        self.btn_import.clicked.connect(self.start_import_data)
        button_layout.addWidget(self.btn_import)
        
        self.btn_pca = QPushButton("2. PCA降维")
        self.btn_pca.clicked.connect(self.start_pca_training)
        button_layout.addWidget(self.btn_pca)
        
        self.btn_rf = QPushButton("3. 训练随机森林")
        self.btn_rf.clicked.connect(self.start_rf_training)
        button_layout.addWidget(self.btn_rf)
        
        self.btn_clear = QPushButton("4. 清空通知")
        self.btn_clear.clicked.connect(self.clear_notification)
        button_layout.addWidget(self.btn_clear)
        
        # 添加按钮布局到主布局
        main_layout.addLayout(button_layout)
        
        # 创建日志显示区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-family: Consolas, Monaco, monospace;
                font-size: 12px;
            }
        """)
        main_layout.addWidget(self.log_text)
        
        self.setLayout(main_layout)
        
        # 创建定时器，用于更新通知标签和日志
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(1000)  # 每1秒更新一次
        
        # 记录启动日志
        logger.info("测试应用程序启动")
    
    def update_ui(self):
        """更新UI"""
        # 更新通知标签
        message = get_notification()
        if message:
            self.notification_label.setText(message)
        
        # 可以在这里添加日志更新逻辑
    
    def start_import_data(self):
        """开始导入数据"""
        # 禁用按钮，防止重复点击
        self.disable_all_buttons()
        
        # 重置进度条
        self.progress_bar.setValue(0)
        
        # 记录日志
        logger.info("开始导入数据")
        
        # 创建并启动工作线程
        def import_data_task(progress_callback=None, progress_value_callback=None):
            """导入数据的任务函数"""
            # 初始化数据库（如果还没有）
            if self.db_manager is None:
                if progress_value_callback:
                    progress_value_callback(20)
                self.db_manager = DatabaseManager()
                if progress_value_callback:
                    progress_value_callback(40)
            
            # 导入数据
            if progress_value_callback:
                progress_value_callback(60)
            result = self.db_manager.import_dga_data('DGA_data.xlsx', progress_callback=progress_callback, progress_value_callback=progress_value_callback)
            return result
        
        # 创建线程
        self.worker = WorkerThread(import_data_task)
        self.worker.finished.connect(self.on_import_finished)
        self.worker.error.connect(self.on_worker_error)
        self.worker.progress.connect(self.on_worker_progress)
        self.worker.progress_value.connect(self.on_worker_progress_value)
        self.worker.start()
    
    def on_import_finished(self, result):
        """数据导入完成处理"""
        # 启用按钮
        self.enable_all_buttons()
        
        # 重置进度条
        self.progress_bar.setValue(0)
        
        # 记录日志
        logger.info(f"数据导入完成，成功导入 {result} 条记录")
    
    def start_pca_training(self):
        """开始PCA降维训练"""
        # 禁用按钮，防止重复点击
        self.disable_all_buttons()
        
        # 重置进度条
        self.progress_bar.setValue(0)
        
        # 记录日志
        logger.info("开始PCA降维训练")
        
        # 创建并启动工作线程
        def pca_task(progress_callback=None, progress_value_callback=None):
            """PCA降维的任务函数"""
            # 训练PCA模型
            result = train_pca_model(progress_callback=progress_callback, progress_value_callback=progress_value_callback)
            return result
        
        # 创建线程
        self.worker = WorkerThread(pca_task)
        self.worker.finished.connect(self.on_pca_finished)
        self.worker.error.connect(self.on_worker_error)
        self.worker.progress.connect(self.on_worker_progress)
        self.worker.progress_value.connect(self.on_worker_progress_value)
        self.worker.start()
    
    def on_pca_finished(self, result):
        """PCA降维完成处理"""
        # 启用按钮
        self.enable_all_buttons()
        
        # 重置进度条
        self.progress_bar.setValue(0)
        
        # 记录日志
        logger.info("PCA降维训练完成")
    
    def start_rf_training(self):
        """开始随机森林训练"""
        # 禁用按钮，防止重复点击
        self.disable_all_buttons()
        
        # 重置进度条
        self.progress_bar.setValue(0)
        
        # 记录日志
        logger.info("开始训练随机森林模型")
        
        # 创建并启动工作线程
        def rf_task(progress_callback=None, progress_value_callback=None):
            """随机森林训练的任务函数"""
            # 训练随机森林模型
            result = train_random_forest(progress_callback=progress_callback, progress_value_callback=progress_value_callback)
            return result
        
        # 创建线程
        self.worker = WorkerThread(rf_task)
        self.worker.finished.connect(self.on_rf_finished)
        self.worker.error.connect(self.on_worker_error)
        self.worker.progress.connect(self.on_worker_progress)
        self.worker.progress_value.connect(self.on_worker_progress_value)
        self.worker.start()
    
    def on_rf_finished(self, result):
        """随机森林训练完成处理"""
        # 启用按钮
        self.enable_all_buttons()
        
        # 重置进度条
        self.progress_bar.setValue(0)
        
        # 记录日志
        logger.info(f"随机森林训练完成，准确率: {result['accuracy']:.4f}")
    
    def clear_notification(self):
        """清空通知"""
        from config import clear_notification
        clear_notification()
        notify("通知已清空")
        logger.info("通知已清空")
    
    def on_worker_error(self, error_msg):
        """工作线程错误处理"""
        # 启用所有按钮
        self.enable_all_buttons()
        
        # 重置进度条
        self.progress_bar.setValue(0)
        
        # 发送错误通知
        notify(f"错误: {error_msg}")
        logger.error(f"错误: {error_msg}")
    
    def on_worker_progress(self, message):
        """工作线程进度更新处理"""
        # 发送通知
        notify(message)
        logger.info(message)
    
    def on_worker_progress_value(self, value):
        """工作线程进度值更新处理"""
        # 更新进度条
        self.progress_bar.setValue(value)
    
    def disable_all_buttons(self):
        """禁用所有按钮"""
        self.btn_import.setEnabled(False)
        self.btn_pca.setEnabled(False)
        self.btn_rf.setEnabled(False)
        self.btn_clear.setEnabled(False)
    
    def enable_all_buttons(self):
        """启用所有按钮"""
        self.btn_import.setEnabled(True)
        self.btn_pca.setEnabled(True)
        self.btn_rf.setEnabled(True)
        self.btn_clear.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainTestApp()
    window.show()
    sys.exit(app.exec())
