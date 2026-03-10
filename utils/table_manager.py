# utils/table_manager.py
"""
表格管理器：负责处理表格相关的操作
"""

import logging
from PySide6.QtWidgets import QTableWidget, QComboBox, QTableWidgetItem, QMessageBox
from PySide6.QtCore import Qt

logger = logging.getLogger(__name__)

class TableManager:
    """表格管理器"""
    
    def __init__(self, table_selector, showdata_tableWidget, data_processor):
        """
        初始化表格管理器
        
        Args:
            table_selector: 表选择器
            showdata_tableWidget: 数据显示表格
            data_processor: 数据处理器
        """
        self.table_selector = table_selector
        self.showdata_tableWidget = showdata_tableWidget
        self.data_processor = data_processor
    
    def refresh_table_list(self):
        """
        刷新表列表
        
        Returns:
            bool: 是否成功
        """
        try:
            # 清空下拉框并重新添加选项
            self.table_selector.clear()
            self.table_selector.addItem("查询数据")
            
            # 获取数据库中的所有表
            tables = self.data_processor.get_all_tables()
            for table in tables:
                self.table_selector.addItem(table)
            
            logger.info("表列表刷新成功")
            return True
        except Exception as e:
            error_msg = f"刷新表列表失败: {str(e)}"
            logger.error(error_msg)
            return False
    
    def load_table_data(self, table_name):
        """
        加载表数据
        
        Args:
            table_name: 表名
            
        Returns:
            tuple: (bool, str) 是否成功，消息
        """
        try:
            # 获取表数据
            data, columns = self.data_processor.get_table_data(table_name)
            
            # 清空表格
            self.showdata_tableWidget.setRowCount(0)
            
            if not columns:
                return False, f"表 {table_name} 不存在，请重新导入数据"
            
            if not data:
                return False, f"表 {table_name} 为空，请先导入数据"
            
            # 设置列
            self.showdata_tableWidget.setColumnCount(len(columns))
            self.showdata_tableWidget.setHorizontalHeaderLabels(columns)
            
            # 设置行
            self.showdata_tableWidget.setRowCount(len(data))
            
            # 填充数据
            for row_idx, row in enumerate(data):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.showdata_tableWidget.setItem(row_idx, col_idx, item)
            
            # 调整列宽
            self.showdata_tableWidget.resizeColumnsToContents()
            
            logger.info(f"成功加载表 {table_name} 的数据，共 {len(data)} 行")
            return True, f"成功加载表 {table_name} 的数据"
        except Exception as e:
            error_msg = f"加载表数据失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def on_table_changed(self, index):
        """
        表选择变化处理
        
        Args:
            index: 选择的索引
            
        Returns:
            tuple: (bool, str) 是否成功，消息
        """
        if index == 0:  # 选择了"查询数据"选项
            self.showdata_tableWidget.setRowCount(0)
            return True, ""
        
        table_name = self.table_selector.currentText()
        
        # 检查table_name是否为空
        if not table_name:
            logger.info("表选择器正在初始化...")
            return True, ""
        
        logger.info(f"用户选择了表: {table_name}")
        if table_name == "查询数据":
            logger.warning("无效的表名")
            return False, "无效的表名"
        
        return self.load_table_data(table_name)