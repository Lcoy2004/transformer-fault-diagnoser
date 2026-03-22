"""
图表模块 - 用于显示数据库中各表的原始数据图表

支持功能：
1. 多数据表切换（DGA + 四个PD通道）
2. 特征选择显示（中文描述 + 单位）
3. 按故障类型分类显示
4. 数据统计信息
5. 鼠标悬停显示数据点详情（跟随鼠标）
"""

import logging
import numpy as np
from typing import List, Tuple, Dict, Optional
from PySide6.QtCore import Qt, QPointF, QPoint
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QGroupBox, QTableWidget, QTableWidgetItem
from PySide6.QtCharts import QChartView, QChart, QLineSeries, QScatterSeries, QValueAxis
from PySide6.QtGui import QColor, QPen, QPainter, QFont, QMouseEvent

from database.db_manager import DatabaseManager
from config.constants import TABLE_CONFIGS, PD_DB_TABLES

logger = logging.getLogger(__name__)

FEATURE_NAME_MAP: Dict[str, str] = {
    'h2': '氢气(H₂)',
    'ch4': '甲烷(CH₄)',
    'c2h6': '乙烷(C₂H₆)',
    'c2h4': '乙烯(C₂H₄)',
    'c2h2': '乙炔(C₂H₂)',
    'band1_energy': '频段1能量',
    'band2_energy': '频段2能量',
    'band3_energy': '频段3能量',
    'band4_energy': '频段4能量',
    'kurtosis': '峭度',
    'main_amp': '主频幅值',
    'main_freq': '主频率',
    'mean': '均值',
    'peak': '峰值',
    'pulse_width': '脉冲宽度',
    'skewness': '偏度',
    'var': '方差'
}

FEATURE_UNIT_MAP: Dict[str, str] = {
    'h2': 'μL/L', 'ch4': 'μL/L', 'c2h6': 'μL/L', 'c2h4': 'μL/L', 'c2h2': 'μL/L',
    'band1_energy': 'pJ', 'band2_energy': 'pJ', 'band3_energy': 'pJ', 'band4_energy': 'pJ',
    'kurtosis': '', 'main_amp': 'mV', 'main_freq': 'kHz', 'mean': 'mV',
    'peak': 'mV', 'pulse_width': 'μs', 'skewness': '', 'var': 'mV²'
}

FAULT_COLORS: List[QColor] = [
    QColor(30, 136, 229), QColor(229, 57, 53), QColor(255, 152, 0),
    QColor(67, 160, 71), QColor(124, 77, 255), QColor(255, 112, 67),
    QColor(0, 172, 193), QColor(142, 36, 170),
]


class HoverLabel(QWidget):
    """浮动在鼠标旁边的提示框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setStyleSheet("""
            background-color: rgb(40, 40, 40);
            border: 1px solid rgb(80, 80, 80);
            border-radius: 6px;
            padding: 8px 12px;
        """)
        self._label = QLabel(self)
        self._label.setFont(QFont("Microsoft YaHei", 9))
        self._label.setStyleSheet("color: white; background: transparent;")
        self._label.setAlignment(Qt.AlignLeft)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.addWidget(self._label)

    def show_at(self, text: str, global_pos: QPoint):
        """在指定全局位置显示"""
        self._label.setText(text)
        self.adjustSize()

        x_offset, y_offset = 18, 18
        new_x = global_pos.x() + x_offset
        new_y = global_pos.y() + y_offset

        self.setGeometry(new_x, new_y, self.width(), self.height())
        self.show()

    def hide_me(self):
        """隐藏"""
        self.hide()


class ChartViewHover(QChartView):
    """支持鼠标悬停显示数据点的图表视图"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self._series_data: Dict[str, Tuple[List[int], np.ndarray]] = {}
        self._hover_label: Optional[HoverLabel] = None

    def _ensure_hover_label(self) -> HoverLabel:
        if self._hover_label is None:
            self._hover_label = HoverLabel(self)
        return self._hover_label

    def set_series_data(self, series_name: str, indices: List[int], values: np.ndarray):
        self._series_data[series_name] = (indices, values)

    def clear_series_data(self):
        self._series_data.clear()

    def _find_nearest_point(self, chart_pos: QPointF) -> Tuple[Optional[str], Optional[int], Optional[float]]:
        if not self._series_data:
            return None, None, None

        min_dist = float('inf')
        nearest = None, None, None

        for series_name, (indices, values) in self._series_data.items():
            for i, idx in enumerate(indices):
                if i >= len(values):
                    continue
                px, py = float(idx), float(values[i])
                dist = ((chart_pos.x() - px) ** 2 + (chart_pos.y() - py) ** 2) ** 0.5
                if dist < min_dist:
                    min_dist = dist
                    nearest = series_name, idx, py

        threshold = 30
        if min_dist > threshold:
            return None, None, None
        return nearest

    def mouseMoveEvent(self, event: QMouseEvent):
        super().mouseMoveEvent(event)
        if self.chart() is None:
            return

        chart_pos = self.chart().mapToValue(event.pos())
        series_name, idx, value = self._find_nearest_point(chart_pos)

        if idx is not None:
            title = self.chart().title().replace(' 分布', '')
            unit = ''
            for key, val in FEATURE_UNIT_MAP.items():
                if key in title.lower().replace(' ', '').replace('_', ''):
                    unit = val
                    break
            if unit:
                text = f"<b>样本 #{idx}</b><br/>{title}: <b>{value:.4f}</b> {unit}<br/>类型: {series_name}"
            else:
                text = f"<b>样本 #{idx}</b><br/>{title}: <b>{value:.4f}</b><br/>类型: {series_name}"

            global_pos = event.globalPosition().toPoint()
            self._ensure_hover_label().show_at(text, global_pos)
            self.viewport().setCursor(Qt.PointingHandCursor)
        else:
            if self._hover_label:
                self._hover_label.hide_me()
            self.viewport().setCursor(Qt.ArrowCursor)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        if self._hover_label:
            self._hover_label.hide_me()


class ChartManager:
    def __init__(self, db_path: str = 'database/fault_data.db'):
        self.db = DatabaseManager(db_path)
        self._current_data: Optional[Tuple[np.ndarray, np.ndarray, List[str]]] = None

    def get_available_tables(self) -> List[Tuple[str, str]]:
        tables = []
        all_tables = self.db.get_all_tables()
        for table_name in PD_DB_TABLES:
            if table_name in all_tables:
                config = TABLE_CONFIGS.get(table_name)
                if config:
                    tables.append((table_name, config['name']))
        if 'oil_chromatography' in all_tables:
            config = TABLE_CONFIGS.get('oil_chromatography')
            if config:
                tables.insert(0, ('oil_chromatography', config['name']))
        return tables

    def load_table_data(self, table_name: str) -> Tuple[np.ndarray, np.ndarray, List[str], Dict]:
        if table_name not in TABLE_CONFIGS:
            raise ValueError(f"[错误] 未知表: {table_name}")
        config = TABLE_CONFIGS[table_name]
        data, columns = self.db.get_table_data(table_name)
        if not data:
            raise ValueError(f"[错误] 表 {table_name} 无数据")

        col_idx = {col: idx for idx, col in enumerate(columns)}
        feature_cols = config['features']
        label_col = config['label_col']
        valid_cols = [c for c in feature_cols if c in col_idx]

        X, y = [], []
        for row in data:
            features = [row[col_idx[c]] for c in valid_cols]
            if all(v is not None for v in features):
                X.append(features)
                y.append(row[col_idx[label_col]] if label_col in col_idx else '未知')

        X, y = np.array(X), np.array(y)
        fault_stats = {}
        for ft in np.unique(y):
            mask = y == ft
            fault_stats[ft] = {'count': int(np.sum(mask)), 'percentage': float(np.sum(mask)) / len(y) * 100}

        self._current_data = (X, y, valid_cols, fault_stats)
        logger.info(f"[加载] {table_name}: {len(X)} 样本, {len(valid_cols)} 特征")
        return self._current_data

    def get_feature_display_name(self, col_name: str) -> str:
        base = col_name.split('_', 1)[-1] if '_' in col_name else col_name
        return FEATURE_NAME_MAP.get(base.lower(), base)

    def get_feature_unit(self, col_name: str) -> str:
        base = col_name.split('_', 1)[-1] if '_' in col_name else col_name
        return FEATURE_UNIT_MAP.get(base.lower(), '')

    def get_y_axis_title(self, col_name: str) -> str:
        name = self.get_feature_display_name(col_name)
        unit = self.get_feature_unit(col_name)
        return f"{name} ({unit})" if unit else name


class ChartContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        self.setMinimumSize(1000, 750)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        selector_layout = QHBoxLayout()
        self.table_label = QLabel("数据表：")
        self.table_label.setFont(QFont("Microsoft YaHei", 10))
        self.table_selector = QComboBox()
        self.table_selector.setFont(QFont("Microsoft YaHei", 10))
        self.table_selector.setMinimumWidth(180)

        self.feature_label = QLabel("特征：")
        self.feature_label.setFont(QFont("Microsoft YaHei", 10))
        self.feature_selector = QComboBox()
        self.feature_selector.setFont(QFont("Microsoft YaHei", 10))
        self.feature_selector.setMinimumWidth(160)

        self.chart_type_label = QLabel("图表类型：")
        self.chart_type_label.setFont(QFont("Microsoft YaHei", 10))
        self.chart_type_selector = QComboBox()
        self.chart_type_selector.setFont(QFont("Microsoft YaHei", 10))
        self.chart_type_selector.addItems(["折线图", "散点图"])
        self.chart_type_selector.setMinimumWidth(100)

        selector_layout.addWidget(self.table_label)
        selector_layout.addWidget(self.table_selector)
        selector_layout.addSpacing(20)
        selector_layout.addWidget(self.feature_label)
        selector_layout.addWidget(self.feature_selector)
        selector_layout.addSpacing(20)
        selector_layout.addWidget(self.chart_type_label)
        selector_layout.addWidget(self.chart_type_selector)
        selector_layout.addStretch()
        main_layout.addLayout(selector_layout)

        info_layout = QHBoxLayout()
        self.info_label = QLabel("请选择数据表查看图表 | 鼠标悬停查看数据点详情")
        self.info_label.setFont(QFont("Microsoft YaHei", 10))
        self.info_label.setStyleSheet("color: #546e7a; padding: 4px;")
        info_layout.addWidget(self.info_label)
        info_layout.addStretch()
        main_layout.addLayout(info_layout)

        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(15)

        self.chart_area = ChartViewHover()
        self.chart_area.setMinimumSize(650, 500)
        self.chart_area.setRenderHint(QPainter.Antialiasing)
        self.chart_area.setStyleSheet("border: 1px solid #cfd8dc; border-radius: 8px; background-color: white;")
        content_layout.addWidget(self.chart_area, 1)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        self.stats_widget = QGroupBox("故障统计")
        self.stats_widget.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Bold))
        stats_layout = QVBoxLayout(self.stats_widget)

        self.stats_table = QTableWidget()
        self.stats_table.setFont(QFont("Microsoft YaHei", 9))
        self.stats_table.setColumnCount(3)
        self.stats_table.setHorizontalHeaderLabels(["故障类型", "数量", "占比"])
        self.stats_table.horizontalHeader().setStretchLastSection(True)
        self.stats_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.stats_table.setAlternatingRowColors(True)
        stats_layout.addWidget(self.stats_table)

        self.fault_dist_label = QLabel()
        self.fault_dist_label.setFont(QFont("Microsoft YaHei", 9))
        self.fault_dist_label.setWordWrap(True)
        self.fault_dist_label.setStyleSheet("color: #455a64; padding: 5px; background: #f5f7f9; border-radius: 4px;")
        stats_layout.addWidget(self.fault_dist_label)
        stats_layout.addStretch()
        right_layout.addWidget(self.stats_widget, 1)

        self.hover_hint_label = QLabel("💡 提示：鼠标移动到图表上的数据点查看详情")
        self.hover_hint_label.setFont(QFont("Microsoft YaHei", 9))
        self.hover_hint_label.setWordWrap(True)
        self.hover_hint_label.setStyleSheet("color: #ff7043; padding: 8px; background: #fff3e0; border-radius: 6px; border: 1px solid #ffcc80;")
        right_layout.addWidget(self.hover_hint_label)

        content_layout.addWidget(right_panel, 0)
        main_layout.addWidget(content_widget, 1)

        self.legend_widget = QWidget()
        self.legend_widget.setMaximumHeight(40)
        self.legend_layout = QHBoxLayout(self.legend_widget)
        self.legend_layout.setAlignment(Qt.AlignCenter)
        self.legend_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.addWidget(self.legend_widget)

        self._init_chart_manager()
        self.table_selector.currentIndexChanged.connect(self._on_table_changed)
        self.feature_selector.currentIndexChanged.connect(self._on_feature_changed)
        self.chart_type_selector.currentIndexChanged.connect(self._on_feature_changed)

    def _init_chart_manager(self):
        self.chart_manager = ChartManager()
        self._refresh_tables()

    def _refresh_tables(self):
        self.table_selector.clear()
        tables = self.chart_manager.get_available_tables()
        for table_name, display_name in tables:
            self.table_selector.addItem(display_name, table_name)
        if tables:
            self._on_table_changed(0)

    def _refresh_features(self, table_name: str):
        self.feature_selector.clear()
        if table_name in TABLE_CONFIGS:
            config = TABLE_CONFIGS[table_name]
            for col_name in config['features']:
                display = self.chart_manager.get_feature_display_name(col_name)
                unit = self.chart_manager.get_feature_unit(col_name)
                text = f"{display} ({unit})" if unit else display
                self.feature_selector.addItem(text, col_name)
            if config['features']:
                self._on_feature_changed(0)

    def _update_stats(self, fault_stats: Dict):
        self.stats_table.setRowCount(len(fault_stats))
        for i, (ft, stats) in enumerate(fault_stats.items()):
            self.stats_table.setItem(i, 0, QTableWidgetItem(ft))
            self.stats_table.setItem(i, 1, QTableWidgetItem(str(stats['count'])))
            self.stats_table.setItem(i, 2, QTableWidgetItem(f"{stats['percentage']:.1f}%"))
        self.stats_table.resizeColumnsToContents()

        dist = "故障分布：\n"
        for ft, stats in sorted(fault_stats.items(), key=lambda x: x[1]['count'], reverse=True):
            dist += f"• {ft}: {stats['count']}个({stats['percentage']:.1f}%)\n"
        self.fault_dist_label.setText(dist.strip())

    def _on_table_changed(self, index: int):
        if index < 0:
            return
        table_name = self.table_selector.currentData()
        if not table_name:
            return
        try:
            X, y, feature_names, fault_stats = self.chart_manager.load_table_data(table_name)
            config = TABLE_CONFIGS[table_name]
            self.info_label.setText(f"表: {config['name']} | 样本数: {len(X)} | 特征数: {len(feature_names)} | 故障类型: {len(fault_stats)}种")
            self._update_stats(fault_stats)
            self._refresh_features(table_name)
        except Exception as e:
            logger.error(f"[图表加载失败] {e}")
            self.info_label.setText(f"加载失败: {e}")

    def _on_feature_changed(self, index: int):
        if index < 0:
            return
        self._display_current_chart()

    def _clear_legend(self):
        while self.legend_layout.count():
            item = self.legend_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _display_current_chart(self):
        if not self.chart_manager._current_data:
            return
        X, y, feature_names, fault_stats = self.chart_manager._current_data
        col_name = self.feature_selector.currentData()
        if not col_name:
            return
        try:
            col_idx = feature_names.index(col_name)
            feature_data = X[:, col_idx]
            y_axis_title = self.chart_manager.get_y_axis_title(col_name)
            chart_type = self.chart_type_selector.currentText()

            self._clear_legend()
            self.chart_area.clear_series_data()

            if chart_type == "折线图":
                self._display_line_chart(feature_data, y, y_axis_title, col_name)
            else:
                self._display_scatter_chart(feature_data, y, y_axis_title, col_name)
        except Exception as e:
            logger.error(f"[图表显示失败] {e}")

    def _display_line_chart(self, feature_data: np.ndarray, y: np.ndarray, y_axis_title: str, col_name: str):
        chart = QChart()
        chart.setTitle(f"{y_axis_title} 分布")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        chart.setBackgroundVisible(True)
        chart.setBackgroundBrush(QColor(255, 255, 255))

        unique_faults = list(np.unique(y))
        fault_color_map = {ft: FAULT_COLORS[i % len(FAULT_COLORS)] for i, ft in enumerate(unique_faults)}

        axis_x = QValueAxis()
        axis_x.setTitleText("样本序号")
        axis_x.setLabelFormat("%d")
        axis_y = QValueAxis()
        axis_y.setTitleText(y_axis_title)
        axis_y.setLabelFormat("%.3f")
        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)

        max_points_per_fault = 2000

        for ft in unique_faults:
            color = fault_color_map[ft]
            series = QLineSeries()
            series.setName(ft)
            series.setPen(QPen(color, 1.5))

            indices = [j for j, label in enumerate(y) if label == ft]
            ft_data = feature_data[indices]
            n_ft = len(indices)
            if n_ft > max_points_per_fault:
                ft_step = n_ft // max_points_per_fault
                sampled_idx = indices[::ft_step]
                sampled_val = ft_data[::ft_step]
            else:
                sampled_idx = indices
                sampled_val = ft_data

            for idx, val in zip(sampled_idx, sampled_val):
                series.append(float(idx), float(val))

            chart.addSeries(series)
            series.attachAxis(axis_x)
            series.attachAxis(axis_y)
            self.chart_area.set_series_data(ft, sampled_idx, sampled_val)

            legend_item = QLabel(f"<span style='color:{color.name()};'>\u25CF</span> {ft}")
            legend_item.setFont(QFont("Microsoft YaHei", 9))
            self.legend_layout.addWidget(legend_item)

        if len(feature_data) > 0:
            axis_x.setRange(0, len(feature_data) - 1)
            y_min, y_max = feature_data.min(), feature_data.max()
            margin = (y_max - y_min) * 0.15 if y_max > y_min else 1.0
            axis_y.setRange(max(0, y_min - margin), y_max + margin)

        self.chart_area.setChart(chart)

    def _display_scatter_chart(self, feature_data: np.ndarray, y: np.ndarray, y_axis_title: str, col_name: str):
        chart = QChart()
        chart.setTitle(f"{y_axis_title} 分布")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        chart.setBackgroundVisible(True)
        chart.setBackgroundBrush(QColor(255, 255, 255))

        unique_faults = list(np.unique(y))
        fault_color_map = {ft: FAULT_COLORS[i % len(FAULT_COLORS)] for i, ft in enumerate(unique_faults)}

        axis_x = QValueAxis()
        axis_x.setTitleText("样本序号")
        axis_x.setLabelFormat("%d")
        axis_y = QValueAxis()
        axis_y.setTitleText(y_axis_title)
        axis_y.setLabelFormat("%.3f")
        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)

        max_points_per_fault = 2000

        for ft in unique_faults:
            color = fault_color_map[ft]
            series = QScatterSeries()
            series.setName(ft)
            series.setColor(color)
            series.setMarkerSize(8)

            indices = [j for j, label in enumerate(y) if label == ft]
            ft_data = feature_data[indices]
            n_ft = len(indices)
            if n_ft > max_points_per_fault:
                ft_step = n_ft // max_points_per_fault
                sampled_idx = indices[::ft_step]
                sampled_val = ft_data[::ft_step]
            else:
                sampled_idx = indices
                sampled_val = ft_data

            for idx, val in zip(sampled_idx, sampled_val):
                series.append(float(idx), float(val))

            chart.addSeries(series)
            series.attachAxis(axis_x)
            series.attachAxis(axis_y)
            self.chart_area.set_series_data(ft, sampled_idx, sampled_val)

            legend_item = QLabel(f"<span style='color:{color.name()};'>\u25CF</span> {ft}")
            legend_item.setFont(QFont("Microsoft YaHei", 9))
            self.legend_layout.addWidget(legend_item)

        if len(feature_data) > 0:
            axis_x.setRange(0, len(feature_data) - 1)
            y_min, y_max = feature_data.min(), feature_data.max()
            margin = (y_max - y_min) * 0.15 if y_max > y_min else 1.0
            axis_y.setRange(max(0, y_min - margin), y_max + margin)

        self.chart_area.setChart(chart)
