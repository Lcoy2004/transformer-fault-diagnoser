"""
测试局部放电数据导入和处理
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_processor import DataProcessor
from config import setup_logging

# 配置日志
setup_logging()
logger = logging.getLogger(__name__)

def test_pd_import():
    """测试局部放电数据导入"""
    try:
        # 初始化数据处理器
        processor = DataProcessor()
        logger.info("数据处理器初始化成功")
        
        # 测试导入局部放电数据
        pd_data_file = 'data/pd_features_with_location.xlsx'
        
        if os.path.exists(pd_data_file):
            logger.info(f"开始导入局部放电数据: {pd_data_file}")
            
            # 导入数据（自动检测数据类型）
            imported_count = processor.import_data(pd_data_file)
            logger.info(f"成功导入 {imported_count} 条局部放电数据")
            
            # 查看所有表
            tables = processor.get_all_tables()
            logger.info(f"数据库中的表: {tables}")
            
            # 查看每个表的数据
            for table in tables:
                if table.startswith('pd_channel_'):
                    data, columns = processor.get_table_data(table)
                    logger.info(f"表 {table} 有 {len(data)} 条数据，列: {columns}")
                    if data:
                        logger.info(f"前3条数据: {data[:3]}")
        else:
            logger.warning(f"局部放电数据文件不存在: {pd_data_file}")
            
    except Exception as e:
        logger.error(f"测试失败: {e}")
        raise

def test_pca_training():
    """测试PCA训练"""
    try:
        processor = DataProcessor()
        logger.info("开始PCA训练")
        
        # 训练PCA模型
        pca_result = processor.train_pca(
            progress_callback=lambda msg: logger.info(f"PCA进度: {msg}"),
            progress_value_callback=lambda val: logger.info(f"PCA进度值: {val}%")
        )
        
        logger.info(f"PCA训练完成，保留 {pca_result['n_components']} 个主成分")
        logger.info(f"累计方差贡献率: {pca_result['cumulative_variance'][-1]:.4f}")
        
    except Exception as e:
        logger.error(f"PCA训练失败: {e}")
        raise

def test_rf_training():
    """测试随机森林训练"""
    try:
        processor = DataProcessor()
        logger.info("开始随机森林训练")
        
        # 训练随机森林模型
        rf_result = processor.train_model(
            progress_callback=lambda msg: logger.info(f"RF进度: {msg}"),
            progress_value_callback=lambda val: logger.info(f"RF进度值: {val}%")
        )
        
        logger.info(f"随机森林训练完成，准确率: {rf_result.get('accuracy', 0):.4f}")
        if 'accuracy_type' in rf_result:
            logger.info(f"故障类型准确率: {rf_result['accuracy_type']:.4f}")
            logger.info(f"故障位置准确率: {rf_result['accuracy_location']:.4f}")
        
    except Exception as e:
        logger.error(f"随机森林训练失败: {e}")
        raise

if __name__ == "__main__":
    logger.info("开始测试局部放电数据处理")
    
    # 测试数据导入
    test_pd_import()
    
    # 测试PCA训练
    test_pca_training()
    
    # 测试随机森林训练
    test_rf_training()
    
    logger.info("局部放电数据处理测试完成")
