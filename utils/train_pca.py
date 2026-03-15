"""
PCA降维训练模块
"""

import logging
import os
import sys
import json
import joblib
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from config import notify

logger = logging.getLogger(__name__)


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
    # 定义通知函数
    def send_notification(message):
        if progress_callback:
            progress_callback(message)
        else:
            notify(message)
    
    # 定义进度值函数
    def send_progress_value(value):
        if progress_value_callback:
            progress_value_callback(value)
    # 获取项目根目录（处理打包环境）
    if hasattr(sys, '_MEIPASS'):
        # 打包环境
        models_dir = os.path.join(os.path.dirname(sys.executable), 'models')
    else:
        # 开发环境
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        models_dir = os.path.join(root_dir, 'models')
    
    # 确保目录存在
    os.makedirs(models_dir, exist_ok=True)
    
    send_notification("开始PCA降维训练")
    send_progress_value(0)
    # 读取数据
    try:
        if data_source == 'database':
            # 从数据库读取数据
            send_notification("从数据库读取数据...")
            send_progress_value(10)
            db_manager = DatabaseManager(db_path=db_path)
            conn = db_manager.get_connection()
            
            # 定义不同表的查询配置
            table_configs = {
                'oil_chromatography': {
                    'query': "SELECT h2, ch4, c2h6, c2h4, c2h2, fault_type, fault_location FROM oil_chromatography",
                    'features': ['h2', 'ch4', 'c2h6', 'c2h4', 'c2h2'],
                    'source': 'DGA'
                },
                'pd_channel_1': {
                    'query': '''SELECT ch1_band1_energy, ch1_band2_energy, ch1_band3_energy, ch1_band4_energy, 
                              ch1_kurtosis, ch1_main_amp, ch1_main_freq, ch1_mean, 
                              ch1_peak, ch1_pulse_width, ch1_skewness, ch1_var, 
                              fault_type, fault_location FROM pd_channel_1''',
                    'features': ['ch1_band1_energy', 'ch1_band2_energy', 'ch1_band3_energy', 'ch1_band4_energy', 
                                'ch1_kurtosis', 'ch1_main_amp', 'ch1_main_freq', 'ch1_mean', 
                                'ch1_peak', 'ch1_pulse_width', 'ch1_skewness', 'ch1_var'],
                    'source': 'PD_CH1'
                },
                'pd_channel_2': {
                    'query': '''SELECT ch2_band1_energy, ch2_band2_energy, ch2_band3_energy, ch2_band4_energy, 
                              ch2_kurtosis, ch2_main_amp, ch2_main_freq, ch2_mean, 
                              ch2_peak, ch2_pulse_width, ch2_skewness, ch2_var, 
                              fault_type, fault_location FROM pd_channel_2''',
                    'features': ['ch2_band1_energy', 'ch2_band2_energy', 'ch2_band3_energy', 'ch2_band4_energy', 
                                'ch2_kurtosis', 'ch2_main_amp', 'ch2_main_freq', 'ch2_mean', 
                                'ch2_peak', 'ch2_pulse_width', 'ch2_skewness', 'ch2_var'],
                    'source': 'PD_CH2'
                },
                'pd_channel_3': {
                    'query': '''SELECT ch3_band1_energy, ch3_band2_energy, ch3_band3_energy, ch3_band4_energy, 
                              ch3_kurtosis, ch3_main_amp, ch3_main_freq, ch3_mean, 
                              ch3_peak, ch3_pulse_width, ch3_skewness, ch3_var, 
                              fault_type, fault_location FROM pd_channel_3''',
                    'features': ['ch3_band1_energy', 'ch3_band2_energy', 'ch3_band3_energy', 'ch3_band4_energy', 
                                'ch3_kurtosis', 'ch3_main_amp', 'ch3_main_freq', 'ch3_mean', 
                                'ch3_peak', 'ch3_pulse_width', 'ch3_skewness', 'ch3_var'],
                    'source': 'PD_CH3'
                },
                'pd_channel_4': {
                    'query': '''SELECT ch4_band1_energy, ch4_band2_energy, ch4_band3_energy, ch4_band4_energy, 
                              ch4_kurtosis, ch4_main_amp, ch4_main_freq, ch4_mean, 
                              ch4_peak, ch4_pulse_width, ch4_skewness, ch4_var, 
                              fault_type, fault_location FROM pd_channel_4''',
                    'features': ['ch4_band1_energy', 'ch4_band2_energy', 'ch4_band3_energy', 'ch4_band4_energy', 
                                'ch4_kurtosis', 'ch4_main_amp', 'ch4_main_freq', 'ch4_mean', 
                                'ch4_peak', 'ch4_pulse_width', 'ch4_skewness', 'ch4_var'],
                    'source': 'PD_CH4'
                }
            }
            
            # 读取所有可用的表数据
            table_data = {}
            for table_name, config in table_configs.items():
                try:
                    # 检查表是否存在
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                    if cursor.fetchone():
                        # 表存在，读取数据
                        df_table = pd.read_sql_query(config['query'], conn)
                        if not df_table.empty:
                            table_data[table_name] = {
                                'data': df_table,
                                'features': config['features'],
                                'source': config['source']
                            }
                            logger.info(f"成功读取表 {table_name}，形状: {df_table.shape}")
                            send_notification(f"成功读取表 {table_name}，形状: {df_table.shape}")
                        else:
                            logger.warning(f"表 {table_name} 为空")
                            send_notification(f"表 {table_name} 为空")
                    else:
                        logger.warning(f"表 {table_name} 不存在")
                        send_notification(f"表 {table_name} 不存在")
                except Exception as e:
                    logger.error(f"读取表 {table_name} 失败: {e}")
                    send_notification(f"读取表 {table_name} 失败: {e}")
            
            conn.close()
            
            if not table_data:
                error_msg = "没有找到有效的数据表"
                logger.error(error_msg)
                send_notification(error_msg)
                raise ValueError(error_msg)
            
            logger.info(f"数据库路径: {db_path}")
        else:
            # 从Excel文件读取数据
            send_notification(f"从Excel文件读取数据: {data_file}")
            send_progress_value(10)
            data_dir = os.path.join(root_dir, 'data')
            data_path = os.path.join(data_dir, data_file)
            df = pd.read_excel(data_path)
            logger.info(f"成功读取数据文件: {data_path}")
            send_notification(f"成功读取数据文件: {data_file}")
            
            # 处理Excel数据
            table_data = {}
            # 检查是否包含DGA数据
            if 'h2' in df.columns and 'ch4' in df.columns:
                table_data['oil_chromatography'] = {
                    'data': df,
                    'features': ['h2', 'ch4', 'c2h6', 'c2h4', 'c2h2'],
                    'source': 'DGA'
                }
            # 检查是否包含局部放电数据
            for i in range(1, 5):
                if f'ch{i}_band1_energy' in df.columns:
                    table_data[f'pd_channel_{i}'] = {
                        'data': df,
                        'features': [f'ch{i}_band1_energy', f'ch{i}_band2_energy', f'ch{i}_band3_energy', f'ch{i}_band4_energy', 
                                   f'ch{i}_kurtosis', f'ch{i}_main_amp', f'ch{i}_main_freq', f'ch{i}_mean', 
                                   f'ch{i}_peak', f'ch{i}_pulse_width', f'ch{i}_skewness', f'ch{i}_var'],
                        'source': f'PD_CH{i}'
                    }
    except Exception as e:
        error_msg = f"读取数据失败: {e}"
        logger.error(error_msg)
        send_notification(error_msg)
        raise
    
    # 数据融合处理
    send_notification("开始数据融合处理...")
    send_progress_value(20)
    
    # 存储每个数据源的处理结果
    processed_data = []
    all_scalers = {}
    all_pcas = {}
    
    # 对每个数据源单独处理
    for table_name, info in table_data.items():
        df = info['data']
        features = info['features']
        source = info['source']
        
        # 提取特征
        try:
            X = df[features].values
            logger.info(f"处理 {source} 数据，特征: {features}")
            
            # 数据清洗：处理NaN值
            nan_count = np.isnan(X).sum()
            if nan_count > 0:
                logger.warning(f"{source} 数据中包含 {nan_count} 个NaN值，将进行处理")
                X = np.nan_to_num(X, nan=0.0)
            
            # 标准化
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            all_scalers[source] = scaler
            
            # PCA降维
            # 根据数据源类型确定降维后的维度
            if source == 'DGA':
                # DGA数据保留全部5个维度
                n_components = min(5, X_scaled.shape[1])
            else:
                # 局部放电数据保留8-10个维度（根据特征数动态调整）
                n_components = min(10, X_scaled.shape[1])
            
            pca = PCA(n_components=n_components)
            X_pca = pca.fit_transform(X_scaled)
            all_pcas[source] = pca
            
            # 记录方差贡献率
            explained_variance = pca.explained_variance_ratio_
            cumulative_variance = explained_variance.cumsum()
            logger.info(f"{source} PCA维度: {n_components}, 累计方差贡献率: {cumulative_variance[-1]:.4f}")
            
            # 存储处理结果
            processed_data.append({
                'X': X_pca,
                'y': df['fault_type'].values if 'fault_type' in df.columns else np.array([None]*len(X_pca)),
                'locations': df['fault_location'].values if 'fault_location' in df.columns else np.array([None]*len(X_pca)),
                'source': source
            })
            
            logger.info(f"{source} 数据降维完成，形状: {X_pca.shape}")
            send_notification(f"{source} 数据降维完成，形状: {X_pca.shape}")
            
        except KeyError as e:
            error_msg = f"处理 {source} 数据失败: {e}"
            logger.error(error_msg)
            send_notification(error_msg)
            continue
    
    if not processed_data:
        error_msg = "没有有效的数据进行处理"
        logger.error(error_msg)
        send_notification(error_msg)
        raise ValueError(error_msg)
    
    # 注意：DGA和PD是不同的样本集，不应该直接拼接特征
    # 各数据源已独立完成PCA降维，不需要再进行跨数据源的特征融合
    # 预测时使用决策级融合策略
    
    logger.info("=" * 50)
    logger.info("PCA降维处理完成，各数据源独立保存")
    logger.info("注意：DGA和PD是不同的样本集，预测时使用决策级融合")
    logger.info("=" * 50)
    send_notification("PCA降维处理完成")
    send_progress_value(60)
    
    # 汇总各数据源信息
    for data in processed_data:
        source = data['source']
        X = data['X']
        logger.info(f"{source}: {X.shape[0]} 样本, {X.shape[1]} 维")
    
    # 不再保存融合后的主模型（因为融合逻辑不正确）
    # 各数据源使用独立的PCA模型
    
    # 保存各个数据源的单独模型
    for source, source_scaler in all_scalers.items():
        source_scaler_path = os.path.join(models_dir, f'scaler_{source}.pkl')
        joblib.dump(source_scaler, source_scaler_path)
        logger.info(f"保存 {source} 标准化模型: {source_scaler_path}")
    
    for source, source_pca in all_pcas.items():
        source_pca_path = os.path.join(models_dir, f'pca_{source}.pkl')
        joblib.dump(source_pca, source_pca_path)
        logger.info(f"保存 {source} PCA模型: {source_pca_path}")
    
    logger.info(f"模型已保存到: {models_dir}")
    send_notification(f"模型已保存到: {models_dir}")
    send_progress_value(70)
    
    # 将PCA降维结果保存到数据库
    try:
        send_notification("将PCA结果保存到数据库...")
        send_progress_value(80)
        db_manager = DatabaseManager(db_path=db_path)
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        model_id = f"PCA_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 保存各数据源的PCA结果到对应的表
        table_mapping = {
            'DGA': 'fusion_features_dga',
            'PD_CH1': 'fusion_features_pd_ch1',
            'PD_CH2': 'fusion_features_pd_ch2',
            'PD_CH3': 'fusion_features_pd_ch3',
            'PD_CH4': 'fusion_features_pd_ch4'
        }
        
        # 清空各数据源的PCA表
        for table_name in table_mapping.values():
            try:
                cursor.execute(f"DELETE FROM {table_name}")
                logger.info(f"已清空 {table_name} 表")
            except Exception as e:
                logger.warning(f"清空 {table_name} 表失败: {e}")
        
        # 保存各数据源的PCA结果
        for i, data in enumerate(processed_data):
            source = data['source']
            X_source = data['X']
            y_source = data['y']
            locations_source = data['locations']
            
            if source in table_mapping:
                table_name = table_mapping[source]
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
                send_notification(f"{source} 数据已保存: {inserted_count} 条")
        
        conn.commit()
        logger.info("PCA结果已保存到数据库")
        send_notification("PCA结果已保存到数据库")
        send_progress_value(95)
        conn.close()
    except Exception as e:
        error_msg = f"保存PCA结果到数据库失败: {e}"
        logger.error(error_msg)
        send_notification(error_msg)
    
    # 返回模型信息
    send_progress_value(100)
    return {
        'all_scalers': all_scalers,
        'all_pcas': all_pcas,
        'processed_data': processed_data
    }


if __name__ == "__main__":
    result = train_pca_model(data_source='database')
    logger.info("PCA训练完成")
    print("PCA训练完成")
