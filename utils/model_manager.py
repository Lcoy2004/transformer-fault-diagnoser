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
        """PCA 训练完成处理 - HTML格式化输出"""
        all_pcas = result.get('all_pcas', {})
        all_scalers = result.get('all_scalers', {})
        processed_data = result.get('processed_data', [])

        # 标题
        html = """
        <div style="background:#e3f2fd;padding:6px 10px;border-radius:4px;margin:4px 0;">
            <b style="color:#1565c0;font-size:12px;">PCA 降维训练完成</b>
        </div>
        """
        self._ui.update_output_html(html)

        # 模型详情表格
        if all_pcas:
            table_html = """
            <table style="border-collapse:collapse;width:100%;font-size:11px;margin:6px 0;">
                <tr style="background:#f5f5f5;">
                    <th style="border:1px solid #ddd;padding:4px 6px;text-align:left;">数据源</th>
                    <th style="border:1px solid #ddd;padding:4px 6px;text-align:center;">原始特征</th>
                    <th style="border:1px solid #ddd;padding:4px 6px;text-align:center;">主成分</th>
                    <th style="border:1px solid #ddd;padding:4px 6px;text-align:center;">降维比例</th>
                    <th style="border:1px solid #ddd;padding:4px 6px;text-align:center;">累计方差</th>
                    <th style="border:1px solid #ddd;padding:4px 6px;text-align:left;">方差分析</th>
                </tr>
            """

            for i, (source, pca) in enumerate(all_pcas.items()):
                explained_variance = pca.explained_variance_ratio_
                cumulative_variance = explained_variance.cumsum()
                n_components = len(explained_variance)
                
                n_features = all_scalers.get(source).n_features_in_ if source in all_scalers else n_components
                reduction_ratio = (1 - n_components / n_features) * 100 if n_features > 0 else 0
                
                is_no_reduction = n_components >= n_features
                reduction_color = "#f57c00" if is_no_reduction else "#2e7d32"
                reduction_text = f"{reduction_ratio:.1f}%" if not is_no_reduction else "未降维"
                
                cum_80_idx = next((j for j, v in enumerate(cumulative_variance) if v >= 0.8), n_components - 1)
                cum_90_idx = next((j for j, v in enumerate(cumulative_variance) if v >= 0.9), n_components - 1)
                cum_95_idx = next((j for j, v in enumerate(cumulative_variance) if v >= 0.95), n_components - 1)
                
                variance_info = f"80%需{cum_80_idx+1}个, 90%需{cum_90_idx+1}个, 95%需{cum_95_idx+1}个"

                bg_color = "#fafafa" if i % 2 == 0 else "#fff"
                table_html += f"""
                <tr style="background:{bg_color};">
                    <td style="border:1px solid #ddd;padding:4px 6px;"><b>{source}</b></td>
                    <td style="border:1px solid #ddd;padding:4px 6px;text-align:center;">{n_features}</td>
                    <td style="border:1px solid #ddd;padding:4px 6px;text-align:center;">{n_components}</td>
                    <td style="border:1px solid #ddd;padding:4px 6px;text-align:center;color:{reduction_color};"><b>{reduction_text}</b></td>
                    <td style="border:1px solid #ddd;padding:4px 6px;text-align:center;color:#2e7d32;"><b>{cumulative_variance[-1]:.2%}</b></td>
                    <td style="border:1px solid #ddd;padding:4px 6px;font-size:9px;color:#666;">{variance_info}</td>
                </tr>
                """

            table_html += "</table>"
            self._ui.update_output_html(table_html)
            
            # 添加警告说明
            warning_html = """
            <div style="background:#fff3e0;padding:6px 10px;border-radius:4px;margin:6px 0;font-size:10px;color:#e65100;">
                <b>说明:</b> 当原始特征数 ≤ 目标主成分数时，无法有效降维，将保留所有特征。<br>
                DGA目标: 5个主成分 | PD目标: 10个主成分
            </div>
            """
            self._ui.update_output_html(warning_html)

        # 统计信息
        total_samples = sum(len(d['X']) for d in processed_data)
        summary_html = f"""
        <div style="background:#f1f8e9;padding:6px 10px;border-radius:4px;margin:6px 0;font-size:11px;">
            <span style="color:#558b2f;">✓</span> 共训练 <b>{len(all_pcas)}</b> 个PCA模型，处理 <b>{total_samples}</b> 个样本
        </div>
        <hr style="border:none;border-top:1px solid #e0e0e0;margin:8px 0;">
        """
        self._ui.update_output_html(summary_html)

    def _on_rf_finished(self, result: Dict[str, Any]) -> None:
        """随机森林训练完成处理 - HTML格式化输出"""
        # 标题
        html = """
        <div style="background:#e8f5e9;padding:6px 10px;border-radius:4px;margin:4px 0;">
            <b style="color:#2e7d32;font-size:12px;">随机森林模型训练完成</b>
        </div>
        """
        self._ui.update_output_html(html)

        if 'all_models' in result:
            all_models = result['all_models']

            # 模型结果表格
            table_html = """
            <table style="border-collapse:collapse;width:100%;font-size:11px;margin:6px 0;">
                <tr style="background:#f5f5f5;">
                    <th style="border:1px solid #ddd;padding:4px 6px;text-align:left;">模型</th>
                    <th style="border:1px solid #ddd;padding:4px 6px;text-align:center;">准确率</th>
                    <th style="border:1px solid #ddd;padding:4px 6px;text-align:left;">详情</th>
                </tr>
            """

            for i, (model_name, model_result) in enumerate(all_models.items()):
                accuracy = model_result.get('accuracy', 0)
                is_multi = model_result.get('is_multi_output', False)
                is_regression = model_result.get('is_regression', False)

                details = []
                if is_multi:
                    acc_type = model_result.get('accuracy_type', 0)
                    if is_regression:
                        r2_loc = model_result.get('r2_location', 0)
                        mean_err = model_result.get('mean_error', 0)
                        details.append(f"类型:{acc_type:.1%} 定位R²:{r2_loc:.2f} 误差:{mean_err:.4f}")
                    else:
                        acc_loc = model_result.get('accuracy_location', 0)
                        details.append(f"类型:{acc_type:.1%} 定位:{acc_loc:.1%}")

                model_path = model_result.get('model_path', 'N/A')
                if model_path != 'N/A':
                    details.append(f"路径: {model_path.split('/')[-1]}")

                bg_color = "#fafafa" if i % 2 == 0 else "#fff"
                acc_color = "#2e7d32" if accuracy >= 0.9 else "#f57c00" if accuracy >= 0.8 else "#c62828"

                table_html += f"""
                <tr style="background:{bg_color};">
                    <td style="border:1px solid #ddd;padding:4px 6px;"><b>{model_name}</b></td>
                    <td style="border:1px solid #ddd;padding:4px 6px;text-align:center;color:{acc_color};"><b>{accuracy:.2%}</b></td>
                    <td style="border:1px solid #ddd;padding:4px 6px;font-size:10px;color:#666;">{'; '.join(details) if details else '-'}</td>
                </tr>
                """

            table_html += "</table>"
            self._ui.update_output_html(table_html)

            # 融合策略说明
            strategy_html = """
            <div style="background:#fff3e0;padding:6px 10px;border-radius:4px;margin:6px 0;font-size:10px;color:#e65100;">
                <b>决策级融合策略:</b><br>
                ① DGA模型识别故障大类（正常/过热/放电）<br>
                ② 若为放电，超声波PD模型细化放电类型<br>
                ③ 智能决策融合，输出最终诊断结论
            </div>
            """
            self._ui.update_output_html(strategy_html)
        else:
            # 旧格式
            accuracy = result.get('accuracy', 0)
            is_multi = result.get('is_multi_output', False)

            html = f"""
            <table style="border-collapse:collapse;width:100%;font-size:11px;margin:6px 0;">
                <tr style="background:#f5f5f5;">
                    <td style="border:1px solid #ddd;padding:4px 6px;">准确率</td>
                    <td style="border:1px solid #ddd;padding:4px 6px;text-align:center;color:#2e7d32;"><b>{accuracy:.2%}</b></td>
                </tr>
                <tr style="background:#fff;">
                    <td style="border:1px solid #ddd;padding:4px 6px;">模型类型</td>
                    <td style="border:1px solid #ddd;padding:4px 6px;text-align:center;">{'多输出' if is_multi else '单输出'}</td>
                </tr>
            </table>
            """
            self._ui.update_output_html(html)

        # 重新加载预测器
        try:
            self._data.reload_predictor()
            reload_html = """
            <div style="background:#e3f2fd;padding:4px 10px;border-radius:4px;margin:6px 0;font-size:11px;color:#1565c0;">
                ✓ 预测器已重新加载
            </div>
            <hr style="border:none;border-top:1px solid #e0e0e0;margin:8px 0;">
            """
            self._ui.update_output_html(reload_html)
        except Exception as e:
            logger.error(f"重新加载预测器失败: {e}")

    def _on_error(self, error_msg: str) -> None:
        """错误处理 - HTML格式化输出"""
        self._set_buttons(True)
        logger.error(error_msg)

        error_html = f"""
        <div style="background:#ffebee;padding:6px 10px;border-radius:4px;margin:4px 0;font-size:11px;">
            <span style="color:#c62828;">✗ 错误:</span> <span style="color:#b71c1c;">{error_msg}</span>
        </div>
        """
        self._ui.update_output_html(error_html)
