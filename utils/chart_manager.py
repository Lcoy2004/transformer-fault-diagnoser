"""
图表模块 - 用于显示数据库中各表的原始数据图表
使用Qt Charts 2D图表，避免3D渲染性能问题
"""

import logging
import numpy as np
from typing import List, Dict, Tuple, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
    QLabel, QStackedWidget, QProgressDialog, QSplitter
)
from PySide6.QtCore import Qt, QSize, QPointF
from PySide6.QtCharts import QChartView, QChart, QLineSeries, QValueAxis
from PySide6.QtGui import QColor, QPen, QPainter

from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class ChartManager:
    """图表管理器 - 管理图表的创建和数据展示"""
    
    TABLE_CONFIG = {
        'pd_channel_1': {
            'name': '通道1 (PD)',
            'feature_cols': ['ch1_band1_energy', 'ch1_band2_energy', 'ch1_band3_energy',
                           'ch1_band4_energy', 'ch1_kurtosis', 'ch1_main_amp',
                           'ch1_main_freq', 'ch1_mean', 'ch1_peak', 
                           'ch1_pulse_width', 'ch1_skewness', 'ch1_var'],
            'label_col': 'fault_type',
            'type': 'auto',
            'description': '局部放电通道1特征数据'
        },
        'pd_channel_2': {
            'name': '通道2 (PD)',
            'feature_cols': ['ch2_band1_energy', 'ch2_band2_energy', 'ch2_band3_energy',
                           'ch2_band4_energy', 'ch2_kurtosis', 'ch2_main_amp',
                           'ch2_main_freq', 'ch2_mean', 'ch2_peak',
                           'ch2_pulse_width', 'ch2_skewness', 'ch2_var'],
            'label_col': 'fault_type',
            'type': 'auto',
            'description': '局部放电通道2特征数据'
        },
        'pd_channel_3': {
            'name': '通道3 (PD)',
            'feature_cols': ['ch3_band1_energy', 'ch3_band2_energy', 'ch3_band3_energy',
                           'ch3_band4_energy', 'ch3_kurtosis', 'ch3_main_amp',
                           'ch3_main_freq', 'ch3_mean', 'ch3_peak',
                           'ch3_pulse_width', 'ch3_skewness', 'ch3_var'],
            'label_col': 'fault_type',
            'type': 'auto',
            'description': '局部放电通道3特征数据'
        },
        'pd_channel_4': {
            'name': '通道4 (PD)',
            'feature_cols': ['ch4_band1_energy', 'ch4_band2_energy', 'ch4_band3_energy',
                           'ch4_band4_energy', 'ch4_kurtosis', 'ch4_main_amp',
                           'ch4_main_freq', 'ch4_mean', 'ch4_peak',
                           'ch4_pulse_width', 'ch4_skewness', 'ch4_var'],
            'label_col': 'fault_type',
            'type': 'auto',
            'description': '局部放电通道4特征数据'
        }
    }
    
    FAULT_COLORS = {
        '正常': (0.2, 0.8, 0.2, 1.0),
        '过热': (1.0, 0.5, 0.0, 1.0),
        '放电': (0.8, 0.2, 0.2, 1.0),
        '电弧放电': (1.0, 0.0, 0.0, 1.0),
        '火花放电': (1.0, 0.5, 0.0, 1.0),
        '局部放电': (0.8, 0.4, 0.8, 1.0),
        'default': (0.3, 0.3, 0.8, 1.0)
    }
    
    def __init__(self, db_path: str = 'database/fault_data.db'):
        self.db = DatabaseManager(db_path)
        self._current_data = None
        self._current_table = None
    
    def get_available_tables(self) -> List[Tuple[str, str]]:
        """获取可用的图表表列表"""
        tables = []
        all_tables = self.db.get_all_tables()
        
        for table_name, config in self.TABLE_CONFIG.items():
            if table_name in all_tables:
                tables.append((table_name, config['name']))
        
        return tables
    
    def load_table_data(self, table_name: str) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        加载表数据
        
        Returns:
            (特征数据, 标签数据, 特征列名)
        """
        if table_name not in self.TABLE_CONFIG:
            raise ValueError(f"[错误] 未知表: {table_name}")
        
        config = self.TABLE_CONFIG[table_name]
        data, columns = self.db.get_table_data(table_name)
        
        if not data:
            raise ValueError(f"[错误] 表 {table_name} 无数据")
        
        col_idx = {col: idx for idx, col in enumerate(columns)}
        
        feature_cols = config['feature_cols']
        label_col = config['label_col']
        
        valid_cols = [c for c in feature_cols if c in col_idx]
        
        X = []
        y = []
        for row in data:
            features = [row[col_idx[c]] for c in valid_cols]
            if all(v is not None for v in features):
                X.append(features)
                if label_col in col_idx:
                    y.append(row[col_idx[label_col]] or '未知')
                else:
                    y.append('未知')
        
        self._current_data = (np.array(X), np.array(y), valid_cols)
        self._current_table = table_name
        
        logger.info(f"[加载] {table_name}: {len(X)} 样本, {len(valid_cols)} 特征")
        
        return self._current_data
    
    def get_colors_for_labels(self, labels: np.ndarray) -> np.ndarray:
        """根据标签获取颜色"""
        colors = np.zeros((len(labels), 4))
        
        for i, label in enumerate(labels):
            color = self.FAULT_COLORS.get(label, self.FAULT_COLORS['default'])
            colors[i] = color
        
        return colors


class ChartContainer(QWidget):
    """图表容器窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._init_chart_manager()
    
    def _init_ui(self):
        self.setMinimumSize(900, 700)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        selector_layout = QHBoxLayout()
        
        selector_label = QLabel("选择数据表：")
        self.table_selector = QComboBox()
        self.table_selector.setMinimumWidth(200)
        
        feature_label = QLabel("选择特征：")
        self.feature_selector = QComboBox()
        self.feature_selector.setMinimumWidth(150)
        
        selector_layout.addWidget(selector_label)
        selector_layout.addWidget(self.table_selector)
        selector_layout.addSpacing(20)
        selector_layout.addWidget(feature_label)
        selector_layout.addWidget(self.feature_selector)
        selector_layout.addStretch()
        
        main_layout.addLayout(selector_layout)
        
        self.info_label = QLabel("请选择数据表查看图表")
        self.info_label.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        main_layout.addWidget(self.info_label)
        
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, 1)
        
        self.legend_widget = QWidget()
        self.legend_layout = QHBoxLayout(self.legend_widget)
        self.legend_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.addWidget(self.legend_widget)
    
    def _init_chart_manager(self):
        """初始化图表管理器"""
        self.chart_manager = ChartManager()
        self._refresh_tables()
        
        self.table_selector.currentIndexChanged.connect(self._on_table_changed)
        self.feature_selector.currentIndexChanged.connect(self._on_feature_changed)
    
    def _refresh_tables(self):
        """刷新表列表"""
        self.table_selector.clear()
        tables = self.chart_manager.get_available_tables()
        
        for table_name, display_name in tables:
            self.table_selector.addItem(display_name, table_name)
        
        if tables:
            self._on_table_changed(0)
    
    def _refresh_features(self, table_name: str):
        """刷新特征列表"""
        self.feature_selector.clear()
        
        if table_name in self.chart_manager.TABLE_CONFIG:
            feature_cols = self.chart_manager.TABLE_CONFIG[table_name]['feature_cols']
            
            for i, feature in enumerate(feature_cols):
                self.feature_selector.addItem(feature, i)
            
            if feature_cols:
                self._on_feature_changed(0)
    
    def _on_table_changed(self, index: int):
        """表选择变化"""
        if index < 0:
            return
        
        table_name = self.table_selector.currentData()
        if not table_name:
            return
        
        try:
            X, y, feature_names = self.chart_manager.load_table_data(table_name)
            
            config = self.chart_manager.TABLE_CONFIG[table_name]
            self.info_label.setText(
                f"数据表: {config['description']} | "
                f"样本数: {len(X)} | 特征数: {X.shape[1]}"
            )
            
            self._refresh_features(table_name)
            
        except Exception as e:
            logger.error(f"[图表加载失败] {e}")
            self.info_label.setText(f"加载失败: {e}")
    
    def _on_feature_changed(self, index: int):
        """特征选择变化"""
        if index < 0:
            return
        
        self._display_current_chart()
    
    def _clear_stacked_widget(self):
        """清空堆叠控件"""
        while self.stacked_widget.count():
            widget = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget)
            if widget:
                widget.deleteLater()
    
    def _clear_legend(self):
        """清空图例"""
        while self.legend_layout.count():
            item = self.legend_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _display_current_chart(self):
        """显示当前选中特征的数据分布"""
        if not self.chart_manager._current_data:
            return
        
        X, y, feature_names = self.chart_manager._current_data
        table_name = self.chart_manager._current_table
        feature_index = self.feature_selector.currentData()
        
        if feature_index is None or feature_index < 0:
            return
        
        self._clear_stacked_widget()
        self._clear_legend()
        
        try:
            feature_name = feature_names[feature_index]
            feature_data = X[:, feature_index]
            
            self._display_feature_distribution(feature_data, y, feature_name)
            
        except Exception as e:
            logger.error(f"[图表显示失败] {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def _display_feature_distribution(self, feature_data: np.ndarray, y: np.ndarray, feature_name: str):
        """显示特征数据分布"""
        chart = QChart()
        chart.setTitle(f"特征分布: {feature_name}")
        chart.setAnimationOptions(QChart.NoAnimation)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        
        axis_x = QValueAxis()
        axis_x.setTitleText("样本索引")
        
        axis_y = QValueAxis()
        axis_y.setTitleText("特征值")
        
        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)
        
        colors = [
            QColor(0, 114, 189),    # 蓝色
            QColor(217, 83, 25),    # 橙色
            QColor(237, 177, 32),   # 黄色
            QColor(126, 47, 142),   # 紫色
            QColor(32, 134, 48),    # 绿色
        ]
        
        # 按故障类型分组
        unique_faults = set(y)
        fault_list = list(unique_faults)
        
        for i, fault_type in enumerate(fault_list):
            series = QLineSeries()
            series.setName(fault_type)
            
            pen = QPen(colors[i % len(colors)])
            pen.setWidth(1)
            series.setPen(pen)
            
            # 获取该故障类型的样本索引和特征值
            indices = [j for j, label in enumerate(y) if label == fault_type]
            values = [feature_data[j] for j in indices]
            
            # 添加数据点
            for idx, val in enumerate(indices):
                series.append(QPointF(float(idx), float(values[idx])))
            
            chart.addSeries(series)
            series.attachAxis(axis_x)
            series.attachAxis(axis_y)
        
        # 设置坐标轴范围
        if len(feature_data) > 0:
            axis_x.setRange(0, len(feature_data) - 1)
            y_min, y_max = feature_data.min(), feature_data.max()
            margin = (y_max - y_min) * 0.1
            axis_y.setRange(y_min - margin, y_max + margin)
        
        chart_view = QChartView()
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setChart(chart)
        
        self.stacked_widget.addWidget(chart_view)
        self.stacked_widget.setCurrentWidget(chart_view)
