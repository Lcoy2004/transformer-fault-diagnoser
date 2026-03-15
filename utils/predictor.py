"""
预测器：负责处理不同类型数据的预测

注意：DGA和PD是不同的样本集，使用决策级融合策略：
1. 如果有DGA数据，先用DGA模型预测大类（正常、过热、放电）
2. 如果DGA预测为放电且有PD数据，用PD模型细化放电类型
3. 如果只有PD数据，直接用PD模型预测
"""

import logging
import os
import sys

import numpy as np
import joblib

logger = logging.getLogger(__name__)

class Predictor:
    """预测器"""
    
    def __init__(self):
        """初始化预测器"""
        self.models = {}
        self.scalers = {}
        self.pcas = {}
        self.load_models()
    
    def load_models(self):
        """加载模型"""
        # 获取项目根目录（处理打包环境）
        if hasattr(sys, '_MEIPASS'):
            models_dir = os.path.join(os.path.dirname(sys.executable), 'models')
        else:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            models_dir = os.path.join(root_dir, 'models')
        
        try:
            # 为所有数据类型加载对应的PCA和Scaler模型
            for data_type in ['DGA', 'PD_CH1', 'PD_CH2', 'PD_CH3', 'PD_CH4']:
                type_scaler_path = os.path.join(models_dir, f'scaler_{data_type}.pkl')
                type_pca_path = os.path.join(models_dir, f'pca_{data_type}.pkl')
                
                if all(os.path.exists(path) for path in [type_scaler_path, type_pca_path]):
                    self.scalers[data_type] = joblib.load(type_scaler_path)
                    self.pcas[data_type] = joblib.load(type_pca_path)
                    logger.info(f"[加载] {data_type} PCA模型成功")
            
            # 加载训练好的随机森林模型
            model_files = {
                'DGA': 'random_forest_dga_model.pkl',
                'PD_FUSION': 'random_forest_pd_fusion_model.pkl'
            }
            
            for model_name, model_file in model_files.items():
                model_path = os.path.join(models_dir, model_file)
                if os.path.exists(model_path):
                    self.models[model_name] = joblib.load(model_path)
                    logger.info(f"[加载] {model_name} 随机森林模型成功")
            
            if not self.models:
                logger.warning("[警告] 没有找到可用的随机森林模型")
            
        except Exception as e:
            logger.error(f"[错误] 加载模型失败: {e}")
            raise
    
    def predict_dga(self, input_data):
        """
        使用DGA模型预测
        
        Args:
            input_data: DGA输入数据 [h2, ch4, c2h6, c2h4, c2h2]
        
        Returns:
            tuple: (故障类型, 故障位置)
        """
        return self._predict_single(input_data, 'DGA')
    
    def predict_pd_fusion(self, input_data_dict):
        """
        使用PD融合模型预测
        
        Args:
            input_data_dict: 四通道PD数据字典
                {'PD_CH1': [...], 'PD_CH2': [...], 'PD_CH3': [...], 'PD_CH4': [...]}
        
        Returns:
            tuple: (故障类型, 故障位置)
        """
        fused_data = []
        for ch in ['PD_CH1', 'PD_CH2', 'PD_CH3', 'PD_CH4']:
            if ch in input_data_dict:
                ch_data = input_data_dict[ch]
                if ch in self.pcas:
                    X = np.array([ch_data])
                    scaler = self.scalers[ch]
                    pca = self.pcas[ch]
                    X_scaled = scaler.transform(X)
                    X_pca = pca.transform(X_scaled)
                    fused_data.append(X_pca[0])
        
        if not fused_data:
            raise ValueError("[错误] 没有有效的PD数据")
        
        fused_features = np.concatenate(fused_data)
        
        if 'PD_FUSION' in self.models:
            model = self.models['PD_FUSION']
            X = np.array([fused_features])
            y_pred = model.predict(X)
            
            if hasattr(model, 'estimators_'):
                y_pred = np.array(y_pred)
                return y_pred[0, 0], y_pred[0, 1]
            else:
                return y_pred[0], None
        else:
            raise ValueError("[错误] PD融合模型未加载")
    
    def predict_multi(self, input_data_dict):
        """
        决策级融合预测
        
        融合策略：
        1. 如果有DGA数据，先用DGA模型预测大类（正常、过热、放电）
        2. 如果DGA预测为放电且有PD数据，用PD模型细化放电类型
        3. 如果只有PD数据，直接用PD模型预测
        
        Args:
            input_data_dict: 输入数据字典
                {
                    'DGA': [h2, ch4, c2h6, c2h4, c2h2],
                    'PD_CH1': [...],
                    'PD_CH2': [...],
                    'PD_CH3': [...],
                    'PD_CH4': [...]
                }
        
        Returns:
            dict: 预测结果
        """
        results = {}
        dga_result = None
        pd_result = None
        
        # 1. DGA预测
        if 'DGA' in input_data_dict and 'DGA' in self.models:
            try:
                dga_type, dga_location = self.predict_dga(input_data_dict['DGA'])
                dga_result = (dga_type, dga_location)
                results['DGA'] = dga_result
                logger.info(f"[DGA预测] 故障类型={dga_type}, 故障位置={dga_location}")
            except Exception as e:
                logger.error(f"[DGA预测失败] {e}")
        
        # 2. PD融合预测
        has_pd_data = any(ch in input_data_dict for ch in ['PD_CH1', 'PD_CH2', 'PD_CH3', 'PD_CH4'])
        if has_pd_data and 'PD_FUSION' in self.models:
            try:
                pd_type, pd_location = self.predict_pd_fusion(input_data_dict)
                pd_result = (pd_type, pd_location)
                results['PD_FUSION'] = pd_result
                logger.info(f"[PD融合预测] 故障类型={pd_type}, 故障位置={pd_location}")
            except Exception as e:
                logger.error(f"[PD融合预测失败] {e}")
        
        # 3. 决策级融合
        fusion_type = None
        fusion_location = None
        confidence = 0.0
        
        if dga_result and pd_result:
            dga_type, dga_location = dga_result
            pd_type, pd_location = pd_result
            
            if dga_type == '放电':
                fusion_type = pd_type
                fusion_location = dga_location
                confidence = 0.9
                logger.info("[决策融合] DGA预测为放电，使用PD细化放电类型")
            else:
                fusion_type = dga_type
                fusion_location = dga_location
                confidence = 0.95
                logger.info(f"[决策融合] DGA预测为{dga_type}，直接采纳")
        
        elif dga_result:
            fusion_type, fusion_location = dga_result
            confidence = 0.9
            logger.info("[决策融合] 只有DGA数据，直接使用DGA预测结果")
        
        elif pd_result:
            fusion_type, fusion_location = pd_result
            confidence = 0.85
            logger.info("[决策融合] 只有PD数据，使用PD融合预测结果")
        
        else:
            raise ValueError("[错误] 没有有效的预测结果")
        
        results['fusion'] = (fusion_type, fusion_location, confidence)
        
        return results
    
    def _predict_single(self, input_data, data_type):
        """
        单一数据源预测
        
        Args:
            input_data: 输入数据
            data_type: 数据类型
        
        Returns:
            tuple: (故障类型, 故障位置)
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
                    logger.warning(f"[警告] 输入维度{actual_dim}小于期望维度{expected_dim}，补零处理")
                    X_padded = np.zeros((1, expected_dim))
                    X_padded[0, :actual_dim] = X[0]
                    X = X_padded
                else:
                    logger.warning(f"[警告] 输入维度{actual_dim}大于期望维度{expected_dim}，截断处理")
                    X = X[:, :expected_dim]
            
            X_scaled = scaler.transform(X)
            X_pca = pca.transform(X_scaled)
            
            if data_type in self.models:
                model = self.models[data_type]
                y_pred = model.predict(X_pca)
                
                if hasattr(model, 'estimators_'):
                    y_pred = np.array(y_pred)
                    return y_pred[0, 0], y_pred[0, 1]
                else:
                    return y_pred[0], None
            else:
                raise ValueError(f"[错误] {data_type} 模型未加载")
            
        except Exception as e:
            logger.error(f"[预测失败] {e}")
            raise
    
    def predict(self, input_data, data_type='DGA'):
        """
        预测故障（单类型数据）
        
        Args:
            input_data: 输入数据列表
            data_type: 数据类型 ('DGA', 'PD_CH1', 'PD_CH2', 'PD_CH3', 'PD_CH4')
        
        Returns:
            tuple: (故障类型, 故障位置)
        """
        return self._predict_single(input_data, data_type)
    
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
        return model_name in self.models
