"""
模型管理模块
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ModelManager:
    """模型管理器"""
    
    def __init__(self, data_processor, ui_manager, thread_manager):
        """
        初始化模型管理器
        
        Args:
            data_processor: 数据处理器
            ui_manager: UI 管理器
            thread_manager: 线程管理器
        """
        self._data = data_processor
        self._ui = ui_manager
        self._thread = thread_manager
    
    def train_pca(self) -> None:
        """训练 PCA 模型"""
        self._start_training(
            self._data.train_pca,
            self._on_pca_finished,
            "PCA 训练完成"
        )
    
    def train_rf(self) -> None:
        """训练随机森林模型"""
        self._start_training(
            self._data.train_model,
            self._on_rf_finished,
            "随机森林训练完成"
        )
    
    def _start_training(self, train_func, callback, success_msg: str) -> None:
        """
        启动训练任务
        
        Args:
            train_func: 训练函数
            callback: 完成回调
            success_msg: 成功消息
        """
        self._ui.clear_output()
        
        worker = self._thread.start(train_func)
        worker.progress.connect(self._ui.update_output)
        worker.progress_value.connect(self._ui.update_progress)
        worker.finished.connect(callback)
        worker.error.connect(self._on_error)
        worker.start()
    
    def _on_pca_finished(self, result: Dict[str, Any]) -> None:
        """PCA 训练完成处理"""
        self._ui.update_output(f"PCA 训练完成")
        self._ui.update_output(f"解释方差比: {result.get('explained_variance_ratio', 'N/A')}")
        self._ui.update_output(f"模型路径: {result.get('pca_path', 'N/A')}")
    
    def _on_rf_finished(self, result: Dict[str, Any]) -> None:
        """随机森林训练完成处理"""
        self._ui.update_output(f"模型训练完成")
        self._ui.update_output(f"准确率: {result.get('accuracy', 0):.4f}")
        
        if 'fault_type_report' in result:
            self._ui.update_output(f"故障类型准确率: {result['fault_type_report']}")
        if 'fault_location_report' in result:
            self._ui.update_output(f"故障位置准确率: {result['fault_location_report']}")
        
        model_type = "多输出" if result.get('is_multi_output') else "单输出"
        self._ui.update_output(f"模型类型: {model_type}")
        self._ui.update_output(f"模型路径: {result.get('model_path', 'N/A')}")
        
        # 重新加载预测器
        try:
            self._data.reload_predictor()
            self._ui.update_output("预测器已重新加载")
        except Exception as e:
            logger.error(f"重新加载预测器失败: {e}")
    
    def _on_error(self, error_msg: str) -> None:
        """错误处理"""
        logger.error(error_msg)
        self._ui.update_output(f"错误: {error_msg}")
