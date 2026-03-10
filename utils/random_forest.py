# utils/random_forest.py
"""
随机森林模型训练
"""

import logging
import os
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from config import notify

logger = logging.getLogger(__name__)

def train_random_forest(
    data_source='database',
    data_file=None,
    db_path='database/fault_data.db',
    n_estimators=100,
    random_state=42,
    progress_callback=None,
    progress_value_callback=None
):
    """
    训练随机森林模型
    
    Args:
        data_source: 数据来源 ('database' 或 'file')
        data_file: 数据文件路径（当data_source='file'时使用）
        db_path: 数据库路径（当data_source='database'时使用）
        n_estimators: 随机森林树的数量
        random_state: 随机种子
        progress_callback: 进度回调函数
        progress_value_callback: 进度值回调函数
    
    Returns:
        dict: 训练结果
    """
    def send_notification(message):
        if progress_callback:
            progress_callback(message)
        else:
            notify(message)
    
    def send_progress_value(value):
        if progress_value_callback:
            progress_value_callback(value)
    
    try:
        # 1. 读取数据
        send_notification("开始训练随机森林模型...")
        send_progress_value(10)
        
        if data_source == 'database':
            # 从数据库读取PCA降维后的数据
            from database.db_manager import DatabaseManager
            db_manager = DatabaseManager(db_path=db_path)
            conn = db_manager.get_connection()
            
            query = "SELECT principal_components, fault_type, fault_location FROM fusion_features"
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            logger.info(f"从数据库读取数据，形状: {df.shape}")
            send_notification(f"从数据库读取数据，形状: {df.shape}")
        else:
            # 从文件读取数据
            df = pd.read_excel(data_file)
            logger.info(f"从文件读取数据: {data_file}")
            send_notification(f"从文件读取数据: {data_file}")
        
        send_progress_value(20)
        
        # 2. 解析主成分数据（从JSON字符串转换为数组）
        send_notification("解析主成分数据...")
        send_progress_value(30)
        import json
        X = []
        y = []
        fault_locations = []
        
        for _, row in df.iterrows():
            try:
                # 解析JSON格式的主成分数据
                pc_data = json.loads(str(row['principal_components']))
                X.append(pc_data)
                y.append(row['fault_type'])
                fault_locations.append(row.get('fault_location', None))
            except Exception as e:
                error_msg = f"解析主成分数据失败: {e}"
                logger.error(error_msg)
                send_notification(error_msg)
                continue
        
        X = np.array(X)
        y = np.array(y)
        fault_locations = np.array(fault_locations)
        
        # 检查是否有有效的故障位置数据
        has_location_data = any(loc is not None and str(loc).strip() != '' for loc in fault_locations)
        
        if has_location_data:
            # 准备多输出标签
            # 过滤掉fault_location为None的样本
            valid_indices = [i for i, loc in enumerate(fault_locations) if loc is not None and str(loc).strip() != '']
            X = X[valid_indices]
            y = y[valid_indices]
            fault_locations = fault_locations[valid_indices]
            
            if len(X) == 0:
                error_msg = "没有有效的故障位置数据"
                logger.error(error_msg)
                send_notification(error_msg)
                raise ValueError("无法获取有效的故障位置数据")
            
            # 构建多输出标签矩阵
            y_multi = np.column_stack((y, fault_locations))
            
            logger.info(f"特征形状: {X.shape}")
            send_notification(f"特征形状: {X.shape}")
            send_progress_value(40)
            logger.info(f"多输出标签形状: {y_multi.shape}")
            send_notification(f"多输出标签形状: {y_multi.shape}")
            
            # 3. 划分训练集和测试集
            X_train, X_test, y_train_multi, y_test_multi = train_test_split(
                X, y_multi, test_size=0.2, random_state=random_state
            )
            
            # 确保所有数组都是numpy数组
            X_train = np.array(X_train)
            X_test = np.array(X_test)
            y_train_multi = np.array(y_train_multi)
            y_test_multi = np.array(y_test_multi)
            
            logger.info(f"训练集大小: {X_train.shape[0]}, 测试集大小: {X_test.shape[0]}")
            send_notification(f"训练集大小: {X_train.shape[0]}, 测试集大小: {X_test.shape[0]}")
            send_progress_value(50)
            
            # 4. 训练多输出随机森林模型
            send_notification("开始训练多输出随机森林模型...")
            logger.info("开始训练多输出随机森林模型...")
            base_model = RandomForestClassifier(
                n_estimators=n_estimators,
                random_state=random_state,
                n_jobs=-1
            )
            rf_model = MultiOutputClassifier(base_model, n_jobs=-1)
            rf_model.fit(X_train, y_train_multi)
            logger.info("多输出随机森林模型训练完成")
            send_notification("多输出随机森林模型训练完成")
            send_progress_value(70)
            
            # 5. 模型评估
            send_notification("评估模型性能...")
            send_progress_value(80)
            y_pred_multi = rf_model.predict(X_test)
            
            # 分别评估故障类型和故障位置的预测性能
            y_test_type = y_test_multi[:, 0]
            y_test_location = y_test_multi[:, 1]
            y_pred_type = y_pred_multi[:, 0]
            y_pred_location = y_pred_multi[:, 1]
            
            # 计算准确率
            accuracy_type = accuracy_score(y_test_type, y_pred_type)
            accuracy_location = accuracy_score(y_test_location, y_pred_location)
            overall_accuracy = (accuracy_type + accuracy_location) / 2
            
            # 生成分类报告
            report_type = classification_report(y_test_type, y_pred_type)
            report_location = classification_report(y_test_location, y_pred_location)
            
            logger.info(f"故障类型准确率: {accuracy_type:.4f}")
            logger.info(f"故障位置准确率: {accuracy_location:.4f}")
            logger.info(f"综合准确率: {overall_accuracy:.4f}")
            
            send_notification(f"故障类型准确率: {accuracy_type:.4f}")
            send_notification(f"故障位置准确率: {accuracy_location:.4f}")
            send_notification(f"综合准确率: {overall_accuracy:.4f}")
            
            # 6. 保存模型
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            models_dir = os.path.join(root_dir, 'models')
            os.makedirs(models_dir, exist_ok=True)
            
            model_path = os.path.join(models_dir, 'random_forest_multioutput_model.pkl')
            joblib.dump(rf_model, model_path)
            logger.info(f"多输出模型已保存到: {model_path}")
            send_notification(f"多输出模型生成成功！")
            send_progress_value(90)
            
            # 7. 返回结果
            send_progress_value(100)
            return {
                'model': rf_model,
                'accuracy': overall_accuracy,
                'accuracy_type': accuracy_type,
                'accuracy_location': accuracy_location,
                'report_type': report_type,
                'report_location': report_location,
                'model_path': model_path
            }
        else:
            # 没有故障位置数据，只训练故障类型预测
            logger.info("没有故障位置数据，只训练故障类型预测模型")
            send_notification("没有故障位置数据，只训练故障类型预测模型")
            
            logger.info(f"特征形状: {X.shape}")
            send_notification(f"特征形状: {X.shape}")
            logger.info(f"标签形状: {y.shape}")
            send_notification(f"标签形状: {y.shape}")
            send_progress_value(40)
            
            # 3. 划分训练集和测试集
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=random_state
            )
            
            # 确保所有数组都是numpy数组
            X_train = np.array(X_train)
            X_test = np.array(X_test)
            y_train = np.array(y_train)
            y_test = np.array(y_test)
            
            logger.info(f"训练集大小: {X_train.shape[0]}, 测试集大小: {X_test.shape[0]}")
            send_notification(f"训练集大小: {X_train.shape[0]}, 测试集大小: {X_test.shape[0]}")
            send_progress_value(50)
            
            # 4. 训练单输出随机森林模型
            send_notification("开始训练故障类型预测模型...")
            logger.info("开始训练故障类型预测模型...")
            rf_model = RandomForestClassifier(
                n_estimators=n_estimators,
                random_state=random_state,
                n_jobs=-1
            )
            rf_model.fit(X_train, y_train)
            logger.info("故障类型预测模型训练完成")
            send_notification("故障类型预测模型训练完成")
            send_progress_value(70)
            
            # 5. 模型评估
            send_notification("评估模型性能...")
            send_progress_value(80)
            y_pred = rf_model.predict(X_test)
            
            # 计算准确率
            accuracy = accuracy_score(y_test, y_pred)
            
            # 生成分类报告
            report = classification_report(y_test, y_pred)
            
            logger.info(f"故障类型准确率: {accuracy:.4f}")
            send_notification(f"故障类型准确率: {accuracy:.4f}")
            
            # 6. 保存模型
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            models_dir = os.path.join(root_dir, 'models')
            os.makedirs(models_dir, exist_ok=True)
            
            model_path = os.path.join(models_dir, 'random_forest_single_output_model.pkl')
            joblib.dump(rf_model, model_path)
            logger.info(f"单输出模型已保存到: {model_path}")
            send_notification(f"单输出模型生成成功！")
            send_progress_value(90)
            
            # 7. 返回结果
            send_progress_value(100)
            return {
                'model': rf_model,
                'accuracy': accuracy,
                'report': report,
                'model_path': model_path,
                'has_location': False
            }
            
    except Exception as e:
        error_msg = f"训练随机森林模型失败: {e}"
        logger.error(error_msg)
        send_notification(error_msg)
        raise
