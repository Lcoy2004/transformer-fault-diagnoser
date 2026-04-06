"""
随机森林模型训练模块
"""

import logging
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score

from config import notify
from database.db_manager import DatabaseManager
from config.constants import PCA_TABLE_MAPPING
from config.helpers import ensure_models_dir, ProgressHelper

logger = logging.getLogger(__name__)

VALID_PCA_TABLES = set(PCA_TABLE_MAPPING.values())


def _validate_table_name(table_name: str) -> bool:
    """验证表名是否在白名单中"""
    return table_name in VALID_PCA_TABLES


def _parse_location_coord(location_str):
    """
    解析位置坐标字符串为 x, y, z 数值

    Args:
        location_str: 坐标字符串，如 "3.922e-03,2.375e-05,5.000e-06"

    Returns:
        tuple: (x, y, z) 或 None
    """
    if location_str is None or str(location_str).strip() == '':
        return None

    try:
        parts = str(location_str).split(',')
        if len(parts) >= 3:
            coords = []
            for i, part in enumerate(parts[:3]):
                val = float(part.strip())
                if not np.isfinite(val):
                    logger.warning(f"坐标第{i+1}个值非有限数: {val}，替换为0.0")
                    val = 0.0
                elif abs(val) > 1e6:
                    logger.warning(f"坐标第{i+1}个值异常大: {val}，截断到±1e6")
                    val = max(min(val, 1e6), -1e6)
                coords.append(val)
            return tuple(coords)
        return None
    except (ValueError, AttributeError):
        return None


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

            with db_manager._connect() as conn:
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
                total_samples = len(pd_data_by_sample)
                filtered_samples = 0
                for sample_num, data in pd_data_by_sample.items():
                    if len(data['pcs']) == 4:
                        fused_pc = np.concatenate(data['pcs'])
                        pd_fused_data.append({
                            'principal_components': fused_pc,
                            'fault_type': data['fault_type'],
                            'fault_location': data['fault_location']
                        })
                    else:
                        filtered_samples += 1

                if filtered_samples > 0:
                    logger.warning(f"PD数据融合: {total_samples} 个样本中，{filtered_samples} 个因通道数不足被过滤")
                    progress.send(f"  警告: {filtered_samples}/{total_samples} 样本通道不完整，已过滤")

                progress.send(f"  PD融合数据: {len(pd_fused_data)} 条 (四通道融合)")
                logger.info(f"PD融合数据: {len(pd_fused_data)} 条")

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
            is_regression = result.get('is_regression', False)
            if is_regression:
                acc_type = result.get('accuracy_type', 0)
                r2_loc = result.get('r2_location', 0)
                progress.send(f"  {model_name} 类型准确率: {acc_type:.2%} 位置R²: {r2_loc:.2f}")
            else:
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
    训练单个模型 - 故障类型分类 + 故障位置回归
    
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
    fault_coords = []
    
    for _, row in df.iterrows():
        try:
            pc_data = row['principal_components']
            if isinstance(pc_data, str):
                pc_data = json.loads(pc_data)
            X.append(pc_data)
            y.append(row['fault_type'])
            
            coord = _parse_location_coord(row.get('fault_location', None))
            fault_coords.append(coord)
        except Exception as e:
            log.error(f"解析数据失败: {e}")
            continue
    
    if not X:
        log.warning(f"{model_name} 没有有效数据")
        return None
    
    X = np.array(X)
    y = np.array(y)
    
    has_location_data = any(c is not None for c in fault_coords)
    
    models_dir = ensure_models_dir()
    
    enhanced_n_estimators = max(n_estimators, 200)
    
    if has_location_data:
        valid_indices = [i for i, c in enumerate(fault_coords) if c is not None]
        X_loc = X[valid_indices]
        y_loc = y[valid_indices]
        coords_array = np.array([fault_coords[i] for i in valid_indices])
        
        if len(X_loc) == 0:
            log.warning(f"{model_name} 没有有效的故障位置数据")
            has_location_data = False
        elif len(X_loc) < 5:
            log.warning(f"{model_name} 数据量过少({len(X_loc)}个)，无法进行可靠的训练/测试分割")
            has_location_data = False
        else:
            X_train, X_test, y_train, y_test, coords_train, coords_test = train_test_split(
                X_loc, y_loc, coords_array, test_size=0.2, random_state=random_state
            )
            
            rf_type = RandomForestClassifier(
                n_estimators=enhanced_n_estimators,
                random_state=random_state,
                n_jobs=-1,
                class_weight='balanced',
                max_depth=20
            )
            rf_type.fit(X_train, y_train)
            y_pred_type = rf_type.predict(X_test)
            accuracy_type = accuracy_score(y_test, y_pred_type)
            
            rf_location = MultiOutputRegressor(
                RandomForestRegressor(
                    n_estimators=500,
                    random_state=random_state,
                    n_jobs=-1,
                    max_depth=None,
                    min_samples_split=2,
                    min_samples_leaf=1,
                    max_features=1.0
                )
            )
            rf_location.fit(X_train, coords_train)
            coords_pred = rf_location.predict(X_test)
            
            mse = mean_squared_error(coords_test, coords_pred)
            r2 = r2_score(coords_test, coords_pred)
            
            coord_errors = np.sqrt(np.sum((coords_test - coords_pred) ** 2, axis=1))
            mean_error = np.mean(coord_errors)
            max_error = np.max(coord_errors)
            
            overall_score = (accuracy_type + r2) / 2
            
            log.info(f"{model_name} 故障类型准确率: {accuracy_type:.4f}")
            log.info(f"{model_name} 位置回归 R²: {r2:.4f}")
            log.info(f"{model_name} 位置平均误差: {mean_error:.6f} (最大: {max_error:.6f})")
            log.info(f"{model_name} 综合评分: {overall_score:.4f}")
            
            progress.send(f"{model_name} 故障类型准确率: {accuracy_type:.4f}")
            progress.send(f"{model_name} 位置回归 R²: {r2:.4f}")
            progress.send(f"{model_name} 位置平均误差: {mean_error:.6f}")
            
            type_model_path = f'{models_dir}/random_forest_{model_name.lower()}_type.pkl'
            location_model_path = f'{models_dir}/random_forest_{model_name.lower()}_location.pkl'
            joblib.dump(rf_type, type_model_path)
            joblib.dump(rf_location, location_model_path)
            log.info(f"{model_name} 类型模型已保存: {type_model_path}")
            log.info(f"{model_name} 位置回归模型已保存: {location_model_path}")
            
            return {
                'model_type': rf_type,
                'model_location': rf_location,
                'accuracy': overall_score,
                'accuracy_type': accuracy_type,
                'r2_location': r2,
                'mse_location': mse,
                'mean_error': mean_error,
                'model_path': type_model_path,
                'is_multi_output': True,
                'is_regression': True
            }
    
    if not has_location_data:
        if len(X) < 5:
            log.warning(f"{model_name} 数据量过少({len(X)}个)，无法进行可靠的训练/测试分割")
            return None
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=random_state
        )
        
        rf_model = RandomForestClassifier(
            n_estimators=enhanced_n_estimators,
            random_state=random_state,
            n_jobs=-1,
            class_weight='balanced',
            max_depth=20
        )
        rf_model.fit(X_train, y_train)
        
        y_pred = rf_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        log.info(f"{model_name} 故障类型准确率: {accuracy:.4f}")
        progress.send(f"{model_name} 故障类型准确率: {accuracy:.4f}")
        
        model_path = f'{models_dir}/random_forest_{model_name.lower()}_type.pkl'
        joblib.dump(rf_model, model_path)
        log.info(f"{model_name} 模型已保存: {model_path}")
        
        return {
            'model': rf_model,
            'accuracy': accuracy,
            'model_path': model_path,
            'is_multi_output': False,
            'is_regression': False
        }
