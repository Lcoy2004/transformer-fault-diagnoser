import pandas as pd
import numpy as np
import os
import logging
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# 添加项目根目录到Python路径
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager

logger = logging.getLogger(__name__)

def train_random_forest(db_path='database/fault_data.db', n_estimators=100, random_state=42):
    """
    训练随机森林分类器并保存（同时预测fault_type和fault_location）
    
    Args:
        db_path (str): 数据库文件路径
        n_estimators (int): 随机森林树的数量
        random_state (int): 随机种子
    
    Returns:
        dict: 包含以下键的字典:
            - model: 训练好的随机森林模型
            - accuracy: 模型准确率（综合）
            - fault_type_report: 故障类型分类报告
            - fault_location_report: 故障位置分类报告
            - model_path: 模型保存路径
    """

    # 获取项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(root_dir, 'models')
    
    # 确保目录存在
    os.makedirs(models_dir, exist_ok=True)
    
    try:
        # 1. 从数据库读取PCA降维后的数据
        logger.info("从数据库读取PCA降维后的数据...")
        db_manager = DatabaseManager(db_path=db_path)
        conn = db_manager.get_connection()
        
        # 查询fusion_features表中的降维数据
        query = "SELECT principal_components, fault_type, fault_location FROM fusion_features"
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            logger.error("fusion_features表为空，请先运行train_pca.py生成降维数据")
            raise ValueError("缺少PCA降维数据")
        
        logger.info(f"成功读取PCA降维数据，形状: {df.shape}")
        
        # 2. 解析主成分数据（从JSON字符串转换为数组）
        import json
        X = []
        y = []
        fault_locations = []
        
        for _, row in df.iterrows():
            try:
                # 解析JSON格式的主成分数据
                pc_data = json.loads(row['principal_components'])
                X.append(pc_data)
                y.append(row['fault_type'])
                fault_locations.append(row.get('fault_location', None))
            except Exception as e:
                logger.error(f"解析主成分数据失败: {e}")
                continue
        
        X = np.array(X)
        y = np.array(y)
        fault_locations = np.array(fault_locations)
        
        # 准备多输出标签
        # 过滤掉fault_location为None的样本
        valid_indices = [i for i, loc in enumerate(fault_locations) if loc is not None and str(loc).strip() != '']
        X = X[valid_indices]
        y = y[valid_indices]
        fault_locations = fault_locations[valid_indices]
        
        if len(X) == 0:
            logger.error("没有有效的故障位置数据")
            raise ValueError("无法获取有效的故障位置数据")
        
        # 构建多输出标签矩阵
        y_multi = np.column_stack((y, fault_locations))
        
        logger.info(f"特征形状: {X.shape}")
        logger.info(f"多输出标签形状: {y_multi.shape}")
        
        # 3. 划分训练集和测试集
        X_train, X_test, y_train_multi, y_test_multi = train_test_split(
            X, y_multi, test_size=0.2, random_state=random_state
        )
        logger.info(f"训练集大小: {X_train.shape[0]}, 测试集大小: {X_test.shape[0]}")
        
        # 6. 训练多输出随机森林模型
        logger.info("开始训练多输出随机森林模型...")
        base_model = RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=-1
        )
        rf_model = MultiOutputClassifier(base_model, n_jobs=-1)
        rf_model.fit(X_train, y_train_multi)
        logger.info("多输出随机森林模型训练完成")
        
        # 7. 模型评估
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
        logger.info(f"故障类型分类报告:\n{report_type}")
        logger.info(f"故障位置分类报告:\n{report_location}")
        
        # 8. 保存模型
        model_path = os.path.join(models_dir, 'random_forest_multioutput_model.pkl')
        joblib.dump(rf_model, model_path)
        logger.info(f"多输出模型已保存到: {model_path}")
        
        # 9. 返回结果
        return {
            'model': rf_model,
            'accuracy': overall_accuracy,
            'fault_type_report': report_type,
            'fault_location_report': report_location,
            'model_path': model_path
        }
        
    except Exception as e:
        logger.error(f"训练随机森林模型失败: {e}")
        raise

def predict_with_random_forest(X):
    """
    使用训练好的随机森林模型进行预测（同时预测故障类型和故障位置）
    
    Args:
        X (array): 输入特征数据，形状为 (n_samples, 5)，对应 ['h2', 'ch4', 'c2h6', 'c2h4', 'c2h2']
                   数据来自输入框，而不是数据库
    
    Returns:
        tuple: (故障类型预测结果, 故障位置预测结果)
    """
    # 输入数据示例：
    # X = np.array([[33.0, 29.0, 9.0, 12.0, 0.0]])  # 从输入框获取的H2, CH4, C2H6, C2H4, C2H2数据
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(root_dir, 'models')
    
    try:
        # 加载模型
        scaler_path = os.path.join(models_dir, 'scaler.pkl')
        pca_path = os.path.join(models_dir, 'pca_model.pkl')
        rf_path = os.path.join(models_dir, 'random_forest_multioutput_model.pkl')
        
        if not all(os.path.exists(path) for path in [scaler_path, pca_path, rf_path]):
            logger.error("缺少必要的模型文件")
            raise FileNotFoundError("请先运行train_pca.py和train_random_forest.py")
        
        scaler = joblib.load(scaler_path)
        pca = joblib.load(pca_path)
        rf_model = joblib.load(rf_path)
        
        # 数据预处理和预测
        X_scaled = scaler.transform(X)
        X_pca = pca.transform(X_scaled)
        y_pred_multi = rf_model.predict(X_pca)
        
        # 分离故障类型和故障位置的预测结果
        y_pred_type = y_pred_multi[:, 0]
        y_pred_location = y_pred_multi[:, 1]
        
        return y_pred_type, y_pred_location
        
    except Exception as e:
        logger.error(f"预测失败: {e}")
        raise

if __name__ == "__main__":
    # 当直接运行脚本时执行训练
    result = train_random_forest()
    print(f"随机森林模型训练完成")
    print(f"准确率: {result['accuracy']:.4f}")
    print(f"模型已保存到: {result['model_path']}")