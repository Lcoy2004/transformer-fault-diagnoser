"""
数据库管理模块
"""

import logging
import os
import sqlite3
from pathlib import Path
from typing import List, Tuple, Optional, Any

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
    'hf_partial_discharge': """
        CREATE TABLE IF NOT EXISTS hf_partial_discharge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            amplitude REAL, frequency REAL, phase REAL, pulse_count INTEGER,
            fault_type TEXT, fault_location TEXT,
            sample_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source_file TEXT
        )
    """,
    'uhf_partial_discharge': """
        CREATE TABLE IF NOT EXISTS uhf_partial_discharge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            amplitude REAL, frequency REAL, phase REAL, time_difference REAL,
            fault_type TEXT, fault_location TEXT,
            sample_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source_file TEXT
        )
    """,
    'fusion_features': """
        CREATE TABLE IF NOT EXISTS fusion_features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            model_id TEXT,
            principal_components TEXT,
            fault_type TEXT, fault_location TEXT,
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
        with self._connect() as conn:
            # 获取列信息
            cursor = conn.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # 获取数据
            cursor = conn.execute(f"SELECT * FROM {table_name}")
            data = [tuple(row) for row in cursor.fetchall()]
            
            logger.debug(f"获取表 {table_name} 数据: {len(data)} 行")
            return data, columns
    
    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """执行 SQL 语句"""
        with self._connect() as conn:
            return conn.execute(sql, params)
    
    def executemany(self, sql: str, params_list: List[tuple]) -> sqlite3.Cursor:
        """批量执行 SQL 语句"""
        with self._connect() as conn:
            return conn.executemany(sql, params_list)


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


if __name__ == "__main__":
    # 测试
    db = DatabaseManager()
    print(f"表列表: {db.get_all_tables()}")
