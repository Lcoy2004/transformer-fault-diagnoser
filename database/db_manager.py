"""
数据库管理模块
"""

import logging
import re
import sqlite3
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)

# SQL 建表语句
CREATE_TABLE_SQL = {
    'oil_chromatography': """
        CREATE TABLE IF NOT EXISTS oil_chromatography (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            h2 REAL, ch4 REAL, c2h6 REAL, c2h4 REAL, c2h2 REAL,
            fault_type TEXT, fault_location TEXT,
            sample_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source_file TEXT
        )
    """,

    'fusion_features_dga': """
        CREATE TABLE IF NOT EXISTS fusion_features_dga (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            model_id TEXT,
            principal_components TEXT,
            fault_type TEXT, fault_location TEXT,
            sample_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source_file TEXT
        )
    """,
    'fusion_features_pd_ch1': """
        CREATE TABLE IF NOT EXISTS fusion_features_pd_ch1 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            model_id TEXT,
            principal_components TEXT,
            fault_type TEXT, fault_location TEXT,
            sample_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source_file TEXT
        )
    """,
    'fusion_features_pd_ch2': """
        CREATE TABLE IF NOT EXISTS fusion_features_pd_ch2 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            model_id TEXT,
            principal_components TEXT,
            fault_type TEXT, fault_location TEXT,
            sample_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source_file TEXT
        )
    """,
    'fusion_features_pd_ch3': """
        CREATE TABLE IF NOT EXISTS fusion_features_pd_ch3 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            model_id TEXT,
            principal_components TEXT,
            fault_type TEXT, fault_location TEXT,
            sample_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source_file TEXT
        )
    """,
    'fusion_features_pd_ch4': """
        CREATE TABLE IF NOT EXISTS fusion_features_pd_ch4 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            model_id TEXT,
            principal_components TEXT,
            fault_type TEXT, fault_location TEXT,
            sample_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source_file TEXT
        )
    """,

    'pd_channel_1': """
        CREATE TABLE IF NOT EXISTS pd_channel_1 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            filename TEXT,
            ch1_band1_energy REAL,
            ch1_band2_energy REAL,
            ch1_band3_energy REAL,
            ch1_band4_energy REAL,
            ch1_kurtosis REAL,
            ch1_main_amp REAL,
            ch1_main_freq REAL,
            ch1_mean REAL,
            ch1_peak REAL,
            ch1_pulse_width REAL,
            ch1_skewness REAL,
            ch1_var REAL,
            fault_type TEXT,
            fault_location TEXT,
            sample_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source_file TEXT
        )
    """,
    'pd_channel_2': """
        CREATE TABLE IF NOT EXISTS pd_channel_2 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            filename TEXT,
            ch2_band1_energy REAL,
            ch2_band2_energy REAL,
            ch2_band3_energy REAL,
            ch2_band4_energy REAL,
            ch2_kurtosis REAL,
            ch2_main_amp REAL,
            ch2_main_freq REAL,
            ch2_mean REAL,
            ch2_peak REAL,
            ch2_pulse_width REAL,
            ch2_skewness REAL,
            ch2_var REAL,
            fault_type TEXT,
            fault_location TEXT,
            sample_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source_file TEXT
        )
    """,
    'pd_channel_3': """
        CREATE TABLE IF NOT EXISTS pd_channel_3 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            filename TEXT,
            ch3_band1_energy REAL,
            ch3_band2_energy REAL,
            ch3_band3_energy REAL,
            ch3_band4_energy REAL,
            ch3_kurtosis REAL,
            ch3_main_amp REAL,
            ch3_main_freq REAL,
            ch3_mean REAL,
            ch3_peak REAL,
            ch3_pulse_width REAL,
            ch3_skewness REAL,
            ch3_var REAL,
            fault_type TEXT,
            fault_location TEXT,
            sample_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source_file TEXT
        )
    """,
    'pd_channel_4': """
        CREATE TABLE IF NOT EXISTS pd_channel_4 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            filename TEXT,
            ch4_band1_energy REAL,
            ch4_band2_energy REAL,
            ch4_band3_energy REAL,
            ch4_band4_energy REAL,
            ch4_kurtosis REAL,
            ch4_main_amp REAL,
            ch4_main_freq REAL,
            ch4_mean REAL,
            ch4_peak REAL,
            ch4_pulse_width REAL,
            ch4_skewness REAL,
            ch4_var REAL,
            fault_type TEXT,
            fault_location TEXT,
            sample_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source_file TEXT
        )
    """
}


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = 'database/fault_data.db'):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._ensure_directory()
        self._init_tables()
        logger.info(f"数据库初始化完成: {db_path}")
    
    def _ensure_directory(self) -> None:
        """确保数据库目录存在"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _init_tables(self) -> None:
        """初始化数据表"""
        with self._connect() as conn:
            for table_name, sql in CREATE_TABLE_SQL.items():
                conn.execute(sql)
            conn.commit()
        logger.info("数据表初始化完成")
    
    def _connect(self):
        """获取数据库连接（上下文管理器）"""
        return ConnectionContext(self.db_path)
    
    def get_connection(self):
        """获取数据库连接（需手动关闭）"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_all_tables(self) -> List[str]:
        """获取所有表名"""
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            return [row[0] for row in cursor.fetchall()]
    
    def get_table_data(self, table_name: str) -> Tuple[List[tuple], List[str]]:
        """
        获取表数据
        
        Args:
            table_name: 表名
            
        Returns:
            (数据行列表, 列名列表)
        """
        # 验证表名合法性，防止SQL注入
        if not self._is_valid_table_name(table_name):
            raise ValueError(f"非法表名: {table_name}")
        
        with self._connect() as conn:
            # 获取列信息 - PRAGMA 不支持参数化查询，但表名已通过验证
            cursor = conn.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # 获取数据 - 表名已通过_is_valid_table_name验证
            cursor = conn.execute(f"SELECT * FROM {table_name}")
            data = [tuple(row) for row in cursor.fetchall()]
            
            logger.debug(f"获取表 {table_name} 数据: {len(data)} 行")
            return data, columns
    
    def _is_valid_table_name(self, table_name: str) -> bool:
        """验证表名是否合法"""
        return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name))


class ConnectionContext:
    """数据库连接上下文管理器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
    
    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.conn.close()
        return False



