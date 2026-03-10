# utils/multi_input_manager.py
"""
多类型输入数据管理器：支持同时输入DGA、HF、UHF三类数据
"""

import logging
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                                QTableWidgetItem, QLabel, QGroupBox, QPushButton,
                                QCheckBox)
from PySide6.QtCore import Qt

logger = logging.getLogger(__name__)

class MultiInputManager:
    """多类型输入数据管理器"""
    
    def __init__(self, parent_widget):
        """
        初始化多类型输入数据管理器
        
        Args:
            parent_widget: 父窗口部件
        """
        self.parent_widget = parent_widget
        
        # 定义不同输入类型的列配置
        self.input_configs = {
            "DGA": {
                'columns': ['H2', 'CH4', 'C2H6', 'C2H4', 'C2H2'],
                'label': 'DGA数据 (油色谱)',
                'enabled': True
            },
            "HF": {
                'columns': ['amplitude', 'frequency', 'phase', 'pulse_count'],
                'label': 'HF局部放电 (高频)',
                'enabled': False
            },
            "UHF": {
                'columns': ['amplitude', 'frequency', 'phase', 'time_difference'],
                'label': 'UHF局部放电 (超高频)',
                'enabled': False
            }
        }
        
        # 存储输入数据
        self.input_data = {
            "DGA": None,
            "HF": None,
            "UHF": None
        }
        
        # 存储复选框状态
        self.checkboxes = {}
        
        # 存储表格部件
        self.tables = {}
        
        # 创建UI
        self.create_ui()
    
    def create_ui(self):
        """创建多类型输入UI"""
        # 创建主布局
        self.main_layout = QVBoxLayout()
        
        # 为每种数据类型创建输入组
        for data_type, config in self.input_configs.items():
            group = self.create_input_group(data_type, config)
            self.main_layout.addWidget(group)
        
        # 设置布局
        container = QWidget()
        container.setLayout(self.main_layout)
        
        # 如果父窗口有布局，添加到父窗口
        if self.parent_widget.layout():
            self.parent_widget.layout().addWidget(container)
        else:
            layout = QVBoxLayout()
            layout.addWidget(container)
            self.parent_widget.setLayout(layout)
    
    def create_input_group(self, data_type, config):
        """
        创建输入组
        
        Args:
            data_type: 数据类型
            config: 配置信息
        
        Returns:
            QGroupBox: 输入组
        """
        # 创建组
        group = QGroupBox(config['label'])
        group_layout = QVBoxLayout()
        
        # 创建复选框
        checkbox = QCheckBox("启用此类型数据")
        checkbox.setChecked(config['enabled'])
        checkbox.stateChanged.connect(lambda state, dt=data_type: self.on_checkbox_changed(dt, state))
        self.checkboxes[data_type] = checkbox
        group_layout.addWidget(checkbox)
        
        # 创建表格
        table = QTableWidget()
        table.setColumnCount(len(config['columns']))
        table.setHorizontalHeaderLabels(config['columns'])
        table.setRowCount(1)
        
        # 设置默认值
        for col in range(len(config['columns'])):
            item = QTableWidgetItem('0.0')
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(0, col, item)
        
        # 根据启用状态设置表格可用性
        table.setEnabled(config['enabled'])
        self.tables[data_type] = table
        group_layout.addWidget(table)
        
        # 设置组布局
        group.setLayout(group_layout)
        
        return group
    
    def on_checkbox_changed(self, data_type, state):
        """
        复选框状态变化处理
        
        Args:
            data_type: 数据类型
            state: 复选框状态
        """
        enabled = state == Qt.CheckState.Checked.value
        self.input_configs[data_type]['enabled'] = enabled
        self.tables[data_type].setEnabled(enabled)
        logger.info(f"{data_type} 数据类型 {'启用' if enabled else '禁用'}")
    
    def get_input_data(self):
        """
        获取所有启用的输入数据
        
        Returns:
            dict: 输入数据字典，格式为 {data_type: [values]}
        """
        result = {}
        
        for data_type, config in self.input_configs.items():
            if not config['enabled']:
                continue
            
            table = self.tables[data_type]
            input_data = []
            
            for col in range(table.columnCount()):
                item = table.item(0, col)
                if not item or not item.text().strip():
                    logger.warning(f"{data_type} 数据第 {col+1} 列为空")
                    continue
                try:
                    value = float(item.text().strip())
                    input_data.append(value)
                except ValueError:
                    logger.error(f"{data_type} 数据第 {col+1} 列格式错误: {item.text()}")
                    return None
            
            if input_data:
                result[data_type] = input_data
                logger.info(f"获取到 {data_type} 数据: {input_data}")
        
        return result if result else None
    
    def get_enabled_types(self):
        """
        获取启用的数据类型
        
        Returns:
            list: 启用的数据类型列表
        """
        return [dt for dt, config in self.input_configs.items() if config['enabled']]
    
    def set_input_data(self, data_type, data):
        """
        设置输入数据
        
        Args:
            data_type: 数据类型
            data: 数据列表
        
        Returns:
            bool: 是否成功
        """
        try:
            if data_type not in self.tables:
                logger.error(f"未知的数据类型: {data_type}")
                return False
            
            table = self.tables[data_type]
            if len(data) != table.columnCount():
                logger.error(f"数据长度不匹配: {len(data)} != {table.columnCount()}")
                return False
            
            for col, value in enumerate(data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(0, col, item)
            
            logger.info(f"设置 {data_type} 数据: {data}")
            return True
        except Exception as e:
            logger.error(f"设置 {data_type} 数据失败: {e}")
            return False
    
    def clear_all_data(self):
        """清空所有输入数据"""
        for data_type, table in self.tables.items():
            for col in range(table.columnCount()):
                item = QTableWidgetItem('0.0')
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(0, col, item)
        
        logger.info("清空所有输入数据")
    
    def enable_type(self, data_type, enabled=True):
        """
        启用/禁用特定数据类型
        
        Args:
            data_type: 数据类型
            enabled: 是否启用
        """
        if data_type in self.checkboxes:
            self.checkboxes[data_type].setChecked(enabled)
    
    def is_type_enabled(self, data_type):
        """
        检查数据类型是否启用
        
        Args:
            data_type: 数据类型
        
        Returns:
            bool: 是否启用
        """
        return self.input_configs.get(data_type, {}).get('enabled', False)
