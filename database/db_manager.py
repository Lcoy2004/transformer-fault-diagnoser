# database/db_manager.py
import sqlite3
import pandas as pd
import logging
from pathlib import Path


logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器：负责连接、建表、导入数据等操作"""
    
    def __init__(self, db_path='database/fault_data.db'):
        """
        初始化数据库管理器
        :param db_path: 数据库文件路径，默认放在 database 文件夹下
        """
        self.db_path = db_path
        # 确保数据库目录存在
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._create_tables()
        logger.info(f'数据库管理器初始化完成，路径: {db_path}')
    
    def get_connection(self):
        """获取数据库连接（每次操作后记得关闭）"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 使查询结果可以通过列名访问
        return conn
    
    def _create_tables(self):
        """创建所需的表（如果不存在）"""
        create_oil_table = """
        CREATE TABLE IF NOT EXISTS oil_chromatography (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            h2 REAL,                            -- 氢气 H2
            ch4 REAL,                           -- 甲烷 CH4
            c2h6 REAL,                          -- 乙烷 C2H6
            c2h4 REAL,                          -- 乙烯 C2H4
            c2h2 REAL,                          -- 乙炔 C2H2
            fault_type TEXT,                    -- 故障类型（标签）
            fault_location TEXT,                -- 故障位置（标签）
            采集时间 TEXT,
            备注 TEXT,
            sample_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,   -- 记录导入时间
            source_file TEXT                                    -- 记录来源文件
        )
        """
        
        create_hf_table = """
        CREATE TABLE IF NOT EXISTS hf_partial_discharge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            amplitude REAL,                        -- 放电幅值 (pC)
            frequency REAL,                         -- 频率特征
            phase REAL,                             -- 相位特征
            pulse_count INTEGER,                     -- 脉冲计数
            fault_type TEXT,                        -- 故障类型（标签）
            fault_location TEXT,                    -- 故障位置（标签）
            采集时间 TEXT,
            备注 TEXT,
            sample_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,   -- 记录导入时间
            source_file TEXT                                    -- 记录来源文件
        )
        """
        
        create_uhf_table = """
        CREATE TABLE IF NOT EXISTS uhf_partial_discharge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            amplitude REAL,                        -- 放电幅值
            frequency REAL,                         -- 频率特征
            phase REAL,                             -- 相位特征
            time_difference REAL,                    -- 时差法定位用
            fault_type TEXT,                        -- 故障类型（标签）
            fault_location TEXT,                    -- 故障位置（标签）
            采集时间 TEXT,
            备注 TEXT,
            sample_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,   -- 记录导入时间
            source_file TEXT                                    -- 记录来源文件
        )
        """
        
        # 创建融合特征表（用于存储PCA降维后的数据）
        create_fusion_table = """
        CREATE TABLE IF NOT EXISTS fusion_features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            model_id TEXT,                            -- 模型ID
            principal_components TEXT,               -- 主成分得分（JSON格式存储）
            fault_type TEXT,                        -- 故障类型（标签）
            fault_location TEXT,                    -- 故障位置（标签）
            sample_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,   -- 记录导入时间
            source_file TEXT                                    -- 记录来源文件
        )
        """
        
        conn = self.get_connection()
        try:
            conn.execute(create_oil_table)
            conn.execute(create_hf_table)
            conn.execute(create_uhf_table)
            conn.execute(create_fusion_table)
            conn.commit()
            logger.info('数据库表创建/检查完成')
        except Exception as e:
            logger.error(f'创建表失败: {e}')
            raise
        finally:
            conn.close()
    
    def import_dga_data(self, excel_file='DGA_data.xlsx'):##默认路径DGA_data.xlsx
        """
        从Excel文件导入DGA数据到数据库
        
        Args:
            excel_file (str): Excel文件名，默认在 data 目录下
        
        Returns:
            int: 导入的记录数
        """
        import os
        
        # 获取Excel文件路径
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(root_dir, 'data')
        excel_path = os.path.join(data_dir, excel_file)
        
        try:
            # 读取Excel文件
            df = pd.read_excel(excel_path)
            logger.info(f"成功读取Excel文件: {excel_path}")
            logger.info(f"数据形状: {df.shape}")
            
            # 保存原始列名
            original_columns = df.columns.tolist()
            logger.info(f"原始列名: {original_columns}")
            
            # 标准化列名（用于匹配）
            df.columns = [col.strip().lower() for col in df.columns]
            logger.info(f"标准化列名: {list(df.columns)}")
            
            # 提取需要的列
            required_columns = ['h2', 'ch4', 'c2h6', 'c2h4', 'c2h2']
            label_column = None
            
            # 更灵活的故障类型列识别
            fault_type_keywords = ['故障类别', 'fault_type', '故障', '类型', 'label', '标签', 'fault']
            
            # 检查标准化后的列名
            for col in df.columns:
                # 检查中文关键词
                if any(key in col for key in ['故障', '类型', '标签']):
                    label_column = col
                    logger.info(f"识别到故障类型列: {col}")
                    break
                # 检查英文关键词
                if any(key in col for key in ['fault', 'label']):
                    label_column = col
                    logger.info(f"识别到故障类型列: {col}")
                    break
            
            if label_column:
                required_columns.append(label_column)
                logger.info(f"添加故障类型列到导入列表: {label_column}")
            else:
                logger.warning("未找到故障类型列，将不导入故障类型数据")
            
            # 过滤数据
            valid_columns = [col for col in required_columns if col in df.columns]
            df_filtered = df[valid_columns].copy()
            
            # 去除空值
            df_filtered = df_filtered.dropna()
            logger.info(f"过滤后数据形状: {df_filtered.shape}")
            
            # 导入数据到数据库
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # 构建动态的插入语句，根据实际存在的列
            db_columns = ['sample_id', 'h2', 'ch4', 'c2h6', 'c2h4', 'c2h2']
            if label_column:
                db_columns.append('fault_type')
            db_columns.append('source_file')
            
            # 构建SQL语句
            columns_str = ', '.join(db_columns)
            placeholders = ', '.join(['?' for _ in db_columns])
            insert_query = f"""
            INSERT INTO oil_chromatography 
            ({columns_str})
            VALUES ({placeholders})
            """
            
            imported_count = 0
            for idx, row in df_filtered.iterrows():
                sample_id = f"DGA_{idx+1}"
                
                # 构建参数，根据列名动态获取值
                params = [sample_id]
                
                # 添加气体成分数据
                gas_columns = ['h2', 'ch4', 'c2h6', 'c2h4', 'c2h2']
                for gas_col in gas_columns:
                    # 尝试不同的列名变体
                    found_value = None
                    for col in df.columns:
                        if col.strip().lower() == gas_col:
                            found_value = row.get(col, None)
                            break
                    params.append(found_value)
                
                # 添加故障类型
                if label_column:
                    params.append(row.get(label_column, None))
                
                # 添加来源文件
                params.append(excel_file)
                
                try:
                    cursor.execute(insert_query, params)
                    imported_count += 1
                except Exception as e:
                    logger.error(f"导入第 {idx+1} 条记录失败: {e}")  
                    continue
            
            conn.commit()
            logger.info(f"成功导入 {imported_count} 条DGA数据")
            
            return imported_count
            
        except FileNotFoundError:
            logger.error(f"未找到Excel文件: {excel_path}")
            raise
        except Exception as e:
            logger.error(f"导入DGA数据失败: {e}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()
    
    def create_partial_discharge_table(self):
        """
        创建变压器局部放电特征数据表
        """
        create_pd_table = """
        CREATE TABLE IF NOT EXISTS transformer_partial_discharge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            discharge_type TEXT,                -- 放电类型
            phase_resolved_pattern TEXT,        -- 相位解析图谱特征
            time_domain_features TEXT,          -- 时域特征
            frequency_domain_features TEXT,     -- 频域特征
            statistical_features TEXT,          -- 统计特征
            severity_level INTEGER,             -- 严重程度
            fault_location TEXT,                -- 故障位置
            acquisition_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 采集时间
            source_device TEXT,                 -- 采集设备
            remarks TEXT                        -- 备注
        )
        """
        
        conn = self.get_connection()
        try:
            conn.execute(create_pd_table)
            conn.commit()
            logger.info('变压器局部放电特征数据表创建/检查完成')
        except Exception as e:
            logger.error(f'创建局部放电表失败: {e}')
            raise
        finally:
            conn.close()
if __name__ == "__main__":
    # 当直接运行脚本时执行导入
    # 实例化数据库管理器并导入DGA数据
    db_manager = DatabaseManager()
    db_manager.import_dga_data('DGA_data.xlsx')
