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
            'fusion': "融合诊断模式 (DGA + PD)",
            'dga_only': "DGA 单源诊断模式",
            'pd_only': "PD 单源诊断模式"
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

        # 模式标签
        mode_html = f"""
        <div style="background:#e3f2fd;padding:4px 10px;border-radius:4px;margin:4px 0;font-size:11px;">
            <span style="color:#1565c0;">●</span> {mode_desc.get(mode_key, '未知')}
        </div>
        """
        self._ui.update_output_html(mode_html)
        self._ui.update_progress(0)

        worker = self._thread.start(self._do_predict, all_data, has_valid_pd)
        worker.progress.connect(self._ui.update_output)
        worker.progress_value.connect(self._ui.update_progress)
        worker.finished.connect(self._on_predict_done)
        worker.error.connect(self._on_predict_error)
        worker.start()

    def _do_predict(
        self,
        all_data: Dict[str, List[float]],
        has_valid_pd: bool,
        progress_callback=None,
        progress_value_callback=None
    ) -> Dict[str, Any]:
        """
        执行预测（在后台线程中运行）

        Args:
            all_data: 所有输入数据
            has_valid_pd: 是否有有效的PD数据（从UI线程传入，避免线程安全问题）
            progress_callback: 进度回调
            progress_value_callback: 进度值回调

        Returns:
            预测结果字典
        """
        has_dga = 'DGA' in all_data

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
                try:
                    result['data'] = self._data.predict_multi(
                        all_data,
                        progress_callback=progress_callback,
                        progress_value_callback=progress_value_callback
                    )
                except Exception as e:
                    result['error'] = str(e)
        except Exception as e:
            result['error'] = str(e)

        return result

    def _on_predict_done(self, result: Dict[str, Any]):
        """预测完成 - HTML格式化输出"""
        if result.get('error'):
            self._on_predict_error(result['error'])
            return

        self._set_buttons(True)
        self._ui.clear_output()

        # 标题
        title_html = """
        <div style="background:#e8f5e9;padding:6px 10px;border-radius:4px;margin:4px 0;">
            <b style="color:#2e7d32;font-size:12px;">故障诊断结果</b>
        </div>
        """
        self._ui.update_output_html(title_html)

        mode = result['mode']
        data = result['data']

        if mode == 'fusion':
            self._display_fusion_result(data)
        elif mode == 'dga_only':
            self._display_dga_result(data)
        elif mode == 'pd_only':
            self._display_pd_result(data)

        self._ui.update_progress(100)
        self._notify("诊断完成")

    def _display_fusion_result(self, data: Dict[str, Any]):
        """显示融合预测结果 - HTML格式化"""
        # 模式说明
        mode_html = """
        <div style="background:#f3e5f5;padding:4px 10px;border-radius:4px;margin:6px 0;font-size:10px;color:#6a1b9a;">
            [多源融合诊断] DGA油色谱 + 超声波PD局放数据联合分析
        </div>
        """
        self._ui.update_output_html(mode_html)

        # 详细结果表格
        table_html = """
        <table style="border-collapse:collapse;width:100%;font-size:11px;margin:6px 0;">
            <tr style="background:#f5f5f5;">
                <th style="border:1px solid #ddd;padding:4px 6px;text-align:left;">分析类型</th>
                <th style="border:1px solid #ddd;padding:4px 6px;text-align:left;">故障类型</th>
                <th style="border:1px solid #ddd;padding:4px 6px;text-align:left;">故障定位</th>
            </tr>
        """

        if 'DGA' in data:
            dga_data = data['DGA']
            if isinstance(dga_data, (tuple, list)) and len(dga_data) >= 2:
                dga_type, dga_location = dga_data[0], dga_data[1]
            else:
                dga_type, dga_location = str(dga_data), None
            table_html += f"""
            <tr style="background:#fafafa;">
                <td style="border:1px solid #ddd;padding:4px 6px;"><b>DGA分析</b></td>
                <td style="border:1px solid #ddd;padding:4px 6px;">{dga_type}</td>
                <td style="border:1px solid #ddd;padding:4px 6px;">{dga_location or '-'}</td>
            </tr>
            """

        if 'PD_FUSION' in data:
            pd_data = data['PD_FUSION']
            if isinstance(pd_data, (tuple, list)) and len(pd_data) >= 2:
                pd_type, pd_location = pd_data[0], pd_data[1]
            else:
                pd_type, pd_location = str(pd_data), None
            table_html += f"""
            <tr style="background:#fff;">
                <td style="border:1px solid #ddd;padding:4px 6px;"><b>PD分析</b></td>
                <td style="border:1px solid #ddd;padding:4px 6px;">{pd_type}</td>
                <td style="border:1px solid #ddd;padding:4px 6px;">{pd_location or '-'}</td>
            </tr>
            """

        table_html += "</table>"
        self._ui.update_output_html(table_html)

        # 综合诊断结果
        if 'fusion' in data:
            fusion_data = data['fusion']
            if isinstance(fusion_data, (tuple, list)) and len(fusion_data) >= 3:
                fusion_type, fusion_location, confidence = fusion_data[0], fusion_data[1], fusion_data[2]
            else:
                fusion_type, fusion_location, confidence = str(fusion_data), None, 0.0
            conf_color = "#2e7d32" if confidence >= 0.9 else "#f57c00" if confidence >= 0.8 else "#c62828"

            fusion_html = f"""
            <div style="background:#fff8e1;padding:8px 10px;border-radius:4px;margin:8px 0;border-left:3px solid #ffc107;">
                <div style="font-size:11px;color:#666;margin-bottom:4px;">最终诊断结论</div>
                <div style="font-size:13px;color:#e65100;margin-bottom:2px;"><b>{fusion_type}</b></div>
                <div style="font-size:11px;color:#555;">定位: {fusion_location or '未知'}</div>
                <div style="font-size:10px;color:{conf_color};margin-top:4px;">置信度: <b>{confidence:.0%}</b></div>
            </div>
            <hr style="border:none;border-top:1px solid #e0e0e0;margin:8px 0;">
            """
            self._ui.update_output_html(fusion_html)

    def _display_dga_result(self, data: Dict[str, Any]):
        """显示DGA预测结果 - HTML格式化"""
        mode_html = """
        <div style="background:#e3f2fd;padding:4px 10px;border-radius:4px;margin:6px 0;font-size:10px;color:#1565c0;">
            [DGA单源诊断] 仅使用油色谱数据
        </div>
        """
        self._ui.update_output_html(mode_html)

        if 'fusion' in data:
            fusion_data = data['fusion']
            if isinstance(fusion_data, (tuple, list)) and len(fusion_data) >= 3:
                fusion_type, fusion_location, confidence = fusion_data[0], fusion_data[1], fusion_data[2]
            else:
                fusion_type, fusion_location, confidence = str(fusion_data), None, 0.0
            conf_color = "#2e7d32" if confidence >= 0.9 else "#f57c00" if confidence >= 0.8 else "#c62828"

            result_html = f"""
            <div style="background:#fff8e1;padding:8px 10px;border-radius:4px;margin:8px 0;border-left:3px solid #ffc107;">
                <div style="font-size:11px;color:#666;margin-bottom:4px;">DGA诊断结论</div>
                <div style="font-size:13px;color:#e65100;margin-bottom:2px;"><b>{fusion_type}</b></div>
                <div style="font-size:11px;color:#555;">定位: {fusion_location or '未知'}</div>
                <div style="font-size:10px;color:{conf_color};margin-top:4px;">置信度: <b>{confidence:.0%}</b></div>
            </div>
            <hr style="border:none;border-top:1px solid #e0e0e0;margin:8px 0;">
            """
            self._ui.update_output_html(result_html)

    def _display_pd_result(self, data: Dict[str, Any]):
        """显示PD预测结果 - HTML格式化"""
        mode_html = """
        <div style="background:#fce4ec;padding:4px 10px;border-radius:4px;margin:6px 0;font-size:10px;color:#c2185b;">
            [PD单源诊断] 仅使用局部放电超声波数据
        </div>
        """
        self._ui.update_output_html(mode_html)

        if 'fusion' in data:
            fusion_data = data['fusion']
            if isinstance(fusion_data, (tuple, list)) and len(fusion_data) >= 3:
                fusion_type, fusion_location, confidence = fusion_data[0], fusion_data[1], fusion_data[2]
            else:
                fusion_type, fusion_location, confidence = str(fusion_data), None, 0.0
            conf_color = "#2e7d32" if confidence >= 0.9 else "#f57c00" if confidence >= 0.8 else "#c62828"

            result_html = f"""
            <div style="background:#fff8e1;padding:8px 10px;border-radius:4px;margin:8px 0;border-left:3px solid #ffc107;">
                <div style="font-size:11px;color:#666;margin-bottom:4px;">PD诊断结论</div>
                <div style="font-size:13px;color:#e65100;margin-bottom:2px;"><b>{fusion_type}</b></div>
                <div style="font-size:11px;color:#555;">定位: {fusion_location or '未知'}</div>
                <div style="font-size:10px;color:{conf_color};margin-top:4px;">置信度: <b>{confidence:.0%}</b></div>
            </div>
            <hr style="border:none;border-top:1px solid #e0e0e0;margin:8px 0;">
            """
            self._ui.update_output_html(result_html)

    def _on_predict_error(self, error_msg: str):
        """预测失败 - HTML格式化输出"""
        self._set_buttons(True)
        self._ui.update_progress(0)
        logger.error(f"预测失败: {error_msg}")

        # 错误信息
        error_html = f"""
        <div style="background:#ffebee;padding:6px 10px;border-radius:4px;margin:4px 0;font-size:11px;">
            <span style="color:#c62828;">⚠ 诊断中断:</span> <span style="color:#b71c1c;">{error_msg}</span>
        </div>
        """
        self._ui.update_output_html(error_html)

        if "模型未加载" in error_msg or "未找到模型" in error_msg:
            detail = (
                f"{error_msg}\n\n"
                f"请按以下步骤准备模型：\n\n"
                f"  ① 导入训练数据（菜单 → 导入数据）\n"
                f"  ② 执行特征降维（点击「PCA降维」）\n"
                f"  ③ 训练诊断模型（点击「训练模型」）\n"
                f"  ④ 完成后即可开始故障诊断"
            )
            QMessageBox.warning(self._parent, "模型未就绪", detail)
        else:
            QMessageBox.warning(self._parent, "诊断失败", f"诊断过程出错:\n{error_msg}")
