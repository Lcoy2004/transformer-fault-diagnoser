"""
常量配置模块 - 统一管理所有配置常量
"""

from typing import Dict, List

DGA_FEATURES: List[str] = ['H2', 'CH4', 'C2H6', 'C2H4', 'C2H2']

DGA_FEATURES_DB: List[str] = ['h2', 'ch4', 'c2h6', 'c2h4', 'c2h2']

DGA_FEATURES_DESC: Dict[str, str] = {
    'H2': '氢气',
    'CH4': '甲烷',
    'C2H6': '乙烷',
    'C2H4': '乙烯',
    'C2H2': '乙炔'
}

PD_CHANNELS: List[str] = ['PD_CH1', 'PD_CH2', 'PD_CH3', 'PD_CH4']

PD_DB_TABLES: List[str] = ['pd_channel_1', 'pd_channel_2', 'pd_channel_3', 'pd_channel_4']

PD_FEATURES_DESC: Dict[str, str] = {
    'BAND1_ENERGY': '频带1能量',
    'BAND2_ENERGY': '频带2能量',
    'BAND3_ENERGY': '频带3能量',
    'BAND4_ENERGY': '频带4能量',
    'KURTOSIS': '峭度',
    'MAIN_AMP': '主频幅值',
    'MAIN_FREQ': '主频率',
    'MEAN': '均值',
    'PEAK': '峰值',
    'PULSE_WIDTH': '脉冲宽度',
    'SKEWNESS': '偏度',
    'VAR': '方差'
}

def _get_pd_features(channel: int) -> List[str]:
    """获取指定通道的PD特征列名"""
    return [
        f'ch{channel}_band1_energy', f'ch{channel}_band2_energy',
        f'ch{channel}_band3_energy', f'ch{channel}_band4_energy',
        f'ch{channel}_kurtosis', f'ch{channel}_main_amp',
        f'ch{channel}_main_freq', f'ch{channel}_mean',
        f'ch{channel}_peak', f'ch{channel}_pulse_width',
        f'ch{channel}_skewness', f'ch{channel}_var'
    ]

PD_FEATURES: Dict[str, List[str]] = {
    'PD_CH1': _get_pd_features(1),
    'PD_CH2': _get_pd_features(2),
    'PD_CH3': _get_pd_features(3),
    'PD_CH4': _get_pd_features(4),
}

INPUT_CONFIGS: Dict[str, Dict] = {
    "DGA数据": {
        'columns': DGA_FEATURES,
        'descriptions': [DGA_FEATURES_DESC.get(f, f) for f in DGA_FEATURES],
        'type': 'DGA'
    },
    "PD通道1": {
        'columns': [f.upper() for f in PD_FEATURES['PD_CH1']],
        'descriptions': [PD_FEATURES_DESC.get(f.split('_', 1)[1].upper() if '_' in f else f.upper(), f) for f in PD_FEATURES['PD_CH1']],
        'type': 'PD_CH1'
    },
    "PD通道2": {
        'columns': [f.upper() for f in PD_FEATURES['PD_CH2']],
        'descriptions': [PD_FEATURES_DESC.get(f.split('_', 1)[1].upper() if '_' in f else f.upper(), f) for f in PD_FEATURES['PD_CH2']],
        'type': 'PD_CH2'
    },
    "PD通道3": {
        'columns': [f.upper() for f in PD_FEATURES['PD_CH3']],
        'descriptions': [PD_FEATURES_DESC.get(f.split('_', 1)[1].upper() if '_' in f else f.upper(), f) for f in PD_FEATURES['PD_CH3']],
        'type': 'PD_CH3'
    },
    "PD通道4": {
        'columns': [f.upper() for f in PD_FEATURES['PD_CH4']],
        'descriptions': [PD_FEATURES_DESC.get(f.split('_', 1)[1].upper() if '_' in f else f.upper(), f) for f in PD_FEATURES['PD_CH4']],
        'type': 'PD_CH4'
    }
}

TABLE_CONFIGS: Dict[str, Dict] = {
    'oil_chromatography': {
        'name': '油色谱数据 (DGA)',
        'type': 'DGA',
        'features': DGA_FEATURES_DB,
        'label_col': 'fault_type',
        'location_col': 'fault_location'
    },
    'pd_channel_1': {
        'name': '通道1 (PD)',
        'type': 'PD_CH1',
        'features': PD_FEATURES['PD_CH1'],
        'label_col': 'fault_type',
        'location_col': 'fault_location'
    },
    'pd_channel_2': {
        'name': '通道2 (PD)',
        'type': 'PD_CH2',
        'features': PD_FEATURES['PD_CH2'],
        'label_col': 'fault_type',
        'location_col': 'fault_location'
    },
    'pd_channel_3': {
        'name': '通道3 (PD)',
        'type': 'PD_CH3',
        'features': PD_FEATURES['PD_CH3'],
        'label_col': 'fault_type',
        'location_col': 'fault_location'
    },
    'pd_channel_4': {
        'name': '通道4 (PD)',
        'type': 'PD_CH4',
        'features': PD_FEATURES['PD_CH4'],
        'label_col': 'fault_type',
        'location_col': 'fault_location'
    }
}

TABLE_TYPE_MAP: Dict[str, str] = {
    'oil_chromatography': 'DGA',
    'pd_channel_1': 'PD_CH1',
    'pd_channel_2': 'PD_CH2',
    'pd_channel_3': 'PD_CH3',
    'pd_channel_4': 'PD_CH4'
}

LABEL_MAPPING: Dict[str, Dict[str, str]] = {
    'DGA': {
        '正常': '正常',
        '中低温过热': '过热',
        '高温过热': '过热',
        '局部放电': '放电',
        '低能放电': '放电',
        '高能放电': '放电',
        '火花放电': '放电',
        '电弧放电': '放电'
    },
    'PD': {
        '尖端放电': '尖端放电',
        '悬浮放电': '悬浮放电',
        '沿面放电': '沿面放电',
        '气隙放电': '气隙放电'
    }
}

PD_FINE_LABELS: List[str] = ['尖端放电', '悬浮放电', '沿面放电', '气隙放电']

COLUMN_MAPPING: Dict[str, str] = {
    '故障类别': 'fault_type',
    '故障位置': 'fault_location',
    '故障类型': 'fault_type',
    '采集时间': 'sample_time',
    '采样时间': 'sample_time',
    '时间': 'sample_time'
}

PCA_TABLE_MAPPING: Dict[str, str] = {
    'DGA': 'fusion_features_dga',
    'PD_CH1': 'fusion_features_pd_ch1',
    'PD_CH2': 'fusion_features_pd_ch2',
    'PD_CH3': 'fusion_features_pd_ch3',
    'PD_CH4': 'fusion_features_pd_ch4'
}
