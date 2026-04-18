"""
表格管理模块
"""

import logging
from typing import Tuple, Optional
from PySide6.QtWidgets import QTableWidget, QComboBox, QTableWidgetItem
from PySide6.QtCore import Qt

logger = logging.getLogger(__name__)


class TableManager:
    """表格管理器"""
    
    def __init__(self, selector: QComboBox, table: QTableWidget, data_processor):
        """
        初始化表格管理器
        
        Args:
            selector: 表选择器
            table: 数据显示表格
            data_processor: 数据处理器
        """
        self._selector = selector
        self._table = table
        self._data = data_processor
    
    def refresh(self) -> bool:
        """
        刷新表列表
        
        Returns:
            是否成功
        """
        try:
            self._selector.clear()
            
            tables = self._data.get_all_tables()
            if tables:
                for name in tables:
                    self._selector.addItem(name)
            else:
                self._selector.addItem("暂无数据表")
                self._selector.model().item(0).setEnabled(False)
            
            logger.info("表列表刷新成功")
            return True
        except Exception as e:
            logger.error(f"刷新表列表失败: {e}")
            return False
    
    def load(self, table_name: str) -> Tuple[bool, str]:
        """
        加载表数据
        
        Args:
            table_name: 表名
            
        Returns:
            (是否成功, 消息)
        """
        try:
            data, columns = self._data.get_table_data(table_name)
            
            if not columns:
                return False, f"表 {table_name} 不存在"
            if not data:
                return False, f"表 {table_name} 为空"
            
            # 设置表格
            self._table.setColumnCount(len(columns))
            self._table.setHorizontalHeaderLabels(columns)
            self._table.setRowCount(len(data))
            
            # 设置行高
            self._table.verticalHeader().setDefaultSectionSize(36)
            
            # 填充数据
            for row_idx, row in enumerate(data):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self._table.setItem(row_idx, col_idx, item)
            
            self._table.resizeColumnsToContents()
            
            logger.info(f"加载表 {table_name}: {len(data)} 行")
            return True, f"成功加载 {len(data)} 行数据"
            
        except Exception as e:
            logger.error(f"加载表数据失败: {e}")
            return False, str(e)
    
    def on_changed(self, index: int) -> Tuple[bool, str]:
        """
        表选择变化处理
        
        Args:
            index: 选择的索引
            
        Returns:
            (是否成功, 消息)
        """
        if index < 0:
            return True, ""
        
        table_name = self._selector.currentText()
        if not table_name:
            return True, ""
        
        return self.load(table_name)
    
    def get_current_table(self) -> Optional[str]:
        """获取当前选中的表名"""
        name = self._selector.currentText()
        return name if name else None
