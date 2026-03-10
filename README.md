

# TransformerFaultDiagnoser

变压器故障诊断系统 - 基于油色谱分析（DGA）和机器学习算法的智能诊断工具

## 项目简介

TransformerFaultDiagnoser 是一款专业的变压器故障诊断软件，采用油色谱分析（DGA）技术结合机器学习算法（PCA降维 + 随机森林分类），实现对变压器故障类型、位置和置信度的智能诊断。

### 主要功能

- **数据导入**：支持油色谱数据、高频放电数据、特高频放电数据的导入和管理
- **特征提取**：提供PCA降维和特征融合功能，提取关键故障特征
- **模型训练**：基于随机森林算法训练故障分类模型
- **智能诊断**：快速分析待诊断数据，输出故障类型、位置和置信度
- **可视化分析**：提供PCA贡献率柱状图、样本分布散点图、故障位置示意图
- **报告导出**：生成详细的诊断报告

## 软件架构

```
TransformerFaultDiagnoser/
├── config/              # 配置模块
│   ├── logging.py      # 日志配置
│   └── notification.py # 通知管理
├── database/           # 数据库模块
│   └── db_manager.py   # SQLite数据库管理
├── models/             # 训练好的模型
│   ├── pca_model.pkl   # PCA降维模型
│   ├── random_forest_multioutput_model.pkl  # 随机森林模型
│   └── scaler.pkl      # 数据标准化器
├── ui/                 # UI界面模块
│   ├── mainui.ui       # Qt UI定义
│   └── mainui_ui.py    # UI生成代码
├── utils/              # 工具模块
│   ├── random_forest.py  # 随机森林训练与预测
│   └── train_pca.py      # PCA模型训练
├── data/               # 数据目录
│   └── DGA_data.xlsx  # 油色谱样本数据
├── test/               # 测试模块
│   └── test_main_gui.py # GUI测试
└── main.py             # 主程序入口
```

### 技术栈

- **GUI框架**: PySide6
- **数据库**: SQLite3
- **机器学习**: Scikit-learn (PCA, Random Forest)
- **数据处理**: Pandas, NumPy

## 核心模块说明

### config/notification.py

通知管理模块，提供系统消息通知功能。

- `NotificationManager`: 通知管理器类
  - `add_notification(message)`: 添加通知消息
  - `get_current_notification()`: 获取当前通知
  - `get_notification_with_timestamp()`: 获取带时间戳的通知
  - `clear_notification()`: 清除通知

### database/db_manager.py

数据库管理模块，负责SQLite数据库操作。

- `DatabaseManager`: 数据库管理器类
  - `__init__(db_path)`: 初始化数据库连接
  - `get_connection()`: 获取数据库连接
  - `_create_tables()`: 创建数据表
  - `import_dga_data(excel_file, progress_callback, progress_value_callback)`: 导入DGA数据
  - `create_partial_discharge_table()`: 创建放电数据表
  - `get_all_tables()`: 获取所有数据表
  - `get_table_data(table_name)`: 获取指定表数据

### utils/random_forest.py

随机森林模块，用于模型训练和故障预测。

- `train_random_forest(db_path, n_estimators, random_state, progress_callback, progress_value_callback)`: 训练随机森林模型
- `predict_with_random_forest(X)`: 使用随机森林进行预测

### utils/train_pca.py

PCA降维模块，用于特征提取和降维。

- `train_pca_model(data_source, data_file, db_path, feature_columns, n_components, progress_callback, progress_value_callback)`: 训练PCA模型

### main.py

主程序入口，包含GUI主窗口和后台工作线程。

- `WorkerThread`: 后台工作线程类，用于执行耗时操作
- `MainWindow`: 主窗口类，提供用户界面

## 安装教程

### 环境要求

- Python 3.13+
- PySide6
- pandas
- numpy
- scikit-learn
- openpyxl

### 安装步骤

1. 克隆项目到本地：
```bash
git clone https://gitee.com/lcoy/transformer-fault-diagnoser.git
cd transformer-fault-diagnoser
```

2. 创建并激活虚拟环境（推荐）：
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. 安装依赖包：
```bash
pip install -r requirements.txt
```

如果项目中没有requirements.txt，可手动安装：
```bash
pip install PySide6 pandas numpy scikit-learn openpyxl
```

4. 初始化数据库：
```bash
# 运行主程序后，数据导入功能会自动创建数据库
python main.py
```

## 使用说明

### 1. 数据导入

- 点击工具栏中的「油色谱」按钮导入DGA数据
- 支持Excel格式的油色谱数据文件
- 数据将自动存储到SQLite数据库中

### 2. 特征提取

- **PCA降维**：对高维特征进行降维处理，保留主要信息
- **特征融合**：整合多种特征，提高诊断准确性

### 3. 模型训练

- 点击「训练模型」按钮开始训练随机森林分类模型
- 训练过程中可查看进度条
- 训练完成后模型会自动保存

### 4. 故障诊断

- 导入待诊断的变压器数据
- 点击「开始诊断」按钮
- 查看诊断结果：故障类型、故障位置、置信度

### 5. 报告导出

- 诊断完成后可导出详细的诊断报告
- 报告包含原始数据、诊断结果、图表分析

## 目录结构说明

| 目录/文件 | 说明 |
|-----------|------|
| config/ | 系统配置，包含日志和通知管理 |
| database/ | 数据库操作，存储样本数据和诊断记录 |
| models/ | 训练好的机器学习模型 |
| ui/ | Qt用户界面定义 |
| utils/ | 核心算法工具（PCA、随机森林） |
| data/ | 原始数据文件 |
| logs/ | 运行日志 |

## 参与贡献

1. Fork 本仓库
2. 新建特性分支 (`git checkout -b feat/xxx`)
3. 提交更改 (`git commit -m 'Add xxx'`)
4. 推送分支 (`git push origin feat/xxx`)
5. 新建 Pull Request

## 许可证

本项目仅供学习和研究使用。

## 联系方式

- 项目地址：https://gitee.com/lcoy/transformer-fault-diagnoser
- 问题反馈：https://gitee.com/lcoy/transformer-fault-diagnoser/issues