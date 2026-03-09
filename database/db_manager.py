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
        logging.info(f'数据库管理器初始化完成，路径: {db_path}')
    
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
            sample_id TEXT NOT NULL,           -- 样本编号
            h2 REAL,                            -- 氢气 H2
            ch4 REAL,                           -- 甲烷 CH4
            c2h6 REAL,                           -- 乙烷 C2H6
            c2h4 REAL,                           -- 乙烯 C2H4
            c2h2 REAL,                           -- 乙炔 C2H2
            co REAL,                             -- 一氧化碳 CO
            co2 REAL,                            -- 二氧化碳 CO2
            fault_type TEXT,                      -- 故障类型（标签）
            fault_location TEXT,                   -- 故障位置（标签）
           采集时间 TEXT,
           备注 TEXT
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
            fault_type TEXT,
            fault_location TEXT,
            采集时间 TEXT,
            备注 TEXT
        )
        """
        
        create_uhf_table = """
        CREATE TABLE IF NOT EXISTS uhf_partial_discharge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            amplitude REAL,
            frequency REAL,
            phase REAL,
            time_difference REAL,                    -- 时差法定位用
            fault_type TEXT,
            fault_location TEXT,
            采集时间 TEXT,
            备注 TEXT
        )
        """
        
        # 创建融合特征表（用于存储PCA降维后的数据）
        create_fusion_table = """
        CREATE TABLE IF NOT EXISTS fusion_features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            pc1 REAL,                                -- 主成分1
            pc2 REAL,                                -- 主成分2
            pc3 REAL,                                -- 主成分3
            pc4 REAL,                                -- 主成分4
            pc5 REAL,                                -- 主成分5
            variance_ratio TEXT,                      -- 贡献率（JSON格式存储）
            fault_type TEXT,
            fault_location TEXT
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