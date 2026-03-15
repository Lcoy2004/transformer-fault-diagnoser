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
            'pd_channel_1': 'PD_CH1',
            'pd_channel_2': 'PD_CH2',
            'pd_channel_3': 'PD_CH3',
            'pd_channel_4': 'PD_CH4'
        }
        
        # 定义各表的关键列
        self.table_columns = {
            'oil_chromatography': {
                'required': ['h2', 'ch4', 'c2h6', 'c2h4', 'c2h2', 'fault_type', 'fault_location'],
                'optional': ['sample_time'],
                'keywords': ['h2', 'ch4', 'c2h6', 'c2h4', 'c2h2', '氢气', '甲烷', '乙烷', '乙烯', '乙炔']
            },
            'pd_channel_1': {
                'required': ['ch1_band1_energy', 'ch1_band2_energy', 'ch1_band3_energy', 'ch1_band4_energy', 
                            'ch1_kurtosis', 'ch1_main_amp', 'ch1_main_freq', 'ch1_mean', 
                            'ch1_peak', 'ch1_pulse_width', 'ch1_skewness', 'ch1_var', 
                            'fault_type', 'fault_location'],
                'optional': ['filename', 'sample_time'],
                'keywords': ['ch1_', 'channel_1', '通道1']
            },
            'pd_channel_2': {
                'required': ['ch2_band1_energy', 'ch2_band2_energy', 'ch2_band3_energy', 'ch2_band4_energy', 
                            'ch2_kurtosis', 'ch2_main_amp', 'ch2_main_freq', 'ch2_mean', 
                            'ch2_peak', 'ch2_pulse_width', 'ch2_skewness', 'ch2_var', 
                            'fault_type', 'fault_location'],
                'optional': ['filename', 'sample_time'],
                'keywords': ['ch2_', 'channel_2', '通道2']
            },
            'pd_channel_3': {
                'required': ['ch3_band1_energy', 'ch3_band2_energy', 'ch3_band3_energy', 'ch3_band4_energy', 
                            'ch3_kurtosis', 'ch3_main_amp', 'ch3_main_freq', 'ch3_mean', 
                            'ch3_peak', 'ch3_pulse_width', 'ch3_skewness', 'ch3_var', 
                            'fault_type', 'fault_location'],
                'optional': ['filename', 'sample_time'],
                'keywords': ['ch3_', 'channel_3', '通道3']
            },
            'pd_channel_4': {
                'required': ['ch4_band1_energy', 'ch4_band2_energy', 'ch4_band3_energy', 'ch4_band4_energy', 
                            'ch4_kurtosis', 'ch4_main_amp', 'ch4_main_freq', 'ch4_mean', 
                            'ch4_peak', 'ch4_pulse_width', 'ch4_skewness', 'ch4_var', 
                            'fault_type', 'fault_location'],
                'optional': ['filename', 'sample_time'],
                'keywords': ['ch4_', 'channel_4', '通道4']
            }
        }
        
        # 定义中文列名映射
        self.column_mapping = {
            '故障类别': 'fault_type',
            '故障位置': 'fault_location',
            '故障类型': 'fault_type',
            '采集时间': 'sample_time',
            '采样时间': 'sample_time',
            '时间': 'sample_time'
        }
        
        # 定义标签映射（统一分类体系）
        self.label_mapping = {
            # DGA原始标签映射到统一类别
            'DGA': {
                '正常': '正常',
                '中低温过热': '过热',
                '高温过热': '过热',
                '局部放电': '放电',
                '低能放电': '放电',
                '高能放电': '放电',
                '火花放电': '放电',
                '电弧放电': '放电'
            },
            # 局放原始标签映射到统一类别
            'PD': {
                '尖端放电': '放电',
                '悬浮放电': '放电',
                '沿面放电': '放电',
                '气隙放电': '放电'
            }
        }
        
        # 局放细分类别（用于DGA预测为放电时的细化）
        self.pd_fine_labels = ['尖端放电', '悬浮放电', '沿面放电', '气隙放电']
    
    def detect_data_type(self, df):
        """
        检测数据类型
        
        Args:
            df: DataFrame对象
        
        Returns:
            str: 数据类型（'DGA', 'HF', 'UHF', 'PD_CH1', 'PD_CH2', 'PD_CH3', 'PD_CH4' 或 None）
        """
        columns = [col.lower() for col in df.columns]
        
        # 首先检查是否是局部放电数据（包含多个通道）
        pd_channel_columns = ['ch1_', 'ch2_', 'ch3_', 'ch4_']
        pd_channel_count = sum(1 for col in columns if any(channel in col for channel in pd_channel_columns))
        
        if pd_channel_count >= 12:  # 至少有12个通道相关列（每个通道3个特征）
            logger.info(f"检测到局部放电数据，包含 {pd_channel_count} 个通道相关列")
            return 'pd_channel_1'  # 返回任意一个通道表，后续会处理所有通道
        
        # 存储所有表的匹配情况
        match_results = []
        
        for table_name, table_info in self.table_columns.items():
            # 跳过局部放电通道表，因为已经单独处理
            if table_name.startswith('pd_channel_'):
                continue
                
            keywords = table_info['keywords']
            match_count = sum(1 for col in columns if any(keyword in col for keyword in keywords))
            match_results.append((table_name, match_count))
        
        # 按匹配数量排序，选择匹配最多的表
        match_results.sort(key=lambda x: x[1], reverse=True)
        
        # 找到匹配数量最多的表
        if match_results:
            best_match, best_match_count = match_results[0]
            
            if best_match_count >= 3:  # 至少匹配3个关键词
                logger.info(f"检测到数据类型: {self.table_types[best_match]}, 匹配表: {best_match}, 匹配关键词数: {best_match_count}")
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
                # 更灵活的匹配：使用关键词匹配
                if req_col in col:
                    found_columns.append(req_col)
                    found = True
                    break
                # 对于故障类别和位置，尝试匹配中文关键词
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
            
            # 检查是否是局部放电数据（包含多个通道）
            if table_name in ['pd_channel_1', 'pd_channel_2', 'pd_channel_3', 'pd_channel_4']:
                # 对于局部放电数据，需要分别导入到四个通道表
                total_imported = 0
                
                # 导入到四个通道表
                for channel in range(1, 5):
                    channel_table = f'pd_channel_{channel}'
                    
                    # 验证该通道的列
                    is_valid, missing_columns, found_columns = self.validate_columns(df, channel_table)
                    
                    if is_valid:
                        # 导入数据到当前通道表
                        imported_count = self._import_data_to_db(df, channel_table, excel_file, progress_callback, progress_value_callback)
                        total_imported += imported_count
                        logger.info(f"成功导入 {imported_count} 条记录到表 {channel_table}")
                        send_notification(f"成功导入 {imported_count} 条记录到表 {channel_table}")
                    else:
                        logger.warning(f"表 {channel_table} 缺少必要的列: {', '.join(missing_columns)}")
                        send_notification(f"表 {channel_table} 缺少必要的列: {', '.join(missing_columns)}")
                
                send_progress_value(100)
                send_notification(f"局部放电数据导入完成，共导入 {total_imported} 条记录")
                return total_imported
            else:
                # 普通表的导入逻辑
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
                
                logger.info(f"导入完成: {imported_count} 条记录")
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
            # 使用文件名而不是完整路径，避免路径变化导致重复导入
            import os
            file_name = os.path.basename(source_file)
            
            # 检查是否已存在相同文件名的数据
            check_query = f"SELECT COUNT(*) FROM {table_name} WHERE source_file LIKE ?"
            cursor.execute(check_query, (f"%{file_name}%",))
            existing_count = cursor.fetchone()[0]
            
            if existing_count > 0:
                logger.warning(f"数据库中已存在 {existing_count} 条来自 {file_name} 的数据")
                notify(f"数据库中已存在 {existing_count} 条来自 {file_name} 的数据")
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
                            # 处理故障类型标签映射
                            if req_col == 'fault_type' and value is not None:
                                # 确定数据源类型
                                source_type = self.table_types[table_name]
                                if source_type == 'DGA':
                                    # DGA数据映射
                                    value = self.label_mapping['DGA'].get(str(value), value)
                                else:
                                    # 局放数据映射
                                    value = self.label_mapping['PD'].get(str(value), value)
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
                
                # 添加来源文件（使用文件名）
                params.append(file_name)
                
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
