# utils/data_processor.py
"""
数据处理器：负责处理数据相关的操作
"""

import logging
import os
import numpy as np
from database.db_manager import DatabaseManager
from utils.train_pca import train_pca_model
from utils.random_forest import train_random_forest
from utils.data_importer import DataImporter
from utils.predictor import Predictor
from config import notify

logger = logging.getLogger(__name__)

class DataProcessor:
    """数据处理器"""
    
    def __init__(self):
        """初始化数据处理器"""
        self.db_manager = None
        self.data_importer = None
        self.predictor = None
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        try:
            self.db_manager = DatabaseManager()
            self.data_importer = DataImporter(self.db_manager)
            self.predictor = Predictor()
            notify("数据库连接成功")
            logger.info("数据库连接成功")
        except Exception as e:
            error_msg = f"数据库初始化失败: {e}"
            notify(error_msg)
            logger.error(error_msg)
    
    def import_data(self, excel_file, table_name=None, progress_callback=None, progress_value_callback=None):
        """
        导入数据
        
        Args:
            excel_file: Excel文件路径
            table_name: 表名（如果为None，则自动检测）
            progress_callback: 进度回调函数
            progress_value_callback: 进度值回调函数
        
        Returns:
            int: 导入的记录数
        """
        try:
            if self.db_manager is None:
                self.init_database()
            
            # 如果没有指定表名，则自动检测
            if table_name is None:
                import pandas as pd
                df = pd.read_excel(excel_file)
                table_name = self.data_importer.detect_data_type(df)
                
                if table_name is None:
                    error_msg = "无法识别数据类型，请手动指定表名"
                    notify(error_msg)
                    logger.error(error_msg)
                    raise ValueError(error_msg)
            
            # 导入数据到指定表
            result = self.data_importer.import_to_table(
                excel_file=excel_file,
                table_name=table_name,
                progress_callback=progress_callback,
                progress_value_callback=progress_value_callback
            )
            return result
        except Exception as e:
            error_msg = f"导入数据失败: {e}"
            notify(error_msg)
            logger.error(error_msg)
            raise
    
    def get_all_tables(self):
        """
        获取所有表
        
        Returns:
            list: 表名列表
        """
        try:
            if self.db_manager is None:
                self.init_database()
            
            tables = self.db_manager.get_all_tables()
            return tables
        except Exception as e:
            error_msg = f"获取表列表失败: {e}"
            notify(error_msg)
            logger.error(error_msg)
            return []
    
    def get_table_data(self, table_name):
        """
        获取表数据
        
        Args:
            table_name: 表名
        
        Returns:
            tuple: (data, columns)
        """
        try:
            if self.db_manager is None:
                self.init_database()
            
            data, columns = self.db_manager.get_table_data(table_name)
            return data, columns
        except Exception as e:
            error_msg = f"获取表数据失败: {e}"
            notify(error_msg)
            logger.error(error_msg)
            return [], []
    
    def train_pca(self, progress_callback=None, progress_value_callback=None):
        """
        训练PCA模型
        
        Args:
            progress_callback: 进度回调函数
            progress_value_callback: 进度值回调函数
        
        Returns:
            dict: 训练结果
        """
        try:
            result = train_pca_model(
                progress_callback=progress_callback,
                progress_value_callback=progress_value_callback
            )
            return result
        except Exception as e:
            error_msg = f"训练PCA模型失败: {e}"
            notify(error_msg)
            logger.error(error_msg)
            raise
    
    def train_model(self, progress_callback=None, progress_value_callback=None):
        """
        训练随机森林模型
        
        Args:
            progress_callback: 进度回调函数
            progress_value_callback: 进度值回调函数
        
        Returns:
            dict: 训练结果
        """
        try:
            result = train_random_forest(
                progress_callback=progress_callback,
                progress_value_callback=progress_value_callback
            )
            return result
        except Exception as e:
            error_msg = f"训练随机森林模型失败: {e}"
            notify(error_msg)
            logger.error(error_msg)
            raise
    
    def predict(self, input_data, data_type='DGA'):
        """
        预测故障（单类型数据）
        
        Args:
            input_data: 输入数据
            data_type: 数据类型 ('DGA', 'HF', 'UHF')
        
        Returns:
            tuple: (故障类型, 故障位置)
        """
        try:
            if self.predictor is None:
                self.predictor = Predictor()
            
            fault_type, fault_location = self.predictor.predict(input_data, data_type)
            return fault_type, fault_location
        except Exception as e:
            error_msg = f"预测失败: {e}"
            notify(error_msg)
            logger.error(error_msg)
            raise
    
    def predict_multi(self, input_data_dict):
        """
        多类型数据融合预测
        
        Args:
            input_data_dict: 输入数据字典，格式为 {data_type: [values]}
                            例如: {'DGA': [33.0, 29.0, 9.0, 12.0, 0.0], 
                                   'HF': [1.2, 100.0, 30.0, 5.0]}
        
        Returns:
            dict: 预测结果字典，包含各类型预测结果和融合预测结果
                  格式: {
                      'DGA': (fault_type, fault_location),
                      'HF': (fault_type, fault_location),
                      'fusion': (fault_type, fault_location, confidence)
                  }
        """
        try:
            if self.predictor is None:
                self.predictor = Predictor()
            
            results = self.predictor.predict_multi(input_data_dict)
            return results
        except Exception as e:
            error_msg = f"多类型数据融合预测失败: {e}"
            notify(error_msg)
            logger.error(error_msg)
            raise
    
    def reload_predictor(self):
        """重新加载预测器模型"""
        try:
            self.predictor = Predictor()
            logger.info("预测器模型重新加载成功")
        except Exception as e:
            error_msg = f"预测器模型重新加载失败: {e}"
            notify(error_msg)
            logger.error(error_msg)
            raise
