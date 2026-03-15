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
    
    训练两个模型：
    1. DGA模型：仅使用DGA数据
    2. PD融合模型：将四通道PD数据融合后训练
    
    注意：DGA和PD是不同的样本集，预测时使用决策级融合策略
    
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
        send_notification("=" * 50)
        send_notification("开始训练随机森林模型")
        send_notification("=" * 50)
        send_progress_value(5)
        
        if data_source == 'database':
            from database.db_manager import DatabaseManager
            db_manager = DatabaseManager(db_path=db_path)
            conn = db_manager.get_connection()
            
            # 1. 读取DGA数据
            send_notification("\n[1/2] 读取DGA数据...")
            try:
                dga_query = "SELECT principal_components, fault_type, fault_location FROM fusion_features_dga"
                df_dga = pd.read_sql_query(dga_query, conn)
                if not df_dga.empty:
                    send_notification(f"  DGA数据: {len(df_dga)} 条")
                    logger.info(f"DGA数据: {len(df_dga)} 条")
            except Exception as e:
                logger.warning(f"读取DGA数据失败: {e}")
                df_dga = pd.DataFrame()
            
            # 2. 读取四通道PD数据并融合
            send_notification("\n[2/2] 读取四通道PD数据...")
            pd_channels = ['fusion_features_pd_ch1', 'fusion_features_pd_ch2', 
                          'fusion_features_pd_ch3', 'fusion_features_pd_ch4']
            
            pd_data_by_sample = {}
            
            for ch_table in pd_channels:
                try:
                    ch_query = f"SELECT sample_id, principal_components, fault_type, fault_location FROM {ch_table}"
                    df_ch = pd.read_sql_query(ch_query, conn)
                    
                    if not df_ch.empty:
                        for _, row in df_ch.iterrows():
                            sample_id = row['sample_id']
                            # 提取样本编号（去掉通道前缀）
                            sample_num = sample_id.split('_')[-1]
                            
                            if sample_num not in pd_data_by_sample:
                                pd_data_by_sample[sample_num] = {
                                    'pcs': [],
                                    'fault_type': row['fault_type'],
                                    'fault_location': row['fault_location']
                                }
                            
                            import json
                            pc_data = json.loads(str(row['principal_components']))
                            pd_data_by_sample[sample_num]['pcs'].append(pc_data)
                        
                        logger.info(f"从 {ch_table} 读取数据")
                except Exception as e:
                    logger.warning(f"读取 {ch_table} 失败: {e}")
            
            # 融合四通道PD数据
            pd_fused_data = []
            for sample_num, data in pd_data_by_sample.items():
                if len(data['pcs']) == 4:  # 确保有四个通道的数据
                    # 将四个通道的PCA结果拼接
                    fused_pc = np.concatenate(data['pcs'])
                    pd_fused_data.append({
                        'principal_components': fused_pc,
                        'fault_type': data['fault_type'],
                        'fault_location': data['fault_location']
                    })
            
            send_notification(f"  PD融合数据: {len(pd_fused_data)} 条 (四通道融合)")
            logger.info(f"PD融合数据: {len(pd_fused_data)} 条")
            
            conn.close()
            
        else:
            df = pd.read_excel(data_file)
            logger.info(f"从文件读取数据: {data_file}")
            send_notification(f"从文件读取数据: {data_file}")
            df_dga = df
            pd_fused_data = []
        
        send_progress_value(20)
        
        # 存储所有模型结果
        results = {}
        
        # 3. 训练DGA模型
        if not df_dga.empty:
            send_notification("\n" + "=" * 40)
            send_notification("训练DGA模型")
            send_notification("=" * 40)
            dga_result = _train_single_model(
                df_dga, 'DGA', n_estimators, random_state,
                send_notification, send_progress_value, logger
            )
            if dga_result:
                results['DGA'] = dga_result
                send_progress_value(50)
        
        # 4. 训练PD融合模型
        if pd_fused_data:
            send_notification("\n" + "=" * 40)
            send_notification("训练PD融合模型 (四通道融合)")
            send_notification("=" * 40)
            df_pd = pd.DataFrame(pd_fused_data)
            pd_result = _train_single_model(
                df_pd, 'PD_FUSION', n_estimators, random_state,
                send_notification, send_progress_value, logger
            )
            if pd_result:
                results['PD_FUSION'] = pd_result
                send_progress_value(80)
        
        # 5. 汇总结果
        send_notification("\n" + "=" * 50)
        send_notification("模型训练完成汇总")
        send_notification("=" * 50)
        for model_name, result in results.items():
            send_notification(f"  {model_name} 模型准确率: {result['accuracy']:.4f}")
        
        send_notification("\n注意：DGA和PD是不同的样本集")
        send_notification("预测时使用决策级融合策略")
        
        send_progress_value(100)
        
        return {
            'all_models': results,
            'main': results.get('DGA') or results.get('PD_FUSION')
        }
        
    except Exception as e:
        error_msg = f"训练随机森林模型失败: {e}"
        logger.error(error_msg)
        send_notification(error_msg)
        raise


def _train_single_model(df, model_name, n_estimators, random_state, 
                        send_notification, send_progress_value, logger):
    """
    训练单个模型
    
    Args:
        df: 数据DataFrame
        model_name: 模型名称
        n_estimators: 树的数量
        random_state: 随机种子
        send_notification: 通知函数
        send_progress_value: 进度函数
        logger: 日志器
    
    Returns:
        dict: 训练结果
    """
    import json
    import sys
    
    # 解析主成分数据
    X = []
    y = []
    fault_locations = []
    
    for _, row in df.iterrows():
        try:
            pc_data = row['principal_components']
            if isinstance(pc_data, str):
                pc_data = json.loads(pc_data)
            X.append(pc_data)
            y.append(row['fault_type'])
            fault_locations.append(row.get('fault_location', None))
        except Exception as e:
            logger.error(f"解析数据失败: {e}")
            continue
    
    if not X:
        logger.warning(f"{model_name} 没有有效数据")
        return None
    
    X = np.array(X)
    y = np.array(y)
    fault_locations = np.array(fault_locations)
    
    # 检查是否有有效的故障位置数据
    has_location_data = any(loc is not None and str(loc).strip() != '' for loc in fault_locations)
    
    if has_location_data:
        # 准备多输出标签
        valid_indices = [i for i, loc in enumerate(fault_locations) if loc is not None and str(loc).strip() != '']
        X = X[valid_indices]
        y = y[valid_indices]
        fault_locations = fault_locations[valid_indices]
        
        if len(X) == 0:
            logger.warning(f"{model_name} 没有有效的故障位置数据")
            has_location_data = False
        else:
            y_multi = np.column_stack((y, fault_locations))
            
            # 划分训练集和测试集
            X_train, X_test, y_train_multi, y_test_multi = train_test_split(
                X, y_multi, test_size=0.2, random_state=random_state
            )
            
            # 训练多输出模型
            base_model = RandomForestClassifier(
                n_estimators=n_estimators,
                random_state=random_state,
                n_jobs=-1
            )
            rf_model = MultiOutputClassifier(base_model, n_jobs=-1)
            rf_model.fit(X_train, y_train_multi)
            
            # 评估
            y_pred_multi = rf_model.predict(X_test)
            y_test_type = y_test_multi[:, 0]
            y_test_location = y_test_multi[:, 1]
            y_pred_type = y_pred_multi[:, 0]
            y_pred_location = y_pred_multi[:, 1]
            
            accuracy_type = accuracy_score(y_test_type, y_pred_type)
            accuracy_location = accuracy_score(y_test_location, y_pred_location)
            overall_accuracy = (accuracy_type + accuracy_location) / 2
            
            logger.info(f"{model_name} 故障类型准确率: {accuracy_type:.4f}")
            logger.info(f"{model_name} 故障位置准确率: {accuracy_location:.4f}")
            logger.info(f"{model_name} 综合准确率: {overall_accuracy:.4f}")
            
            send_notification(f"{model_name} 故障类型准确率: {accuracy_type:.4f}")
            send_notification(f"{model_name} 故障位置准确率: {accuracy_location:.4f}")
            send_notification(f"{model_name} 综合准确率: {overall_accuracy:.4f}")
            
            # 保存模型
            if hasattr(sys, '_MEIPASS'):
                models_dir = os.path.join(os.path.dirname(sys.executable), 'models')
            else:
                root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                models_dir = os.path.join(root_dir, 'models')
            os.makedirs(models_dir, exist_ok=True)
            
            model_path = os.path.join(models_dir, f'random_forest_{model_name.lower()}_model.pkl')
            joblib.dump(rf_model, model_path)
            logger.info(f"{model_name} 模型已保存: {model_path}")
            
            return {
                'model': rf_model,
                'accuracy': overall_accuracy,
                'accuracy_type': accuracy_type,
                'accuracy_location': accuracy_location,
                'model_path': model_path,
                'is_multi_output': True
            }
    
    if not has_location_data:
        # 训练单输出模型
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=random_state
        )
        
        rf_model = RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=-1
        )
        rf_model.fit(X_train, y_train)
        
        y_pred = rf_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"{model_name} 故障类型准确率: {accuracy:.4f}")
        send_notification(f"{model_name} 故障类型准确率: {accuracy:.4f}")
        
        # 保存模型
        if hasattr(sys, '_MEIPASS'):
            models_dir = os.path.join(os.path.dirname(sys.executable), 'models')
        else:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            models_dir = os.path.join(root_dir, 'models')
        os.makedirs(models_dir, exist_ok=True)
        
        model_path = os.path.join(models_dir, f'random_forest_{model_name.lower()}_model.pkl')
        joblib.dump(rf_model, model_path)
        logger.info(f"{model_name} 模型已保存: {model_path}")
        
        return {
            'model': rf_model,
            'accuracy': accuracy,
            'model_path': model_path,
            'is_multi_output': False
        }
