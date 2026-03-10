# utils/predictor.py
"""
预测器：负责处理不同类型数据的预测
"""

import logging
import numpy as np
import joblib
import os

logger = logging.getLogger(__name__)

class Predictor:
    """预测器"""
    
    def __init__(self):
        """初始化预测器"""
        self.models = {}
        self.scalers = {}
        self.pcas = {}
        self.multi_output_model = None
        self.single_output_model = None
        self.load_models()
    
    def load_models(self):
        """加载模型"""
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        models_dir = os.path.join(root_dir, 'models')
        
        try:
            # 加载DGA模型
            dga_scaler_path = os.path.join(models_dir, 'scaler.pkl')
            dga_pca_path = os.path.join(models_dir, 'pca_model.pkl')
            
            if all(os.path.exists(path) for path in [dga_scaler_path, dga_pca_path]):
                self.scalers['DGA'] = joblib.load(dga_scaler_path)
                self.pcas['DGA'] = joblib.load(dga_pca_path)
                logger.info("DGA模型加载成功")
            else:
                logger.warning("DGA模型文件不完整")
            
            # 尝试加载多输出模型
            multi_output_model_path = os.path.join(models_dir, 'random_forest_multioutput_model.pkl')
            if os.path.exists(multi_output_model_path):
                self.multi_output_model = joblib.load(multi_output_model_path)
                logger.info("多输出模型加载成功")
            
            # 尝试加载单输出模型
            single_output_model_path = os.path.join(models_dir, 'random_forest_single_output_model.pkl')
            if os.path.exists(single_output_model_path):
                self.single_output_model = joblib.load(single_output_model_path)
                logger.info("单输出模型加载成功")
            
            # 如果没有加载任何模型，发出警告
            if self.multi_output_model is None and self.single_output_model is None:
                logger.warning("没有找到可用的随机森林模型")
            
        except Exception as e:
            logger.error(f"加载模型失败: {e}")
            raise
    
    def predict(self, input_data, data_type='DGA'):
        """
        预测故障（单类型数据）
        
        Args:
            input_data: 输入数据列表
            data_type: 数据类型 ('DGA', 'HF', 'UHF')
        
        Returns:
            tuple: (故障类型, 故障位置)
        """
        try:
            # 检查是否有对应的模型
            if data_type not in self.scalers:
                if data_type in ['HF', 'UHF']:
                    logger.warning(f"没有{data_type}类型的专用模型，将使用DGA模型进行预测（可能不准确）")
                    data_type = 'DGA'
                else:
                    raise ValueError(f"不支持的预测类型: {data_type}")
            
            # 转换输入数据为numpy数组
            X = np.array([input_data])
            
            # 获取对应的模型
            scaler = self.scalers[data_type]
            pca = self.pcas[data_type]
            
            # 检查输入维度是否匹配
            expected_dim = scaler.n_features_in_
            actual_dim = X.shape[1]
            
            if actual_dim != expected_dim:
                if actual_dim < expected_dim:
                    logger.warning(f"输入维度{actual_dim}小于期望维度{expected_dim}，将补零处理")
                    X_padded = np.zeros((1, expected_dim))
                    X_padded[0, :actual_dim] = X[0]
                    X = X_padded
                else:
                    logger.warning(f"输入维度{actual_dim}大于期望维度{expected_dim}，将截断处理")
                    X = X[:, :expected_dim]
            
            # 数据预处理和降维
            X_scaled = scaler.transform(X)
            X_pca = pca.transform(X_scaled)
            
            # 选择合适的模型进行预测
            if self.multi_output_model is not None:
                # 使用多输出模型
                y_pred_multi = self.multi_output_model.predict(X_pca)
                y_pred_multi = np.array(y_pred_multi)
                
                # 分离故障类型和故障位置的预测结果
                y_pred_type = y_pred_multi[:, 0]
                y_pred_location = y_pred_multi[:, 1]
                
                return y_pred_type[0], y_pred_location[0]
            elif self.single_output_model is not None:
                # 使用单输出模型，只预测故障类型
                y_pred = self.single_output_model.predict(X_pca)
                return y_pred[0], None
            else:
                raise ValueError("没有可用的预测模型")
            
        except Exception as e:
            logger.error(f"预测失败: {e}")
            raise
    
    def predict_multi(self, input_data_dict):
        """
        多类型数据融合预测
        
        Args:
            input_data_dict: 输入数据字典，格式为 {data_type: [values]}
                            例如: {'DGA': [33.0, 29.0, 9.0, 12.0, 0.0], 
                                   'HF': [1.2, 100.0, 30.0, 5.0]}
        
        Returns:
            dict: 预测结果字典，包含各类型预测结果和融合预测结果
                  格式: {
                      'DGA': (fault_type, fault_location),
                      'HF': (fault_type, fault_location),
                      'fusion': (fault_type, fault_location, confidence)
                  }
        """
        try:
            if not input_data_dict:
                raise ValueError("输入数据为空")
            
            results = {}
            predictions = []
            
            # 对每种数据类型进行预测
            for data_type, input_data in input_data_dict.items():
                try:
                    fault_type, fault_location = self.predict(input_data, data_type)
                    results[data_type] = (fault_type, fault_location)
                    
                    # 只添加有效的预测结果
                    if fault_type is not None:
                        predictions.append({
                            'type': data_type,
                            'fault_type': fault_type,
                            'fault_location': fault_location
                        })
                    logger.info(f"{data_type} 预测结果: 故障类型={fault_type}, 故障位置={fault_location}")
                except Exception as e:
                    logger.error(f"{data_type} 预测失败: {e}")
                    results[data_type] = None
            
            # 融合预测结果
            if len(predictions) > 1:
                fusion_result = self._fuse_predictions(predictions)
                results['fusion'] = fusion_result
                logger.info(f"融合预测结果: 故障类型={fusion_result[0]}, 故障位置={fusion_result[1]}, 置信度={fusion_result[2]:.2f}")
            elif len(predictions) == 1:
                p = predictions[0]
                results['fusion'] = (p['fault_type'], p['fault_location'], 1.0)
            else:
                raise ValueError("没有有效的预测结果")
            
            return results
            
        except Exception as e:
            logger.error(f"多类型数据融合预测失败: {e}")
            raise
    
    def _fuse_predictions(self, predictions):
        """
        融合多个预测结果
        
        Args:
            predictions: 预测结果列表，每个元素包含 'type', 'fault_type', 'fault_location'
        
        Returns:
            tuple: (融合后的故障类型, 融合后的故障位置, 置信度)
        """
        from collections import Counter
        
        # 统计故障类型
        fault_types = [p['fault_type'] for p in predictions]
        type_counter = Counter(fault_types)
        most_common_type = type_counter.most_common(1)[0]
        fault_type = most_common_type[0]
        type_confidence = most_common_type[1] / len(predictions)
        
        # 统计故障位置（只统计非None的位置）
        fault_locations = [p['fault_location'] for p in predictions if p['fault_location'] is not None]
        
        if fault_locations:
            location_counter = Counter(fault_locations)
            most_common_location = location_counter.most_common(1)[0]
            fault_location = most_common_location[0]
            location_confidence = most_common_location[1] / len(fault_locations)
            
            # 计算总体置信度
            overall_confidence = (type_confidence + location_confidence) / 2
        else:
            # 没有有效的故障位置预测
            fault_location = None
            overall_confidence = type_confidence
        
        logger.info(f"融合统计 - 故障类型: {dict(type_counter)}, 故障位置: {dict(location_counter) if fault_locations else '无'}")
        
        return fault_type, fault_location, overall_confidence
    
    def get_supported_types(self):
        """
        获取支持的数据类型
        
        Returns:
            list: 支持的数据类型列表
        """
        return list(self.scalers.keys())
    
    def has_multi_output_model(self):
        """
        检查是否有多输出模型
        
        Returns:
            bool: 是否有多输出模型
        """
        return self.multi_output_model is not None
    
    def has_single_output_model(self):
        """
        检查是否有单输出模型
        
        Returns:
            bool: 是否有单输出模型
        """
        return self.single_output_model is not None
