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
logger = logging.getLogger(__name__)

def train_pca_model(data_source='database', data_file='DGA_data.xlsx', db_path='database/fault_data.db', feature_columns=None, n_components=0.95):
    """
    训练PCA模型并保存
    
    Args:
        data_source (str): 数据来源，可选 'database' 或 'excel'
        data_file (str): 数据文件名，当 data_source 为 'excel' 时使用
        db_path (str): 数据库文件路径，当 data_source 为 'database' 时使用
        feature_columns (list): 特征列名列表，默认使用 ['h2', 'ch4', 'c2h6', 'c2h4', 'c2h2']
        n_components (float or int): PCA 组件数量，默认保留95%方差
    
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
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(root_dir, 'models')
    
    # 确保目录存在
    os.makedirs(models_dir, exist_ok=True)
    
    # 读取数据
    try:
        if data_source == 'database':
            # 从数据库读取数据
            db_manager = DatabaseManager(db_path=db_path)
            conn = db_manager.get_connection()
            
            # 查询 oil_chromatography 表结构和数据
            table_info_query = "PRAGMA table_info(oil_chromatography)"
            table_info = pd.read_sql_query(table_info_query, conn)
            logger.info(f"oil_chromatography 表结构:\n{table_info}")
            
            # 查询油色谱数据
            query = "SELECT h2, ch4, c2h6, c2h4, c2h2, fault_type, fault_location FROM oil_chromatography"
            df = pd.read_sql_query(query, conn)
            
            conn.close()
            
            logger.info(f"成功从数据库读取数据，形状: {df.shape}")
            logger.info(f"数据库路径: {db_path}")
        else:
            # 从Excel文件读取数据
            data_dir = os.path.join(root_dir, 'data')
            data_path = os.path.join(data_dir, data_file)
            df = pd.read_excel(data_path)
            logger.info(f"成功读取数据文件: {data_path}")
    except Exception as e:
        logger.error(f"读取数据失败: {e}")
        raise
    
    # 默认特征列
    if feature_columns is None:
        # 检查数据框的列名，自动调整大小写
        if 'h2' in df.columns:
            # 数据库来源，列名是小写
            feature_columns = ['h2', 'ch4', 'c2h6', 'c2h4', 'c2h2']
        else:
            # Excel来源，列名可能是大写
            feature_columns = ['H2', 'CH4', 'C2H6', 'C2H4', 'C2H2']
    
    # 提取特征
    try:
        X = df[feature_columns].values
        logger.info(f"提取特征: {feature_columns}")
        logger.info(f"原始数据形状: {X.shape}")
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
                logger.error(f"列 {col} 不存在于数据中")
                raise
        
        X = df[adjusted_columns].values
        logger.info(f"调整后提取特征: {adjusted_columns}")
        logger.info(f"原始数据形状: {X.shape}")
    
    # 标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    logger.info("数据标准化完成")
    
    # PCA 降维
    pca = PCA(n_components=n_components)
    X_pca = pca.fit_transform(X_scaled)
    logger.info(f"PCA 降维完成，保留 {X_pca.shape[1]} 个主成分")
    logger.info(f"方差贡献率: {pca.explained_variance_ratio_}")
    logger.info(f"累计贡献率: {pca.explained_variance_ratio_.cumsum()}")
    
    # 保存模型
    pca_path = os.path.join(models_dir, 'pca_model.pkl')
    scaler_path = os.path.join(models_dir, 'scaler.pkl')
    
    joblib.dump(pca, pca_path)
    joblib.dump(scaler, scaler_path)
    
    logger.info(f"模型已保存到: {models_dir}")
    logger.info(f"PCA 模型: {pca_path}")
    logger.info(f"标准化模型: {scaler_path}")
    
    # 将PCA降维结果保存到数据库
    try:
        db_manager = DatabaseManager(db_path=db_path)
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # 清空 fusion_features 表（每次训练前清空）
        cursor.execute("DELETE FROM fusion_features")
        conn.commit()
        logger.info("已清空 fusion_features 表")
        
        import json
        
        # 生成模型ID（基于时间戳）
        from datetime import datetime
        model_id = f"PCA_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 从原始数据中获取故障类型和故障位置
        fault_types = df.get('fault_type', [None]*len(X_pca))
        fault_locations = df.get('fault_location', [None]*len(X_pca))
        
        # 插入融合特征数据
        insert_query = """
        INSERT INTO fusion_features 
        (sample_id, model_id, principal_components, fault_type, fault_location, source_file)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        inserted_count = 0
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
            except Exception as e:
                logger.error(f"插入第 {i+1} 条PCA结果失败: {e}")
                continue
        
        conn.commit()
        logger.info(f"成功将 {inserted_count} 条PCA结果保存到数据库")
        conn.close()
    except Exception as e:
        logger.error(f"保存PCA结果到数据库失败: {e}")
    
    # 返回模型信息
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
