# utils/input_manager.py
"""
输入数据管理器：负责处理用户输入数据的管理
"""

import logging
from PySide6.QtWidgets import QTableWidget, QComboBox, QTableWidgetItem
from PySide6.QtCore import Qt

logger = logging.getLogger(__name__)

class InputManager:
    """输入数据管理器"""
    
    def __init__(self, input_combobox, showinput_tableWidget):
        """
        初始化输入数据管理器
        
        Args:
            input_combobox: 输入表格选择下拉框
            showinput_tableWidget: 输入数据表格
        """
        self.input_combobox = input_combobox
        self.showinput_tableWidget = showinput_tableWidget
        
        # 定义不同输入类型的列配置
        self.input_configs = {
            "DGA数据": ['H2', 'CH4', 'C2H6', 'C2H4', 'C2H2'],
            "HF局部放电": ['amplitude', 'frequency', 'phase', 'pulse_count'],
            "UHF局部放电": ['amplitude', 'frequency', 'phase', 'time_difference']
        }
        
        # 输入类型名称映射（从显示名称到内部类型名称）
        self.type_mapping = {
            "DGA数据": "DGA",
            "HF局部放电": "HF",
            "UHF局部放电": "UHF"
        }
        
        # 初始化输入表格选择器
        self.init_input_combobox()
        
        # 连接信号
        self.input_combobox.currentIndexChanged.connect(self.on_input_type_changed)
        
        # 初始化输入表格
        self.update_input_table()
    
    def init_input_combobox(self):
        """初始化输入表格选择器"""
        # 清空并添加选项
        self.input_combobox.clear()
        for input_type in self.input_configs.keys():
            self.input_combobox.addItem(input_type)
    
    def update_input_table(self):
        """根据选择的输入类型更新输入表格"""
        input_type = self.get_selected_input_type()
        columns = self.input_configs.get(input_type, ['H2', 'CH4', 'C2H6', 'C2H4', 'C2H2'])
        
        # 设置表格列数和列名
        self.showinput_tableWidget.setColumnCount(len(columns))
        self.showinput_tableWidget.setHorizontalHeaderLabels(columns)
        
        # 设置表格行数
        self.showinput_tableWidget.setRowCount(1)
        
        # 为每行添加默认值
        for row in range(self.showinput_tableWidget.rowCount()):
            for col in range(self.showinput_tableWidget.columnCount()):
                item = QTableWidgetItem('0.0')
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.showinput_tableWidget.setItem(row, col, item)
        
        logger.info(f"更新输入表格为 {input_type} 类型，列: {columns}")
    
    def on_input_type_changed(self, index):
        """输入类型变化处理"""
        self.update_input_table()
    
    def get_input_data(self):
        """
        获取输入数据
        
        Returns:
            list: 输入数据列表
        """
        try:
            input_data = []
            for col in range(self.showinput_tableWidget.columnCount()):
                item = self.showinput_tableWidget.item(0, col)
                if not item or not item.text().strip():
                    return None
                try:
                    value = float(item.text().strip())
                    input_data.append(value)
                except ValueError:
                    return None
            
            logger.info(f"获取到输入数据: {input_data}")
            return input_data
        except Exception as e:
            logger.error(f"获取输入数据失败: {e}")
            return None
    
    def set_input_data(self, data):
        """
        设置输入数据
        
        Args:
            data: 输入数据列表
        """
        try:
            if len(data) != self.showinput_tableWidget.columnCount():
                logger.error(f"数据长度不匹配: {len(data)} != {self.showinput_tableWidget.columnCount()}")
                return False
            
            for col, value in enumerate(data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.showinput_tableWidget.setItem(0, col, item)
            
            logger.info(f"设置输入数据: {data}")
            return True
        except Exception as e:
            logger.error(f"设置输入数据失败: {e}")
            return False
    
    def clear_input_data(self):
        """清空输入数据"""
        for col in range(self.showinput_tableWidget.columnCount()):
            item = QTableWidgetItem('0.0')
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.showinput_tableWidget.setItem(0, col, item)
        
        logger.info("清空输入数据")
    
    def get_selected_input_type(self):
        """
        获取选择的输入类型
        
        Returns:
            str: 输入类型
        """
        display_type = self.input_combobox.currentText()
        # 将显示名称映射到内部类型名称
        internal_type = self.type_mapping.get(display_type, display_type)
        return internal_type
    
    def set_input_type(self, input_type):
        """
        设置输入类型
        
        Args:
            input_type: 输入类型
        """
        index = self.input_combobox.findText(input_type)
        if index != -1:
            self.input_combobox.setCurrentIndex(index)
            logger.info(f"设置输入类型: {input_type}")
            return True
        return False