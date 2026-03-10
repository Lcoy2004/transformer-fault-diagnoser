# main.py
"""
主程序入口
"""

import logging
import sys
import os
from datetime import datetime
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QTableWidgetItem
from PySide6.QtCore import Qt
from config import setup_logging, notify, get_notification
from ui import main_ui
from utils.ui_manager import UIManager
from utils.data_processor import DataProcessor
from utils.thread_manager import ThreadManager
from utils.input_manager import InputManager
from utils.table_manager import TableManager
from utils.model_manager import ModelManager

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        # 初始化UI
        self.ui = main_ui.Ui_MainWindow()
        self.ui.setupUi(self)
        
        # 初始化管理器
        self.data_processor = DataProcessor()
        self.ui_manager = UIManager(self)
        self.thread_manager = ThreadManager()
        self.input_manager = InputManager(self.ui.input_combobox, self.ui.showinput_tableWidget)
        self.table_manager = TableManager(self.ui.table_selector, self.ui.showdata_tableWidget, self.data_processor)
        self.model_manager = ModelManager(self.data_processor, self.ui_manager, self.thread_manager)
        
        # 初始化控件
        self.init_widgets()
        
        # 连接信号和槽
        self.connect_signals()
        
        # 初始化表选择器
        self.refresh_table_list()
    
    def init_widgets(self):
        """初始化控件"""
        # 设置进度条初始值
        self.ui.progressBar.setValue(0)
        
        # 设置表格
        self.init_tables()
    
    def init_tables(self):
        """初始化表格"""
        # 数据显示表格
        self.ui.showdata_tableWidget.setColumnCount(5)
        self.ui.showdata_tableWidget.setHorizontalHeaderLabels(['H2', 'CH4', 'C2H6', 'C2H4', 'C2H2'])
        
        # 输入数据表格
        self.ui.showinput_tableWidget.setColumnCount(5)
        self.ui.showinput_tableWidget.setHorizontalHeaderLabels(['H2', 'CH4', 'C2H6', 'C2H4', 'C2H2'])
        # 设置输入表格为1行
        self.ui.showinput_tableWidget.setRowCount(1)
    
    def connect_signals(self):
        """连接信号和槽"""
        # 按钮信号
        self.ui.pushButton.clicked.connect(self.refresh_table_list)
        self.ui.btn_pca.clicked.connect(self.train_pca)
        self.ui.btn_rf.clicked.connect(self.train_model)
        self.ui.btn_pd.clicked.connect(self.predict)
        self.ui.showlog_btn.clicked.connect(self.show_log)
        
        # 菜单项信号
        self.ui.action_6.triggered.connect(self.import_data)
        
        # 表选择器信号
        self.ui.table_selector.currentIndexChanged.connect(self.on_table_changed)
    
    def refresh_table_list(self):
        """刷新表列表"""
        try:
            success = self.table_manager.refresh_table_list()
            if success:
                notify("表列表刷新成功")
            else:
                notify("刷新表列表失败")
        except Exception as e:
            error_msg = f"刷新表列表失败: {str(e)}"
            notify(error_msg)
            logger.error(error_msg)
    
    def on_table_changed(self, index):
        """表选择变化处理"""
        try:
            success, message = self.table_manager.on_table_changed(index)
            if message:
                if success:
                    notify(message)
                else:
                    QMessageBox.warning(self, "错误", message)
        except Exception as e:
            error_msg = f"表选择变化处理失败: {str(e)}"
            notify(error_msg)
            logger.error(error_msg)
    
    def train_pca(self):
        """训练PCA模型"""
        self.model_manager.train_pca()
    
    def train_model(self):
        """训练随机森林模型"""
        self.model_manager.train_model()
    
    def predict(self):
        """预测故障"""
        try:
            # 获取输入数据
            input_data = self.input_manager.get_input_data()
            if input_data is None:
                QMessageBox.warning(self, "错误", "请填写所有输入数据，并且确保数据格式正确")
                return
            
            # 获取当前选择的输入类型
            input_type = self.input_manager.get_selected_input_type()
            
            # 将输入类型转换为数据类型
            data_type_map = {
                "DGA": "DGA",
                "HF": "HF",
                "UHF": "UHF"
            }
            data_type = data_type_map.get(input_type or "DGA", "DGA")
            
            # 开始预测
            fault_type, fault_location = self.data_processor.predict(input_data, data_type)
            
            # 显示结果
            self.ui_manager.clear_output()
            self.ui_manager.update_output(f"预测结果：")
            self.ui_manager.update_output(f"故障类型: {fault_type}")
            self.ui_manager.update_output(f"故障位置: {fault_location}")
            
            notify("预测完成")
        except Exception as e:
            error_msg = f"预测失败: {str(e)}"
            notify(error_msg)
            logger.error(error_msg)
            QMessageBox.warning(self, "错误", error_msg)
    
    def show_log(self):
        """显示日志"""
        try:
            # 构建日志文件路径
            log_file = os.path.join(os.path.dirname(__file__), "logs", datetime.now().strftime("%Y%m%d") + ".log")
            
            # 检查文件是否存在
            if not os.path.exists(log_file):
                QMessageBox.information(self, "提示", "日志文件不存在")
                return
            
            # 打开日志文件
            os.startfile(log_file)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"打开日志文件失败: {str(e)}")
            logger.error(f"打开日志文件失败: {e}")
    
    def on_error(self, error_msg):
        """错误处理"""
        notify(f"错误: {error_msg}")
        logger.error(error_msg)
        QMessageBox.warning(self, "错误", error_msg)
    
    def import_data(self):
        """导入数据"""
        try:
            # 获取当前选择的表
            current_index = self.ui.table_selector.currentIndex()
            table_name = None
            
            if current_index > 0:  # 用户选择了具体的表
                table_name = self.ui.table_selector.currentText()
                logger.info(f"用户选择的表: {table_name}")
            
            # 打开文件选择对话框
            file_dialog = QFileDialog()
            file_dialog.setWindowTitle("选择数据文件")
            file_dialog.setNameFilter("Excel文件 (*.xlsx)")
            file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
            
            if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
                file_path = file_dialog.selectedFiles()[0]
                
                # 清空输出
                self.ui_manager.clear_output()
                
                # 开始导入
                worker = self.thread_manager.start_task(
                    self.data_processor.import_data,
                    file_path,
                    table_name
                )
                
                # 连接信号
                worker.progress.connect(self.ui_manager.update_output)
                worker.progress_value.connect(self.ui_manager.update_progress)
                worker.finished.connect(self.on_import_finished)
                worker.error.connect(self.on_error)
                
                # 启动线程
                worker.start()
        except Exception as e:
            error_msg = f"打开文件选择对话框失败: {str(e)}"
            notify(error_msg)
            logger.error(error_msg)
            QMessageBox.warning(self, "错误", error_msg)
    
    def on_import_finished(self, result):
        """数据导入完成处理"""
        self.ui_manager.update_output(f"数据导入完成，导入了 {result} 条记录")
        notify(f"数据导入完成，导入了 {result} 条记录")
        # 刷新表列表
        self.refresh_table_list()

if __name__ == "__main__":
    setup_logging()  # 配置日志系统
    app = QApplication(sys.argv)
    # 发送启动通知
    notify("程序已启动")
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    logger.info("++=============窗口初始化完成，最近启动时间：%s=============++", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))    
    sys.exit(app.exec())
