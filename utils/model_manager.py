# utils/model_manager.py
"""
模型管理器：负责处理模型训练和预测相关的操作
"""

import logging
from PySide6.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)

class ModelManager:
    """模型管理器"""
    
    def __init__(self, data_processor, ui_manager, thread_manager):
        """
        初始化模型管理器
        
        Args:
            data_processor: 数据处理器
            ui_manager: UI管理器
            thread_manager: 线程管理器
        """
        self.data_processor = data_processor
        self.ui_manager = ui_manager
        self.thread_manager = thread_manager
    
    def train_pca(self):
        """
        训练PCA模型
        """
        # 清空输出
        self.ui_manager.clear_output()
        
        # 开始训练
        worker = self.thread_manager.start_task(self.data_processor.train_pca)
        
        # 连接信号
        worker.progress.connect(self.ui_manager.update_output)
        worker.progress_value.connect(self.ui_manager.update_progress)
        worker.finished.connect(self.on_pca_finished)
        worker.error.connect(self.on_error)
        
        # 启动线程
        worker.start()
    
    def on_pca_finished(self, result):
        """
        PCA训练完成处理
        
        Args:
            result: 训练结果
        """
        self.ui_manager.update_output(f"PCA训练完成，解释方差比: {result['explained_variance_ratio']}")
        self.ui_manager.update_output(f"模型已保存到: {result['pca_path']}")
    
    def train_model(self):
        """
        训练随机森林模型
        """
        # 清空输出
        self.ui_manager.clear_output()
        
        # 开始训练
        worker = self.thread_manager.start_task(self.data_processor.train_model)
        
        # 连接信号
        worker.progress.connect(self.ui_manager.update_output)
        worker.progress_value.connect(self.ui_manager.update_progress)
        worker.finished.connect(self.on_model_finished)
        worker.error.connect(self.on_error)
        
        # 启动线程
        worker.start()
    
    def on_model_finished(self, result):
        """
        模型训练完成处理
        
        Args:
            result: 训练结果
        """
        self.ui_manager.update_output(f"模型训练完成，准确率: {result['accuracy']:.4f}")
        
        # 检查是否有故障类型报告
        if 'fault_type_report' in result:
            self.ui_manager.update_output(f"故障类型准确率: {result['fault_type_report']}")
        
        # 检查是否有故障位置报告
        if 'fault_location_report' in result:
            self.ui_manager.update_output(f"故障位置准确率: {result['fault_location_report']}")
        
        # 显示模型保存路径
        if 'model_path' in result:
            self.ui_manager.update_output(f"模型已保存到: {result['model_path']}")
        
        # 显示模型类型信息
        if result.get('is_multi_output', False):
            self.ui_manager.update_output("模型类型: 多输出模型（故障类型+位置）")
        else:
            self.ui_manager.update_output("模型类型: 单输出模型（仅故障类型）")
    
    def predict(self, input_data):
        """
        预测故障
        
        Args:
            input_data: 输入数据
            
        Returns:
            tuple: (fault_type, fault_location) 故障类型和位置
        """
        try:
            # 开始预测
            fault_type, fault_location = self.data_processor.predict(input_data)
            return fault_type, fault_location
        except Exception as e:
            error_msg = f"预测失败: {str(e)}"
            logger.error(error_msg)
            raise
    
    def on_error(self, error_msg):
        """
        错误处理
        
        Args:
            error_msg: 错误信息
        """
        logger.error(error_msg)