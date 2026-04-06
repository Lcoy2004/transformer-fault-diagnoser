"""
数据导入器：负责识别数据类型和导入数据到对应表
"""

import logging
import os

import pandas as pd

from database.db_manager import DatabaseManager
from config import notify
from config.constants import (
    TABLE_TYPE_MAP, TABLE_CONFIGS, LABEL_MAPPING, COLUMN_MAPPING
)

logger = logging.getLogger(__name__)

VALID_TABLES = set(TABLE_CONFIGS.keys())


def _validate_table_name(table_name: str) -> bool:
    """验证表名是否在白名单中"""
    return table_name in VALID_TABLES


class DataImporter:
    """数据导入器"""
    
    def __init__(self, db_manager=None):
        """
        初始化数据导入器
        
        Args:
            db_manager: 数据库管理器实例
        """
        self.db_manager = db_manager or DatabaseManager()
    
    def detect_data_type(self, df):
        """
        检测数据类型
        
        Args:
            df: DataFrame对象
        
        Returns:
            str: 数据类型（表名）
        """
        columns = [col.lower() for col in df.columns]
        
        pd_channel_columns = ['ch1_', 'ch2_', 'ch3_', 'ch4_']
        pd_channel_count = sum(1 for col in columns if any(channel in col for channel in pd_channel_columns))
        
        if pd_channel_count >= 12:
            logger.info(f"检测到局部放电数据，包含 {pd_channel_count} 个通道相关列")
            return 'pd_channel_1'
        
        match_results = []
        
        for table_name, table_info in TABLE_CONFIGS.items():
            if table_name.startswith('pd_channel_'):
                continue
            
            keywords = [f.lower() for f in table_info['features'][:5]]
            match_count = sum(1 for col in columns if any(keyword in col for keyword in keywords))
            match_results.append((table_name, match_count))
        
        match_results.sort(key=lambda x: x[1], reverse=True)
        
        if match_results:
            best_match, best_match_count = match_results[0]
            
            if best_match_count >= 3:
                logger.info(f"检测到数据类型: {TABLE_TYPE_MAP[best_match]}, 匹配表: {best_match}")
                return best_match
        
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
        table_info = TABLE_CONFIGS.get(table_name)
        if not table_info:
            return False, [], []
        
        required = table_info['features'] + [table_info['label_col'], table_info['location_col']]
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
                if req_col == 'fault_type' and any(keyword in col for keyword in ['故障', '类型', '类别']):
                    found_columns.append(req_col)
                    found = True
                    break
                if req_col == 'fault_location' and any(keyword in col for keyword in ['位置', '部位']):
                    found_columns.append(req_col)
                    found = True
                    break
            if not found:
                missing_columns.append(req_col)
        
        is_valid = len(missing_columns) == 0
        return is_valid, missing_columns, found_columns
    
    def import_to_table(self, excel_file, table_name, progress_callback=None, progress_value_callback=None, pre_read_df=None):
        """
        导入数据到指定表
        
        Args:
            excel_file: Excel 文件路径
            table_name: 目标表名
            progress_callback: 进度回调
            progress_value_callback: 进度值回调
            pre_read_df: 预先读取的DataFrame（避免重复读取文件）
            
        Returns:
            int: 导入的记录数
        """
        def notify_progress(message, value=None):
            if progress_callback:
                progress_callback(message)
            else:
                notify(message)
            if value is not None and progress_value_callback:
                progress_value_callback(value)
        
        try:
            notify_progress(f"开始导入数据到表: {table_name}", 0)
            
            df = pre_read_df if pre_read_df is not None else pd.read_excel(excel_file)
            notify_progress(f"成功读取Excel文件: {excel_file}", 10)
            
            logger.info(f"数据形状: {df.shape}")
            notify_progress(f"数据形状: {df.shape}", 20)
            
            df.columns = [self._map_column_name(col.strip()) for col in df.columns]
            logger.info(f"标准化列名: {list(df.columns)}")
            
            if table_name in ['pd_channel_1', 'pd_channel_2', 'pd_channel_3', 'pd_channel_4']:
                total_imported = 0
                
                for channel in range(1, 5):
                    channel_table = f'pd_channel_{channel}'
                    
                    is_valid, missing_columns, found_columns = self.validate_columns(df, channel_table)
                    
                    if is_valid:
                        imported_count = self._import_data_to_db(df, channel_table, excel_file, progress_value_callback)
                        total_imported += imported_count
                        logger.info(f"成功导入 {imported_count} 条记录到表 {channel_table}")
                        notify_progress(f"成功导入 {imported_count} 条记录到表 {channel_table}")
                    else:
                        logger.warning(f"表 {channel_table} 缺少必要的列: {', '.join(missing_columns)}")
                        notify_progress(f"表 {channel_table} 缺少必要的列: {', '.join(missing_columns)}")
                
                notify_progress(f"局部放电数据导入完成，共导入 {total_imported} 条记录", 100)
                return total_imported
            
            is_valid, missing_columns, found_columns = self.validate_columns(df, table_name)
            
            if not is_valid:
                error_msg = f"缺少必要的列: {', '.join(missing_columns)}"
                logger.error(error_msg)
                notify_progress(error_msg)
                raise ValueError(error_msg)
            
            logger.info(f"找到必要的列: {found_columns}")
            notify_progress(f"找到必要的列: {found_columns}", 30)
            
            imported_count = self._import_data_to_db(df, table_name, excel_file, progress_value_callback)
            
            notify_progress(f"成功导入 {imported_count} 条记录到表 {table_name}", 100)
            
            logger.info(f"导入完成: {imported_count} 条记录")
            return imported_count
            
        except Exception as e:
            error_msg = f"导入数据到表 {table_name} 失败: {e}"
            logger.error(error_msg)
            notify_progress(error_msg)
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
        
        for chinese_name, english_name in COLUMN_MAPPING.items():
            if chinese_name in col_lower:
                logger.info(f"映射列名: {col_name} -> {english_name}")
                return english_name
        
        return col_lower
    
    def _import_data_to_db(self, df, table_name, source_file, progress_value_callback=None):
        """
        导入数据到数据库（批量插入优化）
        
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
        
        if not _validate_table_name(table_name):
            raise ValueError(f"无效的表名: {table_name}")
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            file_name = os.path.basename(source_file)
            
            check_query = f"SELECT COUNT(*) FROM {table_name} WHERE source_file LIKE ?"
            cursor.execute(check_query, (f"%{file_name}%",))
            existing_count = cursor.fetchone()[0]
            
            if existing_count > 0:
                logger.warning(f"数据库中已存在 {existing_count} 条来自 {file_name} 的数据")
                notify(f"数据库中已存在 {existing_count} 条来自 {file_name} 的数据")
                send_progress_value(100)
                return existing_count
            
            table_info = TABLE_CONFIGS[table_name]
            required_cols = table_info['features'] + [table_info['label_col'], table_info['location_col']]
            db_columns = ['sample_id'] + required_cols + ['source_file']
            
            columns_str = ', '.join(db_columns)
            placeholders = ', '.join(['?' for _ in db_columns])
            insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            send_progress_value(40)
            total_count = len(df)
            
            source_type = TABLE_TYPE_MAP[table_name]
            label_mapping = LABEL_MAPPING.get(source_type, {})
            
            col_map = {}
            for req_col in required_cols:
                for col in df.columns:
                    if req_col in col:
                        col_map[req_col] = col
                        break
            
            all_params = []
            for idx, row in df.iterrows():
                sample_id = f"{source_type}_{idx + 1}"
                params = [sample_id]
                
                for req_col in required_cols:
                    value = None
                    if req_col in col_map:
                        mapped_col = col_map[req_col]
                        value = row.get(mapped_col, None)
                        if req_col == table_info['label_col'] and value is not None:
                            value = label_mapping.get(str(value), value)
                    params.append(value)
                
                params.append(file_name)
                all_params.append(params)
            
            try:
                cursor.executemany(insert_query, all_params)
                imported_count = len(all_params)
            except Exception as e:
                logger.error(f"批量插入失败: {e}，尝试逐条插入")
                imported_count = 0
                for params in all_params:
                    try:
                        cursor.execute(insert_query, params)
                        imported_count += 1
                    except Exception as ex:
                        logger.error(f"插入记录失败: {ex}")
                        continue
            
            conn.commit()
            logger.info(f"成功导入 {imported_count} 条记录到表 {table_name}")
            
            return imported_count
            
        finally:
            conn.close()
