"""
随机森林模型训练模块
"""

import logging
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from config import notify
from database.db_manager import DatabaseManager
from config.constants import PCA_TABLE_MAPPING
from config.helpers import ensure_models_dir, ProgressHelper

logger = logging.getLogger(__name__)

VALID_PCA_TABLES = set(PCA_TABLE_MAPPING.values())


def _validate_table_name(table_name: str) -> bool:
    """验证表名是否在白名单中"""
    return table_name in VALID_PCA_TABLES


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
    progress = ProgressHelper(progress_callback, progress_value_callback)
    
    try:
        progress.send("=" * 40)
        progress.send("开始训练随机森林模型")
        progress.send("=" * 40)
        progress.update(5)
        
        if data_source == 'database':
            db_manager = DatabaseManager(db_path=db_path)
            conn = db_manager.get_connection()
            
            try:
                progress.send("\n[1/2] 读取DGA数据...")
                try:
                    dga_query = "SELECT principal_components, fault_type, fault_location FROM fusion_features_dga"
                    df_dga = pd.read_sql_query(dga_query, conn)
                    if not df_dga.empty:
                        progress.send(f"  DGA数据: {len(df_dga)} 条")
                        logger.info(f"DGA数据: {len(df_dga)} 条")
                except Exception as e:
                    logger.warning(f"读取DGA数据失败: {e}")
                    df_dga = pd.DataFrame()
                
                progress.send("\n[2/2] 读取四通道PD数据...")
                pd_channels = [PCA_TABLE_MAPPING[f'PD_CH{i}'] for i in range(1, 5)]
                
                pd_data_by_sample = {}
                
                for ch_table in pd_channels:
                    try:
                        if not _validate_table_name(ch_table):
                            logger.warning(f"无效的表名: {ch_table}")
                            continue
                        
                        cols = ['sample_id', 'principal_components', 'fault_type', 'fault_location']
                        cols_str = ', '.join(cols)
                        ch_query = f"SELECT {cols_str} FROM {ch_table}"
                        df_ch = pd.read_sql_query(ch_query, conn)
                        
                        if not df_ch.empty:
                            for _, row in df_ch.iterrows():
                                sample_id = row['sample_id']
                                if sample_id is None:
                                    continue
                                sample_num = str(sample_id).split('_')[-1]
                                
                                if sample_num not in pd_data_by_sample:
                                    pd_data_by_sample[sample_num] = {
                                        'pcs': [],
                                        'fault_type': row['fault_type'],
                                        'fault_location': row['fault_location']
                                    }
                                
                                pc_data = json.loads(str(row['principal_components']))
                                pd_data_by_sample[sample_num]['pcs'].append(pc_data)
                            
                            logger.info(f"从 {ch_table} 读取数据")
                    except Exception as e:
                        logger.warning(f"读取 {ch_table} 失败: {e}")
                
                pd_fused_data = []
                for sample_num, data in pd_data_by_sample.items():
                    if len(data['pcs']) == 4:
                        fused_pc = np.concatenate(data['pcs'])
                        pd_fused_data.append({
                            'principal_components': fused_pc,
                            'fault_type': data['fault_type'],
                            'fault_location': data['fault_location']
                        })
                
                progress.send(f"  PD融合数据: {len(pd_fused_data)} 条 (四通道融合)")
                logger.info(f"PD融合数据: {len(pd_fused_data)} 条")
            finally:
                conn.close()
            
        else:
            df = pd.read_excel(data_file)
            logger.info(f"从文件读取数据: {data_file}")
            progress.send(f"从文件读取数据: {data_file}")
            df_dga = df
            pd_fused_data = []
        
        progress.update(20)
        
        results = {}
        
        if not df_dga.empty:
            progress.send("\n" + "=" * 40)
            progress.send("训练DGA模型")
            progress.send("=" * 40)
            dga_result = _train_single_model(
                df_dga, 'DGA', n_estimators, random_state, progress, logger
            )
            if dga_result:
                results['DGA'] = dga_result
                progress.update(50)
        
        if pd_fused_data:
            progress.send("\n" + "=" * 40)
            progress.send("训练PD融合模型 (四通道融合)")
            progress.send("=" * 40)
            df_pd = pd.DataFrame(pd_fused_data)
            pd_result = _train_single_model(
                df_pd, 'PD_FUSION', n_estimators, random_state, progress, logger
            )
            if pd_result:
                results['PD_FUSION'] = pd_result
                progress.update(80)
        
        progress.send("\n" + "=" * 40)
        progress.send("模型训练完成汇总")
        progress.send("=" * 40)
        for model_name, result in results.items():
            progress.send(f"  {model_name} 模型准确率: {result['accuracy']:.4f}")
        
        progress.send("\n注意：DGA和PD是不同的样本集")
        progress.send("预测时使用决策级融合策略")
        
        progress.update(100)
        
        return {
            'all_models': results,
            'main': results.get('DGA') or results.get('PD_FUSION')
        }
        
    except Exception as e:
        error_msg = f"训练随机森林模型失败: {e}"
        logger.error(error_msg)
        progress.send(error_msg)
        raise


def _train_single_model(df, model_name, n_estimators, random_state, progress, log):
    """
    训练单个模型
    
    Args:
        df: 数据DataFrame
        model_name: 模型名称
        n_estimators: 树的数量
        random_state: 随机种子
        progress: 进度辅助器
        log: 日志器
    
    Returns:
        dict: 训练结果
    """
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
            log.error(f"解析数据失败: {e}")
            continue
    
    if not X:
        log.warning(f"{model_name} 没有有效数据")
        return None
    
    X = np.array(X)
    y = np.array(y)
    fault_locations = np.array(fault_locations)
    
    has_location_data = any(loc is not None and str(loc).strip() != '' for loc in fault_locations)
    
    models_dir = ensure_models_dir()
    
    if has_location_data:
        valid_indices = [i for i, loc in enumerate(fault_locations) if loc is not None and str(loc).strip() != '']
        X = X[valid_indices]
        y = y[valid_indices]
        fault_locations = fault_locations[valid_indices]
        
        if len(X) == 0:
            log.warning(f"{model_name} 没有有效的故障位置数据")
            has_location_data = False
        else:
            y_multi = np.column_stack((y, fault_locations))
            
            X_train, X_test, y_train_multi, y_test_multi = train_test_split(
                X, y_multi, test_size=0.2, random_state=random_state
            )
            
            base_model = RandomForestClassifier(
                n_estimators=n_estimators,
                random_state=random_state,
                n_jobs=-1
            )
            rf_model = MultiOutputClassifier(base_model, n_jobs=-1)
            rf_model.fit(X_train, y_train_multi)
            
            y_pred_multi = rf_model.predict(X_test)
            y_test_type = y_test_multi[:, 0]  # type: ignore
            y_test_location = y_test_multi[:, 1]  # type: ignore
            y_pred_type = y_pred_multi[:, 0]  # type: ignore
            y_pred_location = y_pred_multi[:, 1]  # type: ignore
            
            accuracy_type = accuracy_score(y_test_type, y_pred_type)
            accuracy_location = accuracy_score(y_test_location, y_pred_location)
            overall_accuracy = (accuracy_type + accuracy_location) / 2
            
            log.info(f"{model_name} 故障类型准确率: {accuracy_type:.4f}")
            log.info(f"{model_name} 故障位置准确率: {accuracy_location:.4f}")
            log.info(f"{model_name} 综合准确率: {overall_accuracy:.4f}")
            
            progress.send(f"{model_name} 故障类型准确率: {accuracy_type:.4f}")
            progress.send(f"{model_name} 故障位置准确率: {accuracy_location:.4f}")
            progress.send(f"{model_name} 综合准确率: {overall_accuracy:.4f}")
            
            model_path = f'{models_dir}/random_forest_{model_name.lower()}_model.pkl'
            joblib.dump(rf_model, model_path)
            log.info(f"{model_name} 模型已保存: {model_path}")
            
            return {
                'model': rf_model,
                'accuracy': overall_accuracy,
                'accuracy_type': accuracy_type,
                'accuracy_location': accuracy_location,
                'model_path': model_path,
                'is_multi_output': True
            }
    
    if not has_location_data:
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
        
        log.info(f"{model_name} 故障类型准确率: {accuracy:.4f}")
        progress.send(f"{model_name} 故障类型准确率: {accuracy:.4f}")
        
        model_path = f'{models_dir}/random_forest_{model_name.lower()}_model.pkl'
        joblib.dump(rf_model, model_path)
        log.info(f"{model_name} 模型已保存: {model_path}")
        
        return {
            'model': rf_model,
            'accuracy': accuracy,
            'model_path': model_path,
            'is_multi_output': False
        }
