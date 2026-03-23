

# TransformerFaultDiagnoser

<p align="center">
  <img src="resources/icon.ico" alt="TransformerFaultDiagnoser Logo" width="128" height="128"/>
  <br>
  <strong>变压器故障诊断系统</strong>
  <br>
  基于油色谱分析（DGA）和机器学习算法的智能诊断工具
</p>

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
├── database/            # 数据库模块
├── models/              # 训练好的模型
├── ui/                  # UI界面模块
├── utils/               # 工具模块
├── data/                # 数据目录
├── test/                # 测试模块
├── resources/           # 资源文件
└── main.py              # 主程序入口
```

### 技术栈

- **GUI框架**: PySide6
- **数据库**: SQLite3
- **机器学习**: Scikit-learn (PCA, Random Forest)
- **数据处理**: Pandas, NumPy
- **数据读写**: openpyxl

## 核心模块说明

### config 模块

系统配置模块，定义常量及辅助函数。

- **constants.py**: 提供PD特征定义和常量配置
- **helpers.py**: 进度辅助类和目录工具
- **notification.py**: 通知管理器类
- **logging.py**: 日志配置

### database 模块

数据库管理模块，负责SQLite数据库操作。

- **db_manager.py**: 数据库管理器类，包含数据表的创建、查询、导入等功能

### utils 模块

核心算法工具及功能模块。

- **data_importer.py**: 数据导入模块，处理Excel数据导入
- **data_processor.py**: 数据处理模块，整合数据导入、处理、训练和预测功能
- **predictor.py**: 预测器模块，加载训练好的模型进行故障预测
- **random_forest.py**: 随机森林模块，用于模型训练和故障预测
- **train_pca.py**: PCA降维模块，用于特征提取和降维
- **thread_manager.py**: 线程管理模块，处理后台任务
- **chart_manager.py**: 图表管理模块，提供数据可视化功能
- **input_manager.py**: 输入管理模块，处理用户输入数据
- **predict_manager.py**: 预测管理模块，协调预测流程
- **model_manager.py**: 模型管理模块，管理模型训练和加载
- **table_manager.py**: 表格管理模块，处理数据表格显示
- **ui_manager.py**: UI管理模块，协调界面更新

### main.py

主程序入口，包含GUI主窗口类。

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
```

3. 激活虚拟环境：
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. 安装依赖包：
```bash
pip install PySide6 pandas numpy scikit-learn openpyxl
```

5. 运行主程序：
```bash
python main.py
```

首次运行时，数据导入功能会自动创建数据库。

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