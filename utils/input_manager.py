"""
输入管理模块
"""

import logging
from typing import List, Optional, Dict
from PySide6.QtWidgets import QTableWidget, QComboBox, QTableWidgetItem
from PySide6.QtCore import Qt

from config.constants import INPUT_CONFIGS

logger = logging.getLogger(__name__)


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
        self._cache: Dict[str, List[float]] = {}
        self._previous_type: Optional[str] = None
        
        self._init_combobox()
        self._update_table()
        self._previous_type = self.get_type()
        
        self._combobox.currentIndexChanged.connect(self._on_type_changed)
    
    def _init_combobox(self) -> None:
        """初始化下拉框"""
        self._combobox.clear()
        for name in INPUT_CONFIGS.keys():
            self._combobox.addItem(name)
    
    def _update_table(self) -> None:
        """更新输入表格（转置显示：特征名为行，输入值为列）"""
        display_name = self._combobox.currentText()
        config = INPUT_CONFIGS.get(display_name)
        
        if config is None:
            logger.error(f"未找到配置: {display_name}")
            config = INPUT_CONFIGS["DGA数据"]
        
        columns = config['columns']
        descriptions = config.get('descriptions', [''] * len(columns))
        
        logger.info(f"更新表格: {display_name} -> {config['type']}, 特征数: {len(columns)}")
        
        self._table.clear()
        self._table.setColumnCount(3)
        self._table.setHorizontalHeaderLabels(['特征', '数值', '备注'])
        self._table.setRowCount(len(columns))
        
        for row, (col_name, desc) in enumerate(zip(columns, descriptions)):
            name_item = QTableWidgetItem(col_name)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(row, 0, name_item)
            
            value_item = QTableWidgetItem('0.0')
            value_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 1, value_item)
            
            desc_item = QTableWidgetItem(desc)
            desc_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            desc_item.setForeground(Qt.GlobalColor.gray)
            self._table.setItem(row, 2, desc_item)
        
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.update()
        logger.info(f"表格更新完成: {config['type']}, 特征: {columns}")
    
    def _on_type_changed(self, index: int) -> None:
        """输入类型变化处理"""
        if self._previous_type is not None:
            self._cache_current_data_with_type(self._previous_type)
        
        self._update_table()
        self._load_cached_data()
        
        self._previous_type = self.get_type()
    
    def _cache_current_data_with_type(self, data_type: str) -> None:
        """缓存当前输入数据到指定类型"""
        data = []
        has_invalid = False
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 1)
            if item and item.text().strip():
                try:
                    data.append(float(item.text().strip()))
                except ValueError:
                    logger.warning(f"第{row+1}行数据格式无效: '{item.text()}'")
                    has_invalid = True
                    break
            else:
                data.append(0.0)
        
        if not has_invalid:
            self._cache[data_type] = data
            logger.debug(f"缓存数据: {data_type} = {data}")
    
    def get_data(self) -> Optional[List[float]]:
        """
        获取输入数据
        
        Returns:
            输入数据列表，如果数据无效返回 None
        """
        data = []
        invalid_rows = []
        
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 1)
            if not item or not item.text().strip():
                invalid_rows.append((row, "空值"))
                continue
            try:
                data.append(float(item.text().strip()))
            except ValueError:
                invalid_rows.append((row, f"无效格式: '{item.text()}'"))
        
        if invalid_rows:
            for row, reason in invalid_rows:
                logger.warning(f"第{row+1}行数据{reason}")
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
        if len(data) != self._table.rowCount():
            logger.error(f"数据长度不匹配: {len(data)} != {self._table.rowCount()}")
            return False
        
        for row, value in enumerate(data):
            item = QTableWidgetItem(str(value))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 1, item)
        
        return True
    
    def clear(self) -> None:
        """清空输入数据"""
        for row in range(self._table.rowCount()):
            item = QTableWidgetItem('0.0')
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 1, item)
    
    def _load_cached_data(self) -> None:
        """加载缓存数据到表格"""
        data_type = self.get_type()
        if data_type in self._cache:
            data = self._cache[data_type]
            table_rows = self._table.rowCount()
            data_len = len(data)
            
            if data_len == table_rows:
                for row, value in enumerate(data):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self._table.setItem(row, 1, item)
            else:
                logger.warning(
                    f"缓存数据长度({data_len})与表格行数({table_rows})不匹配，"
                    f"类型: {data_type}，跳过加载缓存"
                )
    
    def get_all_cached_data(self) -> Dict[str, List[float]]:
        """
        获取所有缓存数据

        Returns:
            所有已输入的数据字典
        """
        return self._cache.copy()
    
    def clear_cache(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self.clear()
        logger.info("缓存已清空")
    
    def has_valid_pd_data(self) -> bool:
        """
        检查是否有有效的PD数据（非全零）

        Returns:
            是否有有效PD数据
        """
        for pd_type in self._cache:
            if pd_type.startswith('PD_CH'):
                data = self._cache[pd_type]
                if data and any(v != 0.0 for v in data):
                    return True
        return False
    
    def get_type(self) -> str:
        """
        获取当前输入类型
        
        Returns:
            输入类型标识 (DGA/PD_CH1/PD_CH2/PD_CH3/PD_CH4)
        """
        display_name = self._combobox.currentText()
        config = INPUT_CONFIGS.get(display_name, INPUT_CONFIGS["DGA数据"])
        return config['type']
    
    def save_current_to_cache(self) -> None:
        """保存当前显示的数据到缓存"""
        current_type = self.get_type()
        self._cache_current_data_with_type(current_type)
        self._previous_type = current_type
