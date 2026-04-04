"""
预测管理模块
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from PySide6.QtWidgets import QWidget, QMessageBox

logger = logging.getLogger(__name__)


class PredictManager:
    """预测管理器"""
    
    def __init__(
        self,
        parent: QWidget,
        data_processor,
        input_manager,
        ui_manager,
        thread_manager,
        set_buttons_callback: Callable[[bool], None],
        notify_callback: Callable[[str], None]
    ):
        """
        初始化预测管理器
        
        Args:
            parent: 父窗口
            data_processor: 数据处理器
            input_manager: 输入管理器
            ui_manager: UI管理器
            thread_manager: 线程管理器
            set_buttons_callback: 设置按钮状态的回调函数
            notify_callback: 通知回调函数
        """
        self._parent = parent
        self._data = data_processor
        self._input = input_manager
        self._ui = ui_manager
        self._thread = thread_manager
        self._set_buttons = set_buttons_callback
        self._notify = notify_callback
    
    def start_predict(self):
        """启动预测"""
        self._input.save_current_to_cache()
        
        all_data = self._input.get_all_cached_data()
        
        if not all_data:
            QMessageBox.warning(self._parent, "提示", "请先在输入区域填写数据")
            return
        
        summary = self._input.get_data_summary()
        
        has_dga = 'DGA' in all_data
        has_valid_pd = self._input.has_valid_pd_data()
        
        if not has_dga and not has_valid_pd:
            QMessageBox.warning(
                self._parent, "输入数据无效",
                f"当前输入的数据全为零或未填写。\n\n{summary}"
            )
            return
        
        mode_desc = {
            ('fusion'): "融合诊断模式 (DGA + PD)",
            ('dga_only'): "DGA 单源诊断模式",
            ('pd_only'): "PD 单源诊断模式"
        }
        mode_key = 'fusion' if (has_dga and has_valid_pd) else ('dga_only' if has_dga else 'pd_only')
        
        reply = QMessageBox.question(
            self._parent, "确认诊断",
            f"即将进行故障诊断\n\n"
            f"诊断模式: {mode_desc.get(mode_key, '未知')}\n\n"
            f"{summary}\n\n"
            f"是否开始诊断？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        self._set_buttons(False)
        self._ui.clear_output()
        self._ui.update_output(f"[{mode_desc.get(mode_key, '未知')}]")
        self._ui.update_output("=" * 50)
        self._ui.update_progress(0)
        
        worker = self._thread.start(self._do_predict, all_data)
        worker.progress.connect(self._ui.update_output)
        worker.progress_value.connect(self._ui.update_progress)
        worker.finished.connect(self._on_predict_done)
        worker.error.connect(self._on_predict_error)
        worker.start()
    
    def _do_predict(
        self,
        all_data: Dict[str, List[float]],
        progress_callback=None,
        progress_value_callback=None
    ) -> Dict[str, Any]:
        """
        执行预测（在后台线程中运行）
        
        Args:
            all_data: 所有输入数据
            progress_callback: 进度回调
            progress_value_callback: 进度值回调
            
        Returns:
            预测结果字典
        """
        has_dga = 'DGA' in all_data
        has_valid_pd = self._input.has_valid_pd_data()
        
        result = {'mode': '', 'data': None, 'error': None}
        
        try:
            if has_dga and has_valid_pd:
                result['mode'] = 'fusion'
                result['data'] = self._data.predict_multi(
                    all_data,
                    progress_callback=progress_callback,
                    progress_value_callback=progress_value_callback
                )
            elif has_dga:
                result['mode'] = 'dga_only'
                dga_data = all_data['DGA']
                if progress_value_callback:
                    progress_value_callback(20)
                if progress_callback:
                    progress_callback("正在进行DGA分析...")
                if progress_value_callback:
                    progress_value_callback(60)
                fault_type, fault_location = self._data.predict(dga_data, 'DGA')
                if progress_value_callback:
                    progress_value_callback(100)
                if progress_callback:
                    progress_callback("诊断完成")
                result['data'] = {'fusion': (fault_type, fault_location, 0.9)}
            else:
                result['mode'] = 'pd_only'
                result['data'] = self._data.predict_multi(
                    all_data,
                    progress_callback=progress_callback,
                    progress_value_callback=progress_value_callback
                )
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _on_predict_done(self, result: Dict[str, Any]):
        """预测完成"""
        if result.get('error'):
            self._on_predict_error(result['error'])
            return
        
        self._set_buttons(True)
        
        self._ui.clear_output()
        self._ui.update_output("=" * 50)
        self._ui.update_output("故障诊断结果")
        self._ui.update_output("=" * 50)
        
        mode = result['mode']
        data = result['data']
        
        if mode == 'fusion':
            self._display_fusion_result(data)
        elif mode == 'dga_only':
            self._display_dga_result(data)
        elif mode == 'pd_only':
            self._display_pd_result(data)
        
        self._ui.update_output("\n" + "=" * 50)
        self._ui.update_progress(100)
        self._notify("诊断完成")
    
    def _display_fusion_result(self, data: Dict[str, Any]):
        """显示融合预测结果"""
        self._ui.update_output("\n[融合预测模式] DGA + PD数据")
        
        if 'DGA' in data:
            dga_type, dga_location = data['DGA']
            self._ui.update_output(f"\nDGA预测: {dga_type} / {(dga_location or '未知')}")
        
        if 'PD_FUSION' in data:
            pd_type, pd_location = data['PD_FUSION']
            self._ui.update_output(f"PD预测: {pd_type} / {(pd_location or '未知')}")
        
        if 'fusion' in data:
            fusion_type, fusion_location, confidence = data['fusion']
            self._ui.update_output("\n" + "-" * 40)
            self._ui.update_output(f"综合诊断: {fusion_type}")
            self._ui.update_output(f"故障位置: {fusion_location or '未知'}")
            self._ui.update_output(f"置信度: {confidence:.0%}")
    
    def _display_dga_result(self, data: Dict[str, Any]):
        """显示DGA预测结果"""
        self._ui.update_output("\n[DGA预测模式] 仅DGA数据")

        if 'fusion' in data:
            fusion_type, fusion_location, confidence = data['fusion']
            self._ui.update_output("\n" + "-" * 40)
            self._ui.update_output(f"诊断结果: {fusion_type}")
            self._ui.update_output(f"故障位置: {fusion_location or '未知'}")
            self._ui.update_output(f"置信度: {confidence:.0%}")
    
    def _display_pd_result(self, data: Dict[str, Any]):
        """显示PD预测结果"""
        self._ui.update_output("\n[PD预测模式] 仅PD数据")
        if 'fusion' in data:
            fusion_type, fusion_location, confidence = data['fusion']
            self._ui.update_output("\n" + "-" * 40)
            self._ui.update_output(f"诊断结果: {fusion_type}")
            self._ui.update_output(f"故障位置: {fusion_location or '未知'}")
            self._ui.update_output(f"置信度: {confidence:.0%}")
    
    def _on_predict_error(self, error_msg: str):
        """预测失败"""
        self._set_buttons(True)
        self._ui.update_progress(0)
        logger.error(f"预测失败: {error_msg}")
        
        if "模型未加载" in error_msg or "未找到模型" in error_msg:
            detail = (
                f"{error_msg}\n\n"
                f"请按以下步骤操作：\n"
                f"  1. 先导入训练数据（菜单 → 导入数据）\n"
                f"  2. 点击「PCA降维」进行特征降维\n"
                f"  3. 点击「训练模型」训练随机森林\n"
                f"  4. 完成后即可进行故障诊断"
            )
            QMessageBox.warning(self._parent, "模型未就绪", detail)
        else:
            QMessageBox.warning(self._parent, "诊断失败", f"诊断过程出错:\n{error_msg}")
