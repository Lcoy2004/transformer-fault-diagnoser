# config/__init__.py
"""
配置模块：包含日志配置、通知功能和常量定义
"""

from .logging import setup_logging, clean_old_logs
from .notification import (
    notify,
    get_notification,
    get_notification_with_time,
    clear_notification
)
from .constants import (
    DGA_FEATURES, DGA_FEATURES_DB, DGA_FEATURES_UNIT,
    PD_CHANNELS, PD_DB_TABLES, PD_FEATURES_UNIT,
    PD_FEATURES, INPUT_CONFIGS, TABLE_CONFIGS, TABLE_TYPE_MAP,
    LABEL_MAPPING, PD_FINE_LABELS, COLUMN_MAPPING, PCA_TABLE_MAPPING,
    ABOUT_CONTENT
)
from .helpers import get_models_dir, ensure_models_dir, ProgressHelper

__all__ = [
    'setup_logging',
    'clean_old_logs',
    'notify',
    'get_notification',
    'get_notification_with_time',
    'clear_notification',
    'DGA_FEATURES',
    'DGA_FEATURES_DB',
    'DGA_FEATURES_UNIT',
    'PD_CHANNELS',
    'PD_DB_TABLES',
    'PD_FEATURES_UNIT',
    'PD_FEATURES',
    'INPUT_CONFIGS',
    'TABLE_CONFIGS',
    'TABLE_TYPE_MAP',
    'LABEL_MAPPING',
    'PD_FINE_LABELS',
    'COLUMN_MAPPING',
    'PCA_TABLE_MAPPING',
    'ABOUT_CONTENT',
    'get_models_dir',
    'ensure_models_dir',
    'ProgressHelper'
]
