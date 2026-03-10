# database/db_manager.py
import sys
import os
import sqlite3
import pandas as pd
import logging
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import notify


logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器：负责连接、建表、查询数据等操作"""
    
    def __init__(self, db_path='database/fault_data.db'):
        """
        初始化数据库管理器
        :param db_path: 数据库文件路径，默认放在 database 文件夹下
        """
        self.db_path = db_path
        # 确保数据库目录存在
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        try:
            self._create_tables()
            logger.info('数据库表创建/检查完成')
            notify('数据库表创建/检查完成')
            logger.info(f'数据库管理器初始化完成，路径: {db_path}')
            notify(f'数据库连接成功，路径: {db_path}')
        except Exception as e:
            error_msg = f'数据库初始化失败: {e}'
            logger.error(error_msg)
            notify(error_msg)
            raise
    
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
    
    def get_all_tables(self):
        """
        获取数据库中的所有表
        
        Returns:
            list: 表名列表
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            # 查询所有表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in cursor.fetchall()]
            logger.info(f"获取到的表列表: {tables}")
            return tables
        except Exception as e:
            logger.error(f'获取表列表失败: {e}')
            raise
        finally:
            conn.close()
    
    def get_table_data(self, table_name):
        """
        获取指定表的数据
        
        Args:
            table_name (str): 表名
        
        Returns:
            tuple: (data, columns)
                data: 数据行列表
                columns: 列名列表
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            logger.info(f"获取表 {table_name} 的数据")
            
            # 安全地引用表名
            # 使用单引号包裹表名，避免SQL注入
            safe_table_name = f"'{table_name}'"
            
            # 查询表结构
            cursor.execute("PRAGMA table_info(" + table_name + ")")
            columns_info = cursor.fetchall()
            columns = [col[1] for col in columns_info]
            logger.info(f"表 {table_name} 的列: {columns}")
            
            # 查询表数据
            cursor.execute("SELECT * FROM " + table_name)
            data = cursor.fetchall()
            
            # 将Row对象转换为元组
            data = [tuple(row) for row in data]
            logger.info(f"表 {table_name} 的数据行数: {len(data)}")
            
            return data, columns
        except Exception as e:
            logger.error(f'获取表数据失败: {e}, 表名: {table_name}')
            raise
        finally:
            conn.close()
if __name__ == "__main__":
    # 当直接运行脚本时执行
    # 实例化数据库管理器
    db_manager = DatabaseManager()
