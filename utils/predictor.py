"""
预测器：负责处理不同类型数据的预测

注意：DGA和PD是不同的样本集，使用决策级融合策略：
1. 如果有DGA数据，先用DGA模型预测大类（正常、过热、放电）
2. 如果DGA预测为放电且有超声波PD数据，用PD模型细化放电类型
3. 如果只有超声波PD数据，直接用PD模型预测
"""

import logging
import os
import joblib
import numpy as np

from config.constants import PD_CHANNELS
from config.helpers import get_models_dir


class Predictor:
    """预测器"""

    def __init__(self):
        """初始化预测器"""
        self._logger = logging.getLogger(__name__)
        self.models_type = {}
        self.models_location = {}
        self.scalers = {}
        self.pcas = {}
        self.load_models()

    def load_models(self):
        """加载模型 - 支持分离的类型/定位模型"""
        models_dir = get_models_dir()

        try:
            for data_type in ['DGA'] + PD_CHANNELS:
                scaler_path = f'{models_dir}/scaler_{data_type}.pkl'
                pca_path = f'{models_dir}/pca_{data_type}.pkl'

                if os.path.exists(scaler_path) and os.path.exists(pca_path):
                    try:
                        self.scalers[data_type] = joblib.load(scaler_path)
                        self.pcas[data_type] = joblib.load(pca_path)
                        self._logger.info(f"[加载] {data_type} PCA模型成功")
                    except Exception as e:
                        self._logger.error(f"[错误] 加载 {data_type} PCA模型失败: {e}")
                        if data_type in self.scalers:
                            del self.scalers[data_type]
                        if data_type in self.pcas:
                            del self.pcas[data_type]

            for model_name in ['DGA', 'PD_FUSION']:
                type_model_path = f'{models_dir}/random_forest_{model_name.lower()}_type.pkl'
                location_model_path = f'{models_dir}/random_forest_{model_name.lower()}_location.pkl'

                if os.path.exists(type_model_path):
                    try:
                        self.models_type[model_name] = joblib.load(type_model_path)
                        self._logger.info(f"[加载] {model_name} 类型模型成功")

                        if os.path.exists(location_model_path):
                            try:
                                self.models_location[model_name] = joblib.load(location_model_path)
                                self._logger.info(f"[加载] {model_name} 定位模型成功")
                            except Exception as e:
                                self._logger.error(f"[错误] 加载 {model_name} 定位模型失败: {e}")
                        else:
                            self._logger.warning(f"[警告] {model_name} 定位模型不存在")
                    except Exception as e:
                        self._logger.error(f"[错误] 加载 {model_name} 类型模型失败: {e}")
                        if model_name in self.models_type:
                            del self.models_type[model_name]

            if not self.models_type:
                self._logger.warning("[警告] 没有找到可用的随机森林模型")

        except Exception as e:
            self._logger.error(f"[错误] 加载模型失败: {e}")

    def predict_dga(self, input_data):
        """
        使用DGA模型预测

        Args:
            input_data: DGA输入数据 [h2, ch4, c2h6, c2h4, c2h2]

        Returns:
            tuple: (故障类型, 故障定位)
        """
        return self._predict_single(input_data, 'DGA')

    def predict_pd_fusion(self, input_data_dict):
        """
        使用PD融合模型预测

        Args:
            input_data_dict: 四通道超声波PD数据字典
                {'PD_CH1': [...], 'PD_CH2': [...], 'PD_CH3': [...], 'PD_CH4': [...]}

        Returns:
            tuple: (故障类型, 故障定位)
        """
        fused_data = []

        for ch in PD_CHANNELS:
            if ch in input_data_dict and ch in self.pcas:
                ch_data = input_data_dict[ch]
                
                # 验证输入数据维度
                expected_dim = self.scalers[ch].n_features_in_
                actual_dim = len(ch_data) if hasattr(ch_data, '__len__') else 0
                
                if actual_dim != expected_dim:
                    self._logger.warning(f"[警告] {ch} 输入维度{actual_dim}与期望维度{expected_dim}不匹配，跳过该通道")
                    pca = self.pcas[ch]
                    n_components = pca.n_components_
                    fused_data.append(np.zeros(n_components))
                    continue
                
                X = np.array([ch_data])
                scaler = self.scalers[ch]
                pca = self.pcas[ch]
                X_scaled = scaler.transform(X)
                X_pca = pca.transform(X_scaled)
                fused_data.append(X_pca[0])
            elif ch in self.pcas:
                pca = self.pcas[ch]
                n_components = pca.n_components_
                fused_data.append(np.zeros(n_components))
                self._logger.warning(f"[警告] {ch} 数据缺失，使用零填充")

        if not any(np.any(d != 0) for d in fused_data):
            raise ValueError("[错误] 没有有效的超声波PD数据")

        fused_features = np.concatenate(fused_data)

        return self._predict_from_features(fused_features, 'PD_FUSION')

    def _predict_from_features(self, features, model_name):
        """
        从特征向量预测

        Args:
            features: 特征向量
            model_name: 模型名称

        Returns:
            tuple: (故障类型, 故障定位坐标)
        """
        X = np.array([features])

        if model_name in self.models_type:
            fault_type = self.models_type[model_name].predict(X)[0]

            if model_name in self.models_location:
                location_model = self.models_location[model_name]
                coords_pred = location_model.predict(X)[0]

                if isinstance(coords_pred, np.ndarray) and len(coords_pred) == 3:
                    coords_pred = np.nan_to_num(coords_pred, nan=0.0, posinf=1e6, neginf=-1e6)
                    x, y, z = coords_pred
                    fault_location = f"({x:.4f}, {y:.4f}, {z:.4f})"
                elif isinstance(coords_pred, (list, tuple)) and len(coords_pred) >= 3:
                    coords_array = np.array(coords_pred[:3], dtype=float)
                    coords_array = np.nan_to_num(coords_array, nan=0.0, posinf=1e6, neginf=-1e6)
                    x, y, z = coords_array
                    fault_location = f"({x:.4f}, {y:.4f}, {z:.4f})"
                else:
                    fault_location = None
            else:
                fault_location = None

            return fault_type, fault_location

        else:
            raise ValueError(f"[错误] {model_name} 模型未加载")

    def predict_multi(self, input_data_dict, progress_callback=None, progress_value_callback=None):
        """
        决策级融合预测

        融合策略：
        1. 如果有DGA数据，先用DGA模型预测大类（正常、过热、放电）
        2. 如果DGA预测为放电且有超声波PD数据，用PD模型细化放电类型
        3. 如果只有超声波PD数据，直接用PD模型预测

        Args:
            input_data_dict: 输入数据字典
                {
                    'DGA': [h2, ch4, c2h6, c2h4, c2h2],
                    'PD_CH1': [...],
                    'PD_CH2': [...],
                    'PD_CH3': [...],
                    'PD_CH4': [...]
                }
            progress_callback: 进度消息回调
            progress_value_callback: 进度值回调 (0-100)

        Returns:
            dict: 预测结果
        """
        def report_progress(msg, value=None):
            if progress_callback:
                progress_callback(msg)
            if progress_value_callback and value is not None:
                progress_value_callback(value)

        results = {}
        dga_result = None
        pd_result = None

        report_progress("开始故障诊断", 10)

        if 'DGA' in input_data_dict and 'DGA' in self.models_type:
            try:
                report_progress("正在进行DGA数据分析", 30)
                dga_type, dga_location = self.predict_dga(input_data_dict['DGA'])
                dga_result = (dga_type, dga_location)
                results['DGA'] = dga_result
                report_progress(f"DGA分析完成 - {dga_type}", 50)
                self._logger.info(f"[DGA预测] 故障类型={dga_type}, 故障定位={dga_location}")
            except Exception as e:
                self._logger.error(f"[DGA预测失败] {e}")

        has_pd_data = any(ch in input_data_dict for ch in PD_CHANNELS)
        if has_pd_data and 'PD_FUSION' in self.models_type:
            try:
                report_progress("正在进行超声波PD局放数据分析", 60)
                pd_type, pd_location = self.predict_pd_fusion(input_data_dict)
                pd_result = (pd_type, pd_location)
                results['PD_FUSION'] = pd_result
                report_progress(f"超声波PD分析完成 - {pd_type}", 80)
                self._logger.info(f"[PD融合预测] 故障类型={pd_type}, 故障定位={pd_location}")
            except Exception as e:
                self._logger.error(f"[PD融合预测失败] {e}")

        fusion_type = None
        fusion_location = None
        confidence = 0.0

        if dga_result and pd_result:
            dga_type, dga_location = dga_result
            pd_type, pd_location = pd_result

            if dga_type == '放电':
                fusion_type = pd_type
                fusion_location = pd_location
                confidence = 0.9
                self._logger.info("[决策融合] DGA预测为放电，使用超声波PD细化放电类型及定位")
            else:
                fusion_type = dga_type
                fusion_location = dga_location
                confidence = 0.95
                self._logger.info(f"[决策融合] DGA预测为{dga_type}，直接采纳")

        elif dga_result:
            fusion_type, fusion_location = dga_result
            confidence = 0.9
            self._logger.info("[决策融合] 只有DGA数据，直接使用DGA预测结果")

        elif pd_result:
            fusion_type, fusion_location = pd_result
            confidence = 0.85
            self._logger.info("[决策融合] 只有超声波PD数据，使用PD融合预测结果")

        else:
            missing_models = []
            if 'DGA' in input_data_dict and 'DGA' not in self.models_type:
                missing_models.append("DGA模型")
            has_pd_data = any(ch in input_data_dict for ch in PD_CHANNELS)
            if has_pd_data and 'PD_FUSION' not in self.models_type:
                missing_models.append("超声波PD融合模型")

            if missing_models:
                raise ValueError(f"[错误] 以下模型未加载，请先训练: {', '.join(missing_models)}")
            else:
                raise ValueError("[错误] 没有有效的预测结果")

        results['fusion'] = (fusion_type, fusion_location, confidence)
        report_progress("诊断完成", 100)

        return results

    def predict(self, input_data, data_type='DGA'):
        """
        预测故障（单类型数据）

        Args:
            input_data: 输入数据列表
            data_type: 数据类型 ('DGA', 'PD_CH1', 'PD_CH2', 'PD_CH3', 'PD_CH4')

        Returns:
            tuple: (故障类型, 故障定位)
        """
        try:
            if data_type not in self.scalers:
                raise ValueError(f"[错误] {data_type}模型未加载，请先训练模型")

            X = np.array([input_data])

            scaler = self.scalers[data_type]
            pca = self.pcas[data_type]

            expected_dim = scaler.n_features_in_
            actual_dim = X.shape[1]

            if actual_dim != expected_dim:
                if actual_dim < expected_dim:
                    self._logger.warning(f"[警告] 输入维度{actual_dim}小于期望维度{expected_dim}，补零处理")
                    X_padded = np.zeros((1, expected_dim))
                    X_padded[0, :actual_dim] = X[0]
                    X = X_padded
                else:
                    self._logger.warning(f"[警告] 输入维度{actual_dim}大于期望维度{expected_dim}，截断处理")
                    X = X[:, :expected_dim]

            X_scaled = scaler.transform(X)
            X_pca = pca.transform(X_scaled)

            model_name = 'DGA' if data_type == 'DGA' else 'PD_FUSION'

            if model_name not in self.models_type:
                raise ValueError(f"[错误] {model_name} 模型未加载")

            fault_type = self.models_type[model_name].predict(X_pca)[0]
            fault_location = None

            if model_name in self.models_location:
                location_model = self.models_location[model_name]
                coords_pred = location_model.predict(X_pca)[0]
                
                if isinstance(coords_pred, np.ndarray) and len(coords_pred) == 3:
                    coords_pred = np.nan_to_num(coords_pred, nan=0.0, posinf=1e6, neginf=-1e6)
                    x, y, z = coords_pred
                    fault_location = f"({x:.4f}, {y:.4f}, {z:.4f})"
                elif isinstance(coords_pred, (list, tuple)) and len(coords_pred) >= 3:
                    coords_array = np.array(coords_pred[:3], dtype=float)
                    coords_array = np.nan_to_num(coords_array, nan=0.0, posinf=1e6, neginf=-1e6)
                    x, y, z = coords_array
                    fault_location = f"({x:.4f}, {y:.4f}, {z:.4f})"

            return fault_type, fault_location

        except Exception as e:
            self._logger.error(f"[预测失败] {e}")
            raise

    def get_supported_types(self):
        """
        获取支持的数据类型

        Returns:
            list: 支持的数据类型列表
        """
        return list(self.scalers.keys())

    def has_model(self, model_name):
        """
        检查是否有指定模型

        Args:
            model_name: 模型名称

        Returns:
            bool: 是否有该模型
        """
        return model_name in self.models_type
