# utils/data_importer.py
"""
数据导入器：负责识别数据类型和导入数据到对应表
"""

import logging
import pandas as pd
from database.db_manager import DatabaseManager
from config import notify

logger = logging.getLogger(__name__)

class DataImporter:
    """数据导入器"""
    
    def __init__(self, db_manager=None):
        """
        初始化数据导入器
        
        Args:
            db_manager: 数据库管理器实例
        """
        self.db_manager = db_manager or DatabaseManager()
        
        # 定义表类型映射
        self.table_types = {
            'oil_chromatography': 'DGA',
            'hf_partial_discharge': 'HF',
            'uhf_partial_discharge': 'UHF'
        }
        
        # 定义各表的关键列
        self.table_columns = {
            'oil_chromatography': {
                'required': ['h2', 'ch4', 'c2h6', 'c2h4', 'c2h2'],
                'optional': ['fault_type', 'fault_location', '采集时间', '备注'],
                'keywords': ['h2', 'ch4', 'c2h6', 'c2h4', 'c2h2', '氢气', '甲烷', '乙烷', '乙烯', '乙炔']
            },
            'hf_partial_discharge': {
                'required': ['amplitude', 'frequency', 'phase', 'pulse_count'],
                'optional': ['fault_type', 'fault_location', '采集时间', '备注'],
                'keywords': ['amplitude', 'frequency', 'phase', 'pulse_count', '幅值', '频率', '相位', '脉冲']
            },
            'uhf_partial_discharge': {
                'required': ['amplitude', 'frequency', 'phase', 'time_difference'],
                'optional': ['fault_type', 'fault_location', '采集时间', '备注'],
                'keywords': ['amplitude', 'frequency', 'phase', 'time_difference', '幅值', '频率', '相位', '时差']
            }
        }
        
        # 定义中文列名映射
        self.column_mapping = {
            '故障类别': 'fault_type',
            '故障位置': 'fault_location',
            '故障类型': 'fault_type'
        }
    
    def detect_data_type(self, df):
        """
        检测数据类型
        
        Args:
            df: DataFrame对象
        
        Returns:
            str: 数据类型（'DGA', 'HF', 'UHF' 或 None）
        """
        columns = [col.lower() for col in df.columns]
        
        for table_name, table_info in self.table_columns.items():
            keywords = table_info['keywords']
            match_count = sum(1 for col in columns if any(keyword in col for keyword in keywords))
            
            if match_count >= 3:  # 至少匹配3个关键词
                logger.info(f"检测到数据类型: {self.table_types[table_name]}, 匹配表: {table_name}")
                return table_name
        
        logger.warning("无法识别数据类型")
        return None
    
    def validate_columns(self, df, table_name):
        """
        验证列是否符合要求
        
        Args:
            df: DataFrame对象
            table_name: 表名
        
        Returns:
            tuple: (is_valid, missing_columns, found_columns)
        """
        table_info = self.table_columns.get(table_name)
        if not table_info:
            return False, [], []
        
        required = table_info['required']
        columns = [col.lower() for col in df.columns]
        
        missing_columns = []
        found_columns = []
        
        for req_col in required:
            found = False
            for col in columns:
                if req_col in col:
                    found_columns.append(req_col)
                    found = True
                    break
            if not found:
                missing_columns.append(req_col)
        
        is_valid = len(missing_columns) == 0
        return is_valid, missing_columns, found_columns
    
    def import_to_table(self, excel_file, table_name, progress_callback=None, progress_value_callback=None):
        """
        导入数据到指定表
        
        Args:
            excel_file: Excel文件路径
            table_name: 表名
            progress_callback: 进度回调函数
            progress_value_callback: 进度值回调函数
        
        Returns:
            int: 导入的记录数
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
            send_notification(f"开始导入数据到表: {table_name}")
            send_progress_value(0)
            
            df = pd.read_excel(excel_file)
            logger.info(f"成功读取Excel文件: {excel_file}")
            send_notification(f"成功读取Excel文件: {excel_file}")
            send_progress_value(10)
            
            logger.info(f"数据形状: {df.shape}")
            send_notification(f"数据形状: {df.shape}")
            send_progress_value(20)
            
            # 标准化列名：将中文列名映射到英文
            original_columns = df.columns.tolist()
            df.columns = [self._map_column_name(col.strip()) for col in df.columns]
            logger.info(f"标准化列名: {list(df.columns)}")
            
            # 验证列
            is_valid, missing_columns, found_columns = self.validate_columns(df, table_name)
            
            if not is_valid:
                error_msg = f"缺少必要的列: {', '.join(missing_columns)}"
                logger.error(error_msg)
                send_notification(error_msg)
                raise ValueError(error_msg)
            
            logger.info(f"找到必要的列: {found_columns}")
            send_notification(f"找到必要的列: {found_columns}")
            send_progress_value(30)
            
            # 导入数据
            imported_count = self._import_data_to_db(df, table_name, excel_file, progress_callback, progress_value_callback)
            
            send_notification(f"成功导入 {imported_count} 条记录到表 {table_name}")
            send_progress_value(100)
            
            return imported_count
            
        except Exception as e:
            error_msg = f"导入数据到表 {table_name} 失败: {e}"
            logger.error(error_msg)
            send_notification(error_msg)
            raise
    
    def _map_column_name(self, col_name):
        """
        映射列名
        
        Args:
            col_name: 原始列名
        
        Returns:
            str: 映射后的列名
        """
        col_lower = col_name.lower()
        
        # 检查是否是中文列名，需要映射到英文
        for chinese_name, english_name in self.column_mapping.items():
            if chinese_name in col_lower:
                logger.info(f"映射列名: {col_name} -> {english_name}")
                return english_name
        
        # 如果不是中文列名，直接返回小写
        return col_lower
    
    def _import_data_to_db(self, df, table_name, source_file, progress_callback=None, progress_value_callback=None):
        """
        导入数据到数据库
        
        Args:
            df: DataFrame对象
            table_name: 表名
            source_file: 源文件路径
            progress_callback: 进度回调函数
            progress_value_callback: 进度值回调函数
        
        Returns:
            int: 导入的记录数
        """
        def send_progress_value(value):
            if progress_value_callback:
                progress_value_callback(value)
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # 检查是否已存在相同来源文件的数据
            check_query = f"SELECT COUNT(*) FROM {table_name} WHERE source_file = ?"
            cursor.execute(check_query, (source_file,))
            existing_count = cursor.fetchone()[0]
            
            if existing_count > 0:
                logger.warning(f"数据库中已存在 {existing_count} 条来自 {source_file} 的数据")
                notify(f"数据库中已存在 {existing_count} 条来自 {source_file} 的数据")
                return existing_count
            
            # 构建插入语句
            table_info = self.table_columns[table_name]
            db_columns = ['sample_id'] + table_info['required'] + table_info['optional'] + ['source_file']
            
            columns_str = ', '.join(db_columns)
            placeholders = ', '.join(['?' for _ in db_columns])
            insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            imported_count = 0
            send_progress_value(40)
            total_count = len(df)
            
            for _, row in df.iterrows():
                current_index = imported_count + 1
                sample_id = f"{self.table_types[table_name]}_{current_index}"
                
                params = [sample_id]
                
                # 添加必需列数据
                for req_col in table_info['required']:
                    value = None
                    for col in df.columns:
                        if req_col in col:
                            value = row.get(col, None)
                            break
                    params.append(value)
                
                # 添加可选列数据
                for opt_col in table_info['optional']:
                    value = None
                    for col in df.columns:
                        if opt_col in col:
                            value = row.get(col, None)
                            break
                    params.append(value)
                
                # 添加来源文件
                params.append(str(source_file))
                
                try:
                    cursor.execute(insert_query, params)
                    imported_count += 1
                    
                    if imported_count % max(1, total_count // 10) == 0:
                        progress = 40 + (imported_count / total_count) * 50
                        send_progress_value(int(progress))
                        
                except Exception as e:
                    logger.error(f"导入第 {current_index} 条记录失败: {e}")
                    continue
            
            conn.commit()
            logger.info(f"成功导入 {imported_count} 条记录到表 {table_name}")
            
            return imported_count
            
        finally:
            conn.close()
