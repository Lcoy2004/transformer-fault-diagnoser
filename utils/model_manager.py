"""
模型管理模块
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ModelManager:
    """模型管理器"""
    
    def __init__(self, data_processor, ui_manager, thread_manager, set_buttons_callback=None, confirm_callback=None):
        """
        初始化模型管理器
        
        Args:
            data_processor: 数据处理器
            ui_manager: UI 管理器
            thread_manager: 线程管理器
            set_buttons_callback: 设置按钮状态的回调函数
            confirm_callback: 确认对话框回调 (title, message) -> bool
        """
        self._data = data_processor
        self._ui = ui_manager
        self._thread = thread_manager
        self._set_buttons = set_buttons_callback or (lambda enabled: None)
        self._confirm = confirm_callback or (lambda title, msg: True)
    
    def train_pca(self) -> None:
        """训练 PCA 模型"""
        if not self._confirm("确认训练", "即将开始 PCA 降维训练，\n此过程可能需要较长时间。\n\n是否继续？"):
            return
        self._start_training(
            self._data.train_pca,
            self._on_pca_finished
        )
    
    def train_rf(self) -> None:
        """训练随机森林模型"""
        if not self._confirm("确认训练", "即将开始随机森林模型训练，\n此过程可能需要较长时间。\n\n是否继续？"):
            return
        self._start_training(
            self._data.train_model,
            self._on_rf_finished
        )
    
    def _start_training(self, train_func, callback) -> None:
        """
        启动训练任务
        
        Args:
            train_func: 训练函数
            callback: 完成回调
        """
        self._ui.clear_output()
        self._set_buttons(False)
        
        worker = self._thread.start(train_func)
        worker.progress.connect(self._ui.update_output)
        worker.progress_value.connect(self._ui.update_progress)
        worker.finished.connect(self._make_on_finished(callback))
        worker.error.connect(self._on_error)
        worker.start()
    
    def _make_on_finished(self, callback):
        """包装完成回调，确保恢复按钮状态"""
        def wrapper(result):
            self._set_buttons(True)
            callback(result)
        return wrapper
    
    def _on_pca_finished(self, result: Dict[str, Any]) -> None:
        """PCA 训练完成处理"""
        self._ui.update_output("=" * 40)
        self._ui.update_output("PCA 训练完成")
        self._ui.update_output("=" * 40)
        
        all_pcas = result.get('all_pcas', {})
        all_scalers = result.get('all_scalers', {})
        processed_data = result.get('processed_data', [])
        
        for source, pca in all_pcas.items():
            explained_variance = pca.explained_variance_ratio_
            cumulative_variance = explained_variance.cumsum()
            n_components = len(explained_variance)
            
            self._ui.update_output(f"\n【{source} 模型】")
            self._ui.update_output(f"  主成分数量: {n_components}")
            self._ui.update_output(f"  累计方差贡献率: {cumulative_variance[-1]:.4f}")
            self._ui.update_output(f"  各成分方差贡献: {[f'{v:.4f}' for v in explained_variance]}")
        
        self._ui.update_output("\n" + "=" * 40)
        self._ui.update_output(f"共训练 {len(all_pcas)} 个PCA模型")
        self._ui.update_output(f"共处理 {sum(len(d['X']) for d in processed_data)} 个样本")
        self._ui.update_output("=" * 40)
    
    def _on_rf_finished(self, result: Dict[str, Any]) -> None:
        """随机森林训练完成处理"""
        # 检查结果格式
        if 'all_models' in result:
            # 新格式：包含所有模型结果
            all_models = result['all_models']
            
            self._ui.update_output("=" * 40)
            self._ui.update_output("模型训练完成")
            self._ui.update_output("=" * 40)
            
            # 显示各模型准确率
            for model_name, model_result in all_models.items():
                self._ui.update_output(f"\n【{model_name} 模型】")
                self._ui.update_output(f"  准确率: {model_result.get('accuracy', 0):.4f}")
                
                if model_result.get('is_multi_output'):
                    self._ui.update_output(f"  故障类型准确率: {model_result.get('accuracy_type', 0):.4f}")
                    self._ui.update_output(f"  故障位置准确率: {model_result.get('accuracy_location', 0):.4f}")
                
                self._ui.update_output(f"  模型路径: {model_result.get('model_path', 'N/A')}")
            
            # 显示融合策略说明
            self._ui.update_output("\n" + "=" * 40)
            self._ui.update_output("决策级融合策略:")
            self._ui.update_output("1. DGA模型: 预测故障大类")
            self._ui.update_output("2. PD融合模型: 预测放电细类")
            self._ui.update_output("3. 决策融合: DGA放电时用PD细化")
            self._ui.update_output("=" * 40)
        else:
            # 旧格式：只有单个模型结果
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
            self._ui.update_output("\n预测器已重新加载")
        except Exception as e:
            logger.error(f"重新加载预测器失败: {e}")
    
    def _on_error(self, error_msg: str) -> None:
        """错误处理"""
        self._set_buttons(True)
        logger.error(error_msg)
        self._ui.update_output(f"错误: {error_msg}")
