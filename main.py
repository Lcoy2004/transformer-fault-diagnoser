"""
主程序入口
"""

import logging
import sys
import os
from datetime import datetime
from typing import Optional
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QVBoxLayout
from PySide6.QtCore import Qt

from config import setup_logging, notify
from ui import main_ui, aboutme_ui
from utils import (
    UIManager, DataProcessor, ThreadManager,
    InputManager, TableManager, ModelManager, ChartContainer
)

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._init_managers()
        self._connect_signals()
        self._refresh_tables()
    
    def _init_ui(self):
        """初始化 UI"""
        self.ui = main_ui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.progressBar.setValue(0)
    
    def _init_managers(self):
        """初始化管理器"""
        self._data = DataProcessor()
        self._ui = UIManager(self)
        self._thread = ThreadManager()
        self._input = InputManager(
            self.ui.input_combobox,
            self.ui.showinput_tableWidget
        )
        self._table = TableManager(
            self.ui.table_selector,
            self.ui.showdata_tableWidget,
            self._data
        )
        self._model = ModelManager(self._data, self._ui, self._thread)
    
    def _connect_signals(self):
        """连接信号"""
        # 按钮
        self.ui.pushButton.clicked.connect(self._refresh_tables)
        self.ui.btn_pca.clicked.connect(self._model.train_pca)
        self.ui.btn_rf.clicked.connect(self._model.train_rf)
        self.ui.btn_pd.clicked.connect(self._predict)
        self.ui.showlog_btn.clicked.connect(self._show_log)
        
        # 菜单
        self.ui.action_6.triggered.connect(self._import_data)
        self.ui.action_8.triggered.connect(self._show_about)
        self.ui.action.triggered.connect(self._show_chart)
        
        # 选择器
        self.ui.table_selector.currentIndexChanged.connect(self._on_table_changed)
    
    def _refresh_tables(self):
        """刷新表列表"""
        try:
            if self._table.refresh():
                notify("表列表刷新成功")
            else:
                notify("刷新表列表失败")
        except Exception as e:
            logger.error(f"刷新表列表失败: {e}")
            notify(f"刷新失败: {e}")
    
    def _on_table_changed(self, index: int):
        """表选择变化"""
        try:
            success, msg = self._table.on_changed(index)
            if msg:
                if success:
                    notify(msg)
                else:
                    QMessageBox.warning(self, "提示", msg)
        except Exception as e:
            logger.error(f"表选择变化处理失败: {e}")
    
    def _predict(self):
        """预测故障"""
        try:
            input_data = self._input.get_data()
            if input_data is None:
                QMessageBox.warning(self, "错误", "请填写所有输入数据")
                return
            
            data_type = self._input.get_type()
            fault_type, fault_location = self._data.predict(input_data, data_type)
            
            self._ui.clear_output()
            self._ui.update_output(f"预测结果：")
            self._ui.update_output(f"故障类型: {fault_type}")
            self._ui.update_output(f"故障位置: {fault_location}")
            
            notify("预测完成")
        except Exception as e:
            logger.error(f"预测失败: {e}")
            QMessageBox.warning(self, "错误", f"预测失败: {e}")
    
    def _show_log(self):
        """显示日志"""
        try:
            log_file = os.path.join(
                os.path.dirname(__file__),
                "logs",
                f"{datetime.now():%Y%m%d}.log"
            )
            
            if not os.path.exists(log_file):
                QMessageBox.information(self, "提示", "日志文件不存在")
                return
            
            os.startfile(log_file)
        except Exception as e:
            logger.error(f"打开日志失败: {e}")
            QMessageBox.warning(self, "错误", f"打开日志失败: {e}")
    
    def _import_data(self):
        """导入数据"""
        try:
            table_name = self._table.get_current_table()
            
            # 选择文件
            dialog = QFileDialog(self)
            dialog.setWindowTitle("选择数据文件")
            dialog.setNameFilter("Excel文件 (*.xlsx)")
            dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
            
            if dialog.exec() != QFileDialog.DialogCode.Accepted:
                return
            
            file_path = dialog.selectedFiles()[0]
            
            self._ui.clear_output()
            
            # 启动导入任务
            worker = self._thread.start(self._data.import_data, file_path, table_name)
            worker.progress.connect(self._ui.update_output)
            worker.progress_value.connect(self._ui.update_progress)
            worker.finished.connect(self._on_import_done)
            worker.error.connect(lambda msg: QMessageBox.warning(self, "错误", msg))
            worker.start()
            
        except Exception as e:
            logger.error(f"导入数据失败: {e}")
            QMessageBox.warning(self, "错误", f"导入失败: {e}")
    
    def _on_import_done(self, result: int):
        """导入完成"""
        self._ui.update_output(f"导入完成: {result} 条记录")
        notify(f"导入完成: {result} 条记录")
        self._refresh_tables()
    
    def _show_about(self):
        """显示关于窗口"""
        from PySide6.QtWidgets import QDialog
        
        dialog = QDialog(self)
        ui = aboutme_ui.Ui_Dialog_aboutme()
        ui.setupUi(dialog)
        
        # 设置窗口标题
        dialog.setWindowTitle("关于")
        
        # 添加Markdown内容
        about_content = """
## 本科毕业设计
---
### 基于多源监测数据的电力变压器故障智能诊断系统
---

**UNIVERSITY_NAME COLLEGE_NAME**  
**学生**：AUTHOR_NAME（GRADE_INFO）  
**项目地址**：[https://gitee.com/lcoy/transformer-fault-diagnoser](https://gitee.com/lcoy/transformer-fault-diagnoser)


"""
        
        # 设置文本内容
        ui.textEdit.setMarkdown(about_content)
        
        # 显示窗口
        dialog.exec()
    
    def _show_chart(self):
        """显示原始图表窗口"""
        from PySide6.QtWidgets import QDialog
        
        dialog = QDialog(self)
        dialog.setWindowTitle("原始数据显示图")
        dialog.resize(900, 700)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)
        
        chart_container = ChartContainer(dialog)
        layout.addWidget(chart_container)
        
        dialog.exec()



def main():
    """主函数"""
    setup_logging()
    
    app = QApplication(sys.argv)
    notify("程序已启动")
    
    window = MainWindow()
    window.show()
    
    logger.info(f"程序启动: {datetime.now():%Y-%m-%d %H:%M:%S}")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
