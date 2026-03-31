"""
主程序入口
"""

import logging
import sys
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, 
    QFileDialog, QVBoxLayout, QDialog
)

from config import setup_logging, notify, ABOUT_CONTENT, HELP_CONTENT
from ui import main_ui, aboutme_ui, guide_ui
from utils import (
    UIManager, DataProcessor, ThreadManager,
    InputManager, TableManager, ModelManager, ChartContainer, PredictManager
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
        self._predictor = PredictManager(
            self, self._data, self._input, self._ui, self._thread,
            self._set_buttons_enabled, notify
        )
    
    def _connect_signals(self):
        """连接信号"""
        self.ui.pushButton.clicked.connect(self._refresh_tables)
        self.ui.btn_pca.clicked.connect(self._model.train_pca)
        self.ui.btn_rf.clicked.connect(self._model.train_rf)
        self.ui.btn_pd.clicked.connect(self._predictor.start_predict)
        self.ui.showlog_btn.clicked.connect(self._show_log)
        
        self.ui.action_6.triggered.connect(self._import_data)
        self.ui.action_7.triggered.connect(self._show_help)
        self.ui.action_8.triggered.connect(self._show_about)
        self.ui.action.triggered.connect(self._show_chart)
        
        self.ui.table_selector.currentIndexChanged.connect(self._on_table_changed)
    
    def _set_buttons_enabled(self, enabled: bool):
        """设置所有按钮的启用状态"""
        self.ui.pushButton.setEnabled(enabled)
        self.ui.btn_pca.setEnabled(enabled)
        self.ui.btn_rf.setEnabled(enabled)
        self.ui.btn_pd.setEnabled(enabled)
        self.ui.showlog_btn.setEnabled(enabled)
        self.ui.input_combobox.setEnabled(enabled)
        self.ui.table_selector.setEnabled(enabled)
    
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
    
    def _show_log(self):
        """显示日志"""
        try:
            from config.logging import get_logs_dir
            log_file = os.path.join(
                get_logs_dir(),
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
            
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择数据文件",
                "",
                "Excel文件 (*.xlsx)"
            )
            
            if not file_path:
                return
            self._ui.clear_output()
            
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
        dialog = QDialog(self)
        ui = aboutme_ui.Ui_Dialog_aboutme()
        ui.setupUi(dialog)
        dialog.setWindowTitle("关于")
        ui.textEdit.setMarkdown(ABOUT_CONTENT)
        dialog.exec()
    
    def _show_help(self):
        """显示操作说明窗口"""
        dialog = QDialog(self)
        ui = guide_ui.Ui_Dialog_guide()
        ui.setupUi(dialog)
        dialog.setWindowTitle("操作说明")
        
        # 使用内嵌的操作说明内容（打包后无需外部文件）
        ui.textEdit.setMarkdown(HELP_CONTENT)
        
        dialog.exec()
    
    def _show_chart(self):
        """显示原始图表窗口"""
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
    app.setApplicationName("TransformerFaultDiagnoser")
    notify("程序已启动")
    
    window = MainWindow()
    window.show()
    
    logger.info(f"程序启动: {datetime.now():%Y-%m-%d %H:%M:%S}")
    
    try:
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"程序异常退出: {e}")
        raise


if __name__ == "__main__":
    main()
