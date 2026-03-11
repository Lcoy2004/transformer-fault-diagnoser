import pandas as pd
import numpy as np
import os
import logging
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import joblib
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from config import notify
logger = logging.getLogger(__name__)

def train_pca_model(data_source='database', data_file='DGA_data.xlsx', db_path='database/fault_data.db', feature_columns=None, n_components=0.95, progress_callback=None, progress_value_callback=None):
    """
    训练PCA模型并保存
    
    Args:
        data_source (str): 数据来源，可选 'database' 或 'excel'
        data_file (str): 数据文件名，当 data_source 为 'excel' 时使用
        db_path (str): 数据库文件路径，当 data_source 为 'database' 时使用
        feature_columns (list): 特征列名列表，默认使用 ['h2', 'ch4', 'c2h6', 'c2h4', 'c2h2']
        n_components (float or int): PCA 组件数量，默认保留95%方差
        progress_callback (callable): 进度回调函数，用于发送进度通知
        progress_value_callback (callable): 进度值回调函数，用于发送进度百分比
    
    Returns:
        dict: 包含以下键的字典:
            - pca_model: PCA 模型对象，用于 transform 新数据
            - scaler: StandardScaler 对象，用于 inverse_transform
            - n_components: 降维后的主成分数量
            - explained_variance_ratio: 各主成分的方差贡献率列表
            - cumulative_variance: 累计方差贡献率列表
            - pca_path: PCA 模型保存路径
            - scaler_path: 标准化模型保存路径
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
    import sys
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
                'hf_partial_discharge': {
                    'query': "SELECT amplitude, frequency, phase, pulse_count, fault_type, fault_location FROM hf_partial_discharge",
                    'features': ['amplitude', 'frequency', 'phase', 'pulse_count'],
                    'source': 'HF'
                },
                'uhf_partial_discharge': {
                    'query': "SELECT amplitude, frequency, phase, time_difference, fault_type, fault_location FROM uhf_partial_discharge",
                    'features': ['amplitude', 'frequency', 'phase', 'time_difference'],
                    'source': 'UHF'
                }
            }
            
            # 读取所有可用的表数据
            dfs = []
            for table_name, config in table_configs.items():
                try:
                    # 检查表是否存在
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                    if cursor.fetchone():
                        # 表存在，读取数据
                        df_table = pd.read_sql_query(config['query'], conn)
                        if not df_table.empty:
                            df_table['source'] = config['source']
                            dfs.append(df_table)
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
            
            if not dfs:
                error_msg = "没有找到有效的数据表"
                logger.error(error_msg)
                send_notification(error_msg)
                raise ValueError(error_msg)
            
            # 合并所有数据
            df = pd.concat(dfs, ignore_index=True)
            logger.info(f"成功合并所有表数据，形状: {df.shape}")
            send_notification(f"成功合并所有表数据，形状: {df.shape}")
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
    except Exception as e:
        error_msg = f"读取数据失败: {e}"
        logger.error(error_msg)
        send_notification(error_msg)
        raise
    
    # 根据数据来源选择特征列
    if feature_columns is None:
        # 检查数据框的列名，自动选择特征列
        if 'h2' in df.columns and 'ch4' in df.columns:
            # DGA数据
            feature_columns = ['h2', 'ch4', 'c2h6', 'c2h4', 'c2h2']
        elif 'amplitude' in df.columns and 'frequency' in df.columns and 'pulse_count' in df.columns:
            # HF局部放电数据
            feature_columns = ['amplitude', 'frequency', 'phase', 'pulse_count']
        elif 'amplitude' in df.columns and 'frequency' in df.columns and 'time_difference' in df.columns:
            # UHF局部放电数据
            feature_columns = ['amplitude', 'frequency', 'phase', 'time_difference']
        else:
            # 尝试从所有可能的特征列中选择
            possible_features = ['h2', 'ch4', 'c2h6', 'c2h4', 'c2h2', 'amplitude', 'frequency', 'phase', 'pulse_count', 'time_difference']
            feature_columns = [col for col in possible_features if col in df.columns]
            if not feature_columns:
                error_msg = "无法识别数据类型，没有找到有效的特征列"
                logger.error(error_msg)
                send_notification(error_msg)
                raise ValueError(error_msg)
    
    # 提取特征
    try:
        X = df[feature_columns].values
        logger.info(f"提取特征: {feature_columns}")
        send_notification(f"提取特征: {feature_columns}")
        send_progress_value(20)
        logger.info(f"原始数据形状: {X.shape}")
        send_notification(f"原始数据形状: {X.shape}")
    except KeyError as e:
        # 尝试大小写转换
        adjusted_columns = []
        for col in feature_columns:
            if col in df.columns:
                adjusted_columns.append(col)
            elif col.lower() in df.columns:
                adjusted_columns.append(col.lower())
            elif col.upper() in df.columns:
                adjusted_columns.append(col.upper())
            else:
                error_msg = f"列 {col} 不存在于数据中"
                logger.error(error_msg)
                send_notification(error_msg)
                raise
        
        X = df[adjusted_columns].values
        logger.info(f"调整后提取特征: {adjusted_columns}")
        send_notification(f"调整后提取特征: {adjusted_columns}")
        send_progress_value(20)
        logger.info(f"原始数据形状: {X.shape}")
        send_notification(f"原始数据形状: {X.shape}")
    
    # 标准化
    send_notification("开始数据标准化...")
    send_progress_value(30)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    logger.info("数据标准化完成")
    send_notification("数据标准化完成")
    
    # PCA 降维
    send_notification("开始PCA降维...")
    send_progress_value(40)
    pca = PCA(n_components=n_components)
    X_pca = pca.fit_transform(X_scaled)
    logger.info(f"PCA 降维完成，保留 {X_pca.shape[1]} 个主成分")
    send_notification(f"PCA 降维完成，保留 {X_pca.shape[1]} 个主成分")
    send_progress_value(60)
    logger.info(f"方差贡献率: {pca.explained_variance_ratio_}")
    logger.info(f"累计贡献率: {pca.explained_variance_ratio_.cumsum()}")
    send_notification(f"累计方差贡献率: {pca.explained_variance_ratio_.cumsum()[-1]:.4f}")
    
    # 保存模型
    pca_path = os.path.join(models_dir, 'pca_model.pkl')
    scaler_path = os.path.join(models_dir, 'scaler.pkl')
    
    joblib.dump(pca, pca_path)
    joblib.dump(scaler, scaler_path)
    
    logger.info(f"模型已保存到: {models_dir}")
    send_notification(f"模型已保存到: {models_dir}")
    send_progress_value(70)
    logger.info(f"PCA 模型: {pca_path}")
    logger.info(f"标准化模型: {scaler_path}")
    
    # 将PCA降维结果保存到数据库
    try:
        send_notification("将PCA结果保存到数据库...")
        send_progress_value(80)
        db_manager = DatabaseManager(db_path=db_path)
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # 清空 fusion_features 表（每次训练前清空）
        cursor.execute("DELETE FROM fusion_features")
        conn.commit()
        logger.info("已清空 fusion_features 表")
        send_notification("已清空 fusion_features 表")
        
        import json
        
        # 生成模型ID（基于时间戳）
        from datetime import datetime
        model_id = f"PCA_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 从原始数据中获取故障类型和故障位置
        fault_types = df['fault_type'].values if 'fault_type' in df.columns else [None]*len(X_pca)
        fault_locations = df['fault_location'].values if 'fault_location' in df.columns else [None]*len(X_pca)
        
        # 插入融合特征数据
        insert_query = """
        INSERT INTO fusion_features 
        (sample_id, model_id, principal_components, fault_type, fault_location, source_file)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        inserted_count = 0
        total_count = len(X_pca)
        
        for i, (pc_values, fault_type, fault_location) in enumerate(zip(X_pca, fault_types, fault_locations)):
            sample_id = f"PCA_{i+1}"
            
            # 将主成分得分转换为JSON
            pc_json = json.dumps(pc_values.tolist())
            
            params = [
                sample_id, model_id, pc_json, fault_type, fault_location, 'PCA_transform'
            ]
            
            try:
                cursor.execute(insert_query, params)
                inserted_count += 1
                
                # 每插入10%的数据更新一次进度
                if inserted_count % max(1, total_count // 10) == 0:
                    progress = 80 + (inserted_count / total_count) * 15
                    send_progress_value(int(progress))
                    
            except Exception as e:
                error_msg = f"插入第 {i+1} 条PCA结果失败: {e}"
                logger.error(error_msg)
                send_notification(error_msg)
                continue
        
        conn.commit()
        success_msg = f"成功将 {inserted_count} 条PCA结果保存到数据库"
        logger.info(success_msg)
        send_notification(success_msg)
        send_progress_value(95)
        conn.close()
    except Exception as e:
        error_msg = f"保存PCA结果到数据库失败: {e}"
        logger.error(error_msg)
        send_notification(error_msg)
    
    # 返回模型信息
    send_progress_value(100)
    return {
        'pca_model': pca,
        'scaler': scaler,
        'n_components': X_pca.shape[1],
        'explained_variance_ratio': pca.explained_variance_ratio_.tolist(),
        'cumulative_variance': pca.explained_variance_ratio_.cumsum().tolist(),
        'pca_path': pca_path,
        'scaler_path': scaler_path
    }


if __name__ == "__main__":
    # 当直接运行脚本时执行训练
    # 从指定的数据库文件读取数据
    result = train_pca_model(data_source='database')
    logger.info(f"PCA训练完成，保留 {result['n_components']} 个主成分")
    logger.info(f"累计方差贡献率: {result['cumulative_variance'][-1]:.4f}")
    logger.info(f"模型已保存到: {result['pca_path']}")
    print(f"PCA训练完成，保留 {result['n_components']} 个主成分")
    print(f"累计方差贡献率: {result['cumulative_variance'][-1]:.4f}")
    print(f"模型已保存到: {result['pca_path']}")
