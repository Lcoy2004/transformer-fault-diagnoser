"""
PCA降维训练模块
"""

import logging
import os
import json
import joblib
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from database.db_manager import DatabaseManager
from config import notify
from config.constants import (
    DGA_FEATURES_DB, PD_CHANNELS, PD_FEATURES, TABLE_CONFIGS, PCA_TABLE_MAPPING
)
from config.helpers import ensure_models_dir, ProgressHelper

logger = logging.getLogger(__name__)

VALID_TABLES = set(TABLE_CONFIGS.keys()) | set(PCA_TABLE_MAPPING.values())


def _validate_table_name(table_name: str) -> bool:
    """验证表名是否在白名单中"""
    return table_name in VALID_TABLES


def train_pca_model(
    data_source='database',
    data_file='DGA_data.xlsx',
    db_path='database/fault_data.db',
    progress_callback=None,
    progress_value_callback=None
):
    """
    训练PCA模型并保存
    
    Args:
        data_source: 数据来源 ('database' 或 'excel')
        data_file: 数据文件名
        db_path: 数据库文件路径
        progress_callback: 进度回调函数
        progress_value_callback: 进度值回调函数
    
    Returns:
        dict: {'all_scalers': {...}, 'all_pcas': {...}, 'processed_data': [...]}
    """
    progress = ProgressHelper(progress_callback, progress_value_callback)
    
    models_dir = ensure_models_dir()
    
    progress.send("开始PCA降维训练")
    progress.update(0)
    
    try:
        if data_source == 'database':
            progress.send("从数据库读取数据...")
            progress.update(10)
            db_manager = DatabaseManager(db_path=db_path)

            table_data = {}

            with db_manager._connect() as conn:
                for table_name, config in TABLE_CONFIGS.items():
                    try:
                        if config.get('is_pca', False):
                            continue
                        if not _validate_table_name(table_name):
                            logger.warning(f"无效的表名: {table_name}")
                            continue

                        cursor = conn.cursor()
                        cursor.execute(
                            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                            (table_name,)
                        )
                        if cursor.fetchone():
                            features = config['features']
                            label_col = config['label_col']
                            location_col = config['location_col']

                            cols_str = ', '.join(features + [label_col, location_col])
                            query = f"SELECT {cols_str} FROM {table_name}"
                            df_table = pd.read_sql_query(query, conn)

                            if not df_table.empty:
                                table_data[table_name] = {
                                    'data': df_table,
                                    'features': features,
                                    'source': config['type']
                                }
                                logger.info(f"成功读取表 {table_name}，形状: {df_table.shape}")
                                progress.send(f"成功读取表 {table_name}，形状: {df_table.shape}")
                    except Exception as e:
                        logger.error(f"读取表 {table_name} 失败: {e}")
                        progress.send(f"读取表 {table_name} 失败: {e}")
            
            if not table_data:
                error_msg = "没有找到有效的数据表"
                logger.error(error_msg)
                progress.send(error_msg)
                raise ValueError(error_msg)
        else:
            progress.send(f"从Excel文件读取数据: {data_file}")
            progress.update(10)
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_path = os.path.join(root_dir, 'data', data_file)
            df = pd.read_excel(data_path)
            
            table_data = {}
            if 'h2' in df.columns and 'ch4' in df.columns:
                table_data['oil_chromatography'] = {
                    'data': df,
                    'features': DGA_FEATURES_DB,
                    'source': 'DGA'
                }
        
        progress.send("开始数据融合处理...")
        progress.update(20)
        
        processed_data = []
        all_scalers = {}
        all_pcas = {}
        
        for table_name, info in table_data.items():
            df = info['data']
            features = info['features']
            source = info['source']
            
            try:
                X = df[features].values
                logger.info(f"处理 {source} 数据，特征: {features}")
                
                nan_count = np.isnan(X).sum()
                if nan_count > 0:
                    logger.warning(f"{source} 数据中包含 {nan_count} 个NaN值，将进行处理")
                    X = np.nan_to_num(X, nan=0.0)
                
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                all_scalers[source] = scaler
                
                if source == 'DGA':
                    n_components = min(5, X_scaled.shape[1])
                else:
                    n_components = min(10, X_scaled.shape[1])
                
                pca = PCA(n_components=n_components)
                X_pca = pca.fit_transform(X_scaled)
                all_pcas[source] = pca
                
                explained_variance = pca.explained_variance_ratio_
                cumulative_variance = explained_variance.cumsum()
                logger.info(f"{source} PCA维度: {n_components}, 累计方差贡献率: {cumulative_variance[-1]:.4f}")
                
                label_col = TABLE_CONFIGS[table_name]['label_col']
                location_col = TABLE_CONFIGS[table_name]['location_col']
                
                processed_data.append({
                    'X': X_pca,
                    'y': df[label_col].values if label_col in df.columns else np.array([None]*len(X_pca)),
                    'locations': df[location_col].values if location_col in df.columns else np.array([None]*len(X_pca)),
                    'source': source
                })
                
                logger.info(f"{source} 数据降维完成，形状: {X_pca.shape}")
                progress.send(f"{source} 数据降维完成，形状: {X_pca.shape}")
                
            except KeyError as e:
                error_msg = f"处理 {source} 数据失败: {e}"
                logger.error(error_msg)
                progress.send(error_msg)
                continue
        
        if not processed_data:
            error_msg = "没有有效的数据进行处理"
            logger.error(error_msg)
            progress.send(error_msg)
            raise ValueError(error_msg)
        
        logger.info("=" * 40)
        logger.info("PCA降维处理完成，各数据源独立保存")
        progress.send("PCA降维处理完成")
        progress.update(60)
        
        for source, source_scaler in all_scalers.items():
            source_scaler_path = os.path.join(models_dir, f'scaler_{source}.pkl')
            joblib.dump(source_scaler, source_scaler_path)
            logger.info(f"保存 {source} 标准化模型: {source_scaler_path}")
        
        for source, source_pca in all_pcas.items():
            source_pca_path = os.path.join(models_dir, f'pca_{source}.pkl')
            joblib.dump(source_pca, source_pca_path)
            logger.info(f"保存 {source} PCA模型: {source_pca_path}")
        
        logger.info(f"模型已保存到: {models_dir}")
        progress.send(f"模型已保存到: {models_dir}")
        progress.update(70)
        
        try:
            progress.send("将PCA结果保存到数据库...")
            progress.update(80)
            db_manager = DatabaseManager(db_path=db_path)

            with db_manager._connect() as conn:
                cursor = conn.cursor()

                model_id = f"PCA_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                for table_name in PCA_TABLE_MAPPING.values():
                    try:
                        if not _validate_table_name(table_name):
                            logger.warning(f"无效的表名: {table_name}")
                            continue
                        cursor.execute(f"DELETE FROM {table_name}")
                        logger.info(f"已清空 {table_name} 表")
                    except Exception as e:
                        logger.warning(f"清空 {table_name} 表失败: {e}")

                for i, data in enumerate(processed_data):
                    source = data['source']
                    X_source = data['X']
                    y_source = data['y']
                    locations_source = data['locations']

                    if source in PCA_TABLE_MAPPING:
                        table_name = PCA_TABLE_MAPPING[source]
                        if not _validate_table_name(table_name):
                            logger.warning(f"无效的表名: {table_name}")
                            continue

                        insert_query = f"""
                        INSERT INTO {table_name}
                        (sample_id, model_id, principal_components, fault_type, fault_location, source_file)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """

                        inserted_count = 0
                        for j, (pc_values, fault_type, fault_location) in enumerate(zip(X_source, y_source, locations_source)):
                            sample_id = f"{source}_{j+1}"
                            pc_json = json.dumps(pc_values.tolist())

                            params = [sample_id, model_id, pc_json, fault_type, fault_location, source]

                            try:
                                cursor.execute(insert_query, params)
                                inserted_count += 1
                            except Exception as e:
                                logger.error(f"插入 {source} 第 {j+1} 条数据失败: {e}")

                        logger.info(f"成功将 {inserted_count} 条 {source} PCA结果保存到 {table_name}")
                        progress.send(f"{source} 数据已保存: {inserted_count} 条")

                logger.info("PCA结果已保存到数据库")
                progress.send("PCA结果已保存到数据库")
                progress.update(95)
        except Exception as e:
            error_msg = f"保存PCA结果到数据库失败: {e}"
            logger.error(error_msg)
            progress.send(error_msg)
        
        progress.update(100)
        return {
            'all_scalers': all_scalers,
            'all_pcas': all_pcas,
            'processed_data': processed_data
        }
        
    except Exception as e:
        error_msg = f"PCA训练失败: {e}"
        logger.error(error_msg)
        progress.send(error_msg)
        raise


