"""
常量配置模块 - 统一管理所有配置常量
"""

import os
from typing import Dict, List

# 加载 .env 文件中的环境变量（如果存在）
from pathlib import Path
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key, value)

DGA_FEATURES: List[str] = ['H2', 'CH4', 'C2H6', 'C2H4', 'C2H2']

DGA_FEATURES_DB: List[str] = ['h2', 'ch4', 'c2h6', 'c2h4', 'c2h2']

DGA_FEATURES_DESC: Dict[str, str] = {
    'H2': '氢气', 'CH4': '甲烷', 'C2H6': '乙烷', 'C2H4': '乙烯', 'C2H2': '乙炔'
}

DGA_FEATURES_UNIT: Dict[str, str] = {
    'H2': 'μL/L', 'CH4': 'μL/L', 'C2H6': 'μL/L', 'C2H4': 'μL/L', 'C2H2': 'μL/L'
}

PD_CHANNELS: List[str] = ['PD_CH1', 'PD_CH2', 'PD_CH3', 'PD_CH4']

PD_FEATURES_DESC: Dict[str, str] = {
    'BAND1_ENERGY': '频带1能量(归一化)', 'BAND2_ENERGY': '频带2能量(归一化)',
    'BAND3_ENERGY': '频带3能量(归一化)', 'BAND4_ENERGY': '频带4能量(归一化)',
    'KURTOSIS': '峭度', 'MAIN_AMP': '主频幅值', 'MAIN_FREQ': '主频率',
    'MEAN': '均值', 'PEAK': '峰值', 'PULSE_WIDTH': '脉冲宽度',
    'SKEWNESS': '偏度', 'VAR': '方差'
}

PD_FEATURES_UNIT: Dict[str, str] = {
    'BAND1_ENERGY': '', 'BAND2_ENERGY': '', 'BAND3_ENERGY': '', 'BAND4_ENERGY': '',
    'KURTOSIS': '', 'MAIN_AMP': 'mV', 'MAIN_FREQ': 'kHz', 'MEAN': 'mV',
    'PEAK': 'mV', 'PULSE_WIDTH': 'μs', 'SKEWNESS': '', 'VAR': 'mV²'
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
    f'PD_CH{i}': _get_pd_features(i) for i in range(1, 5)
}

def _get_pd_input_config(channel: int) -> Dict:
    """获取PD输入配置"""
    features = PD_FEATURES[f'PD_CH{channel}']
    descriptions = []
    for f in features:
        feature_key = f.split('_', 1)[1].upper()
        desc = PD_FEATURES_DESC.get(feature_key, f)
        unit = PD_FEATURES_UNIT.get(feature_key, '')
        descriptions.append(f"{desc} ({unit})" if unit else desc)
    return {
        'columns': [f.upper() for f in features],
        'descriptions': descriptions,
        'type': f'PD_CH{channel}'
    }

INPUT_CONFIGS: Dict[str, Dict] = {
    "DGA数据": {
        'columns': DGA_FEATURES,
        'descriptions': [f"{DGA_FEATURES_DESC.get(f, f)} ({DGA_FEATURES_UNIT.get(f, '')})" for f in DGA_FEATURES],
        'type': 'DGA'
    },
    **{f"PD通道{i}": _get_pd_input_config(i) for i in range(1, 5)}
}

TABLE_CONFIGS: Dict[str, Dict] = {
    'oil_chromatography': {
        'name': '油色谱数据 (DGA)', 'type': 'DGA',
        'features': DGA_FEATURES_DB, 'label_col': 'fault_type', 'location_col': 'fault_location'
    },
    **{f'pd_channel_{i}': {
        'name': f'通道{i} (PD)', 'type': f'PD_CH{i}',
        'features': PD_FEATURES[f'PD_CH{i}'], 'label_col': 'fault_type', 'location_col': 'fault_location'
    } for i in range(1, 5)},
    'fusion_features_dga': {
        'name': 'DGA降维特征', 'type': 'DGA_PCA',
        'features': ['pc1', 'pc2', 'pc3', 'pc4', 'pc5'], 'label_col': 'fault_type', 'location_col': 'fault_location',
        'is_pca': True
    },
    **{f'fusion_features_pd_ch{i}': {
        'name': f'通道{i}降维特征', 'type': f'PD_CH{i}_PCA',
        'features': [f'pc{j}' for j in range(1, 11)], 'label_col': 'fault_type', 'location_col': 'fault_location',
        'is_pca': True
    } for i in range(1, 5)}
}

TABLE_TYPE_MAP: Dict[str, str] = {
    'oil_chromatography': 'DGA',
    **{f'pd_channel_{i}': f'PD_CH{i}' for i in range(1, 5)}
}

TYPE_TO_TABLE_MAP: Dict[str, str] = {
    'DGA': 'oil_chromatography',
    **{f'PD_CH{i}': f'pd_channel_{i}' for i in range(1, 5)}
}

LABEL_MAPPING: Dict[str, Dict[str, str]] = {
    'DGA': {
        '正常': '正常', '中低温过热': '过热', '高温过热': '过热',
        '局部放电': '放电', '低能放电': '放电', '高能放电': '放电',
        '火花放电': '放电', '电弧放电': '放电'
    },
    'PD': {'尖端放电': '尖端放电', '悬浮放电': '悬浮放电', '沿面放电': '沿面放电', '气隙放电': '气隙放电'}
}

COLUMN_MAPPING: Dict[str, str] = {
    '故障类别': 'fault_type', '故障定位': 'fault_location', '故障位置': 'fault_location', '故障类型': 'fault_type',
    '采集时间': 'sample_time', '采样时间': 'sample_time', '时间': 'sample_time'
}

PCA_TABLE_MAPPING: Dict[str, str] = {
    'DGA': 'fusion_features_dga',
    **{f'PD_CH{i}': f'fusion_features_pd_ch{i}' for i in range(1, 5)}
}

VALID_TABLES: set = set(TABLE_CONFIGS.keys())

VALID_PCA_TABLES: set = set(PCA_TABLE_MAPPING.values())

VALID_ALL_TABLES: set = VALID_TABLES | VALID_PCA_TABLES

# 关于窗口内容 - 从环境变量读取敏感信息
_author_name = os.environ.get('AUTHOR_NAME', '开发者')
_author_grade = os.environ.get('AUTHOR_GRADE', '')
_author_university = os.environ.get('AUTHOR_UNIVERSITY', '')
_author_college = os.environ.get('AUTHOR_COLLEGE', '')
_project_url = os.environ.get('PROJECT_URL', '')

ABOUT_CONTENT: str = f"""
## 本科毕业设计
---
### 基于多源监测数据的电力变压器故障智能诊断系统
---

**{_author_university} {_author_college}**  
**学生**：{_author_name}{f'（{_author_grade}）' if _author_grade else ''}  
{f'**项目地址**：[{_project_url}]({_project_url})' if _project_url else ''}
"""

# 操作说明内容（内嵌到程序中，打包后无需外部文件）
HELP_CONTENT: str = """# 变压器故障诊断系统 - 使用手册

## 软件概述

本软件基于**油色谱分析（DGA）**和**局部放电超声波检测（AE-PD）**监测技术，采用**PCA降维**和**随机森林**算法，实现变压器故障的智能诊断。

---

## 功能详解

### 1. 数据导入

**作用**：将Excel格式的训练数据导入数据库

**操作步骤**：
1. 点击顶部菜单栏「文件」→「数据导入」
2. 选择Excel文件（.xlsx格式）
3. 系统自动识别数据类型并导入

**菜单路径**：`文件 → 数据导入`

**支持的数据类型**：
| 数据类型 | 说明 | 文件格式 |
|---------|------|---------|
| 油色谱数据 | H2、CH4、C2H6、C2H4、C2H2含量 | Excel |
| 局部放电数据 | 四通道超声波PD特征数据 | Excel |

**注意事项**：
- 首次导入会自动创建数据库
- 重复导入同一文件会提示已存在
- 列名支持中英文自动识别

---

### 2. 刷新训练数据表

**作用**：刷新数据库表列表

**操作**：点击「刷新训练数据表」按钮

**功能**：
- 重新加载数据库中的所有表
- 更新「查阅数据」下拉框的选项
- 显示表列表刷新状态

---

### 3. 查阅数据

**作用**：查看数据库中的训练/诊断数据

**操作步骤**：
1. 点击「查阅数据」下拉框
2. 选择要查看的表
3. 数据自动显示在左侧表格中

**支持的表**：
- oil_chromatography（油色谱数据）
- pd_channel_1~4（四通道超声波PD数据）
- fusion_features_dga（DGA降维特征）
- fusion_features_pd_ch1~4（PD降维特征）

---

### 4. 数据降维（PCA）

**作用**：对四通道超声波PD数据进行主成分分析，提取关键特征

**操作步骤**：
1. 确保已导入超声波PD数据
2. 点击「数据降维」按钮
3. 等待训练完成

**输出结果**：
- 各通道PCA模型
- 主成分数量
- 累计方差贡献率
- 各成分方差贡献

**注意事项**：
- 必须先导入超声波PD数据才能进行PCA
- 降维后的数据自动保存到数据库
- 用于后续的融合诊断

---

### 5. 训练判断模型

**作用**：训练随机森林分类模型

**操作步骤**：
1. 确保已导入训练数据
2. 点击「训练判断模型」按钮
3. 等待训练完成

**训练内容**：
- **DGA模型**：基于油色谱数据判断故障大类
- **PD融合模型**：基于四通道超声波PD数据判断放电细类

**输出结果**：
- 模型准确率
- 故障类型准确率
- 故障定位准确率
- 模型文件自动保存到models目录

**注意事项**：
- 训练前建议先进行PCA降维（如有超声波PD数据）
- 训练时间取决于数据量
- 新模型会覆盖旧模型

---

### 6. 智能诊断

**作用**：输入待诊断数据，自动判断故障类型和位置

#### 三种诊断模式

| 模式 | 触发条件 | 诊断逻辑 |
|------|---------|---------|
| **仅DGA** | 只输入DGA数据 | DGA模型直接判断故障大类（正常/过热/放电） |
| **仅PD** | 只输入PD数据 | 超声波PD模型判断放电细类 |
| **融合诊断** | DGA+PD数据都有 | DGA判断大类，如果是放电则PD细化放电类型 |

#### 操作步骤

**输入数据**：
1. 在「选择对应表输入数据」下拉框中选择输入类型（DGA数据/PD_CH1/PD_CH2/PD_CH3/PD_CH4）
2. 在右侧输入表格中输入数值
3. 切换输入类型时，数据自动缓存
4. 输入完成后点击「智能判断」按钮

**查看结果**：
- 故障类型（如：正常、过热、放电等）
- 故障定位（超声波时差定位坐标或放电位置）
- 置信度（准确率）

**注意事项**：
- 输入数据时自动缓存，切换类型不会丢失
- 至少输入一种数据才能诊断
- 融合诊断需要同时有DGA和PD数据
- DGA数据包括：H2、CH4、C2H6、C2H4、C2H2五种气体含量
- PD数据包括：四通道超声波传感器的频带能量（归一化比例）、峭度、主频幅值等特征

---

### 7. 查询日志

**作用**：查看软件运行日志

**操作**：点击「查询日志」按钮

**功能**：
- 打开当日日志文件
- 查看操作记录、错误信息、诊断结果

**日志内容**：
- 操作记录
- 错误信息
- 诊断结果
- 系统状态

**日志管理**：
- 日志文件保存在logs目录
- 自动清理30天前的日志

---

### 8. 原始图表

**作用**：查看数据分析图表

**操作步骤**：
1. 点击顶部菜单栏「文件」→「原始图表」
2. 选择数据表和特征
3. 查看图表

**菜单路径**：`文件 → 原始图表`

**支持的图表**：
- **PCA贡献率图**：显示各主成分的方差贡献率
- **样本分布图**：显示二维PCA空间的样本分布
- **特征趋势图**：显示特征值的变化趋势

---

### 9. 操作说明

**作用**：显示本使用手册

**操作**：点击顶部菜单栏「帮助」→「操作说明」

**菜单路径**：`帮助 → 操作说明`

---

### 10. 关于

**作用**：显示作者信息

**操作**：点击顶部菜单栏「帮助」→「关于」

**菜单路径**：`帮助 → 关于`

---

## 完整操作流程

### 首次使用

```
1. 导入训练数据（油色谱 + 局部放电）
   ↓
2. 数据降维（PCA）
   ↓
3. 训练判断模型
   ↓
4. 输入待诊断数据
   ↓
5. 智能诊断
   ↓
6. 查看结果
```

### 日常使用

```
1. 输入待诊断数据
   ↓
2. 智能诊断
   ↓
3. 查看结果
```

---

## 故障诊断原理

### 决策级融合策略

```
输入数据
    │
    ├── DGA数据 ──→ DGA模型 ──→ 故障大类（正常/过热/放电）
    │                              │
    │                              └── 如果是放电 ──→ PD模型细化
    │                                                      ↓
    │                                              放电细类（尖端/悬浮/沿面/气隙）
    │
    └── 超声波PD数据 ────→ PD模型 ──→ 放电细类
```

### 诊断流程

1. **数据输入**：用户在输入区域输入DGA和/或超声波PD数据
2. **模式判断**：系统根据输入数据自动判断使用哪种诊断模式
3. **模型预测**：调用相应的机器学习模型进行预测
4. **结果融合**：如有需要，进行决策级融合
5. **输出结果**：在「操作结果」区域显示故障类型、位置、置信度

---

## 菜单功能汇总

### 文件菜单
| 菜单项 | 功能 |
|--------|------|
| 数据导入 | 导入Excel格式的训练数据到数据库 |
| 原始图表 | 打开数据可视化图表窗口 |

### 帮助菜单
| 菜单项 | 功能 |
|--------|------|
| 操作说明 | 显示本使用手册 |
| 关于 | 显示软件版本和版权信息 |

---

## 界面按钮汇总

| 按钮 | 功能 |
|------|------|
| 刷新训练数据表 | 刷新数据库表列表 |
| 查阅数据 | 下拉框，选择要查看的数据表 |
| 数据降维 | 对超声波PD数据进行PCA降维 |
| 训练判断模型 | 训练随机森林分类模型 |
| 查询日志 | 打开当日日志文件 |
| 智能判断 | 执行故障诊断（橙色大按钮） |

---

## 常见问题

### Q1: 导入数据失败？
**A**: 检查Excel文件格式，确保列名正确（支持中英文自动识别）

### Q2: 智能判断按钮无法点击？
**A**: 需要先训练模型，点击「训练判断模型」按钮完成训练

### Q3: 诊断结果不准确？
**A**: 
- 检查输入数据是否正确
- 增加训练数据量
- 确保模型训练充分

### Q4: 如何查看历史诊断记录？
**A**: 诊断结果保存在数据库中，可通过「查阅数据」下拉框选择相应表查看

### Q5: 模型文件保存在哪里？
**A**: models目录下，包含PCA模型（.pkl）和随机森林模型（.pkl）

### Q6: 输入数据时切换类型，之前的数据会丢失吗？
**A**: 不会。系统会自动缓存各类型输入数据，切换时自动恢复

### Q7: 为什么需要数据降维？
**A**: 超声波PD数据维度较高（四通道×多特征），PCA降维可以提取主要特征，提高模型效率和准确率

### Q8: 融合诊断和单独诊断有什么区别？
**A**: 
- **仅DGA**：只能判断故障大类（正常/过热/放电）
- **仅PD**：只能判断放电细类
- **融合诊断**：DGA判断大类，如果是放电则PD进一步细化，诊断更准确

---

## 技术支持

如有问题，请查看日志文件或提交issue。
"""
