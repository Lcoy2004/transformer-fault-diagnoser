# TransformerFaultDiagnoser

<p align="center">
  <img src="resources/icon.svg" alt="TransformerFaultDiagnoser" width="128"/>
  <br>
  <strong>基于多源监测数据的电力变压器故障智能诊断系统</strong>
  <br>
</p>

---

## 项目简介

本项目是一款变压器故障诊断软件，采用**油色谱分析（DGA）**和**局部放电（PD）监测**技术，结合**PCA降维**和**随机森林分类**算法，实现对变压器故障类型、位置的智能诊断。

### 核心特性

| 特性 | 说明 |
|------|------|
| 多源数据融合 | 支持DGA油色谱数据 + PD局部放电数据联合诊断 |
| 智能算法 | PCA降维 + 随机森林分类 |
| 三种诊断模式 | 仅DGA / 仅PD / 融合诊断 |
| 可视化分析 | PCA贡献率图、样本分布图、故障位置图 |
| 数据管理 | SQLite数据库 + Excel数据导入 |

---

## 技术栈

| 类别 | 技术 |
|------|------|
| GUI | PySide6 |
| 数据库 | SQLite3 |
| 机器学习 | Scikit-learn (PCA, Random Forest) |
| 数据处理 | Pandas, NumPy |
| 数据读写 | openpyxl |

---

## 主要功能

1. **数据导入** - 导入DGA油色谱数据、PD局部放电数据（Excel格式）
2. **PCA降维** - 对四通道PD数据进行主成分分析
3. **模型训练** - 训练随机森林故障分类模型
4. **智能诊断** - 三种模式：仅DGA、仅PD、融合诊断
5. **可视化** - 原始数据PCA贡献率柱状图、样本分布散点图、诊断结果展示
6. **日志管理** - 完整的操作日志记录

---

## 诊断模式

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| 仅DGA | 仅使用油色谱数据进行故障判断 | 只有油色谱数据 |
| 仅PD | 仅使用局部放电数据判断放电细类 | 只有PD数据 |
| 融合诊断 | DGA判断故障大类 + PD细化放电类型 | 两种数据都有 |

---

## 项目结构

```
TransformerFaultDiagnoser/
├── config/              # 配置模块（日志、通知、常量）
├── database/            # 数据库管理（SQLite）
├── models/              # 训练好的模型
├── ui/                  # UI界面（PySide6）
├── utils/               # 工具模块
│   ├── chart_manager.py     # 可视化图表
│   ├── data_processor.py   # 数据处理
│   ├── input_manager.py    # 输入管理
│   ├── model_manager.py    # 模型管理
│   ├── predict_manager.py  # 预测管理
│   ├── predictor.py        # 预测器
│   ├── random_forest.py    # 随机森林算法
│   ├── table_manager.py    # 表格管理
│   ├── thread_manager.py   # 线程管理
│   └── train_pca.py        # PCA降维
├── resources/           # 资源文件
├── data/                # 数据目录
├── logs/                # 日志目录
├── main.py              # 主程序入口
└── README.md
```

---

## 安装

### 环境要求

- Python 3.13+
- Windows / Linux

### 依赖安装

```bash
pip install PySide6 pandas numpy scikit-learn openpyxl
```

### 运行

```bash
python main.py
```

---

## 使用流程

```
数据导入 → PCA降维（PD数据） → 模型训练 → 智能诊断 → 查看结果
```

1. **导入数据** - 点击「导入数据」导入Excel数据
2. **PCA降维** - 对PD数据进行降维处理
3. **训练模型** - 点击「训练判断模型」训练随机森林
4. **智能诊断** - 输入待诊断数据，点击「智能判断」
5. **查看结果** - 查看故障类型、位置、置信度

---

## 软件界面

### 主界面功能区

- **数据表格** - 显示数据库中的训练/诊断数据
- **输入区域** - 输入待诊断数据（DGA/PD）
- **操作按钮** - 导入数据、PCA降维、训练模型、智能判断
- **结果显示** - 输出诊断结果、故障类型、位置、置信度

### 可视化图表

- **PCA贡献率图** - 显示各主成分的方差贡献率
- **样本分布图** - 显示二维PCA空间的样本分布
- **诊断结果图** - 显示故障位置示意图
