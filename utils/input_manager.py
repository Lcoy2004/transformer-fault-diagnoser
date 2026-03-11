"""
输入管理模块
"""

import logging
from typing import List, Optional, Dict
from PySide6.QtWidgets import QTableWidget, QComboBox, QTableWidgetItem
from PySide6.QtCore import Qt

logger = logging.getLogger(__name__)

# 输入类型配置
INPUT_CONFIGS: Dict[str, Dict] = {
    "DGA数据": {
        'columns': ['H2', 'CH4', 'C2H6', 'C2H4', 'C2H2'],
        'type': 'DGA'
    },
    "HF局部放电": {
        'columns': ['amplitude', 'frequency', 'phase', 'pulse_count'],
        'type': 'HF'
    },
    "UHF局部放电": {
        'columns': ['amplitude', 'frequency', 'phase', 'time_difference'],
        'type': 'UHF'
    }
}


class InputManager:
    """输入管理器"""
    
    def __init__(self, combobox: QComboBox, table: QTableWidget):
        """
        初始化输入管理器
        
        Args:
            combobox: 输入类型选择下拉框
            table: 输入数据表格
        """
        self._combobox = combobox
        self._table = table
        
        self._init_combobox()
        self._update_table()
        
        # 连接信号
        self._combobox.currentIndexChanged.connect(self._on_type_changed)
    
    def _init_combobox(self) -> None:
        """初始化下拉框"""
        self._combobox.clear()
        for name in INPUT_CONFIGS.keys():
            self._combobox.addItem(name)
    
    def _update_table(self) -> None:
        """更新输入表格"""
        display_name = self._combobox.currentText()
        config = INPUT_CONFIGS.get(display_name, INPUT_CONFIGS["DGA数据"])
        columns = config['columns']
        
        self._table.setColumnCount(len(columns))
        self._table.setHorizontalHeaderLabels(columns)
        self._table.setRowCount(1)
        
        # 设置默认值
        for col in range(len(columns)):
            item = QTableWidgetItem('0.0')
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(0, col, item)
        
        logger.debug(f"更新输入表格: {config['type']}, 列: {columns}")
    
    def _on_type_changed(self, index: int) -> None:
        """输入类型变化处理"""
        self._update_table()
    
    def get_data(self) -> Optional[List[float]]:
        """
        获取输入数据
        
        Returns:
            输入数据列表，如果数据无效返回 None
        """
        data = []
        for col in range(self._table.columnCount()):
            item = self._table.item(0, col)
            if not item or not item.text().strip():
                return None
            try:
                data.append(float(item.text().strip()))
            except ValueError:
                return None
        
        logger.debug(f"获取输入数据: {data}")
        return data
    
    def set_data(self, data: List[float]) -> bool:
        """
        设置输入数据
        
        Args:
            data: 输入数据列表
            
        Returns:
            是否设置成功
        """
        if len(data) != self._table.columnCount():
            logger.error(f"数据长度不匹配: {len(data)} != {self._table.columnCount()}")
            return False
        
        for col, value in enumerate(data):
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(0, col, item)
        
        return True
    
    def clear(self) -> None:
        """清空输入数据"""
        for col in range(self._table.columnCount()):
            item = QTableWidgetItem('0.0')
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(0, col, item)
    
    def get_type(self) -> str:
        """
        获取当前输入类型
        
        Returns:
            输入类型标识 (DGA/HF/UHF)
        """
        display_name = self._combobox.currentText()
        config = INPUT_CONFIGS.get(display_name, INPUT_CONFIGS["DGA数据"])
        return config['type']
