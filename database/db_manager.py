"""
数据库管理模块
"""

import logging
import re
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def _create_dga_table_sql() -> str:
    return """
        CREATE TABLE IF NOT EXISTS oil_chromatography (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            h2 REAL, ch4 REAL, c2h6 REAL, c2h4 REAL, c2h2 REAL,
            fault_type TEXT, fault_location TEXT,
            sample_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source_file TEXT
        )
    """

def _create_pca_table_sql(table_name: str) -> str:
    return f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            model_id TEXT,
            principal_components TEXT,
            fault_type TEXT, fault_location TEXT,
            sample_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source_file TEXT
        )
    """

def _create_pd_table_sql(channel: int) -> str:
    return f"""
        CREATE TABLE IF NOT EXISTS pd_channel_{channel} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            filename TEXT,
            ch{channel}_band1_energy REAL, ch{channel}_band2_energy REAL,
            ch{channel}_band3_energy REAL, ch{channel}_band4_energy REAL,
            ch{channel}_kurtosis REAL, ch{channel}_main_amp REAL,
            ch{channel}_main_freq REAL, ch{channel}_mean REAL,
            ch{channel}_peak REAL, ch{channel}_pulse_width REAL,
            ch{channel}_skewness REAL, ch{channel}_var REAL,
            fault_type TEXT, fault_location TEXT,
            sample_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source_file TEXT
        )
    """

CREATE_TABLE_SQL = {
    'oil_chromatography': _create_dga_table_sql(),
    **{f'fusion_features_pd_ch{i}': _create_pca_table_sql(f'fusion_features_pd_ch{i}') for i in range(1, 5)},
    **{f'fusion_features_dga': _create_pca_table_sql('fusion_features_dga')},
    **{f'pd_channel_{i}': _create_pd_table_sql(i) for i in range(1, 5)}
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
    
    def get_latest_row(self, table_name: str) -> Optional[Dict[str, float]]:
        """
        获取表的最新一行数据（按id降序）
        
        Args:
            table_name: 表名
            
        Returns:
            字典形式的最新行数据，如果表为空返回None
        """
        if not self._is_valid_table_name(table_name):
            raise ValueError(f"非法表名: {table_name}")
        
        with self._connect() as conn:
            cursor = conn.execute(f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return {col: float(row[col]) if row[col] is not None else 0.0 for col in columns}
            return None


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
            self.conn.commit()  # type: ignore
        else:
            self.conn.rollback()  # type: ignore
        self.conn.close()  # type: ignore
        return False



