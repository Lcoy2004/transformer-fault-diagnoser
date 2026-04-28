#!/usr/bin/env python3
"""
模型参数调优测试 - 评估决策树数量对分类准确率的影响
在DGA数据集上，使用不同的n_estimators值进行实验
"""

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from config.constants import TABLE_CONFIGS, DGA_FEATURES_DB


def load_dga_data():
    """从数据库加载DGA数据"""
    db = DatabaseManager()
    table_name = 'oil_chromatography'
    table_data, columns = db.get_table_data(table_name)
    df = pd.DataFrame(table_data, columns=columns)

    if df is None or len(df) == 0:
        raise ValueError("无法从数据库加载DGA数据")

    X = df[DGA_FEATURES_DB].values
    y = df['fault_type'].values

    return X, y


def train_and_evaluate(X, y, n_estimators, random_state=42):
    """
    训练随机森林模型并评估准确率

    Args:
        X: 特征数据
        y: 标签
        n_estimators: 决策树数量
        random_state: 随机种子

    Returns:
        float: 测试集准确率
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    rf_model = RandomForestClassifier(
        n_estimators=n_estimators,
        random_state=random_state,
        n_jobs=-1,
        class_weight='balanced',
        max_depth=20
    )
    rf_model.fit(X_train_scaled, y_train)

    y_pred = rf_model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)

    return accuracy


def run_n_estimators_experiment():
    """
    运行n_estimators参数调优实验
    评估不同决策树数量对DGA故障分类准确率的影响
    """
    print("=" * 60)
    print("模型参数调优实验 - n_estimators对分类准确率的影响")
    print("=" * 60)

    n_estimators_list = [50, 100, 200, 300, 500]
    accuracies = []
    results_detail = []

    print("\n[1/3] 加载DGA数据...")
    X, y = load_dga_data()
    print(f"      数据加载完成: {len(X)} 个样本, {X.shape[1]} 个特征")
    print(f"      故障类型分布: {dict(zip(*np.unique(y, return_counts=True)))}")

    print("\n[2/3] 开始训练实验...")
    print("-" * 60)

    for n_est in n_estimators_list:
        accuracy = train_and_evaluate(X, y, n_est, random_state=42)
        accuracies.append(accuracy)
        results_detail.append({
            'n_estimators': n_est,
            'accuracy': accuracy,
            'error_rate': 1 - accuracy
        })
        print(f"      n_estimators = {n_est:4d} | 准确率 = {accuracy:.4f} | 错误率 = {1-accuracy:.4f}")

    print("-" * 60)

    print("\n[3/3] 生成准确率对比图表...")
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(n_estimators_list, accuracies, 'bo-', linewidth=2, markersize=10, label='分类准确率')
    ax.fill_between(n_estimators_list, accuracies, alpha=0.3, color='blue')

    for i, (n_est, acc) in enumerate(zip(n_estimators_list, accuracies)):
        ax.annotate(f'{acc:.4f}',
                    xy=(n_est, acc),
                    xytext=(0, 10),
                    textcoords='offset points',
                    ha='center',
                    fontsize=10,
                    fontweight='bold')

    ax.set_xlabel('决策树数量 (n_estimators)', fontsize=12)
    ax.set_ylabel('分类准确率 (Accuracy)', fontsize=12)
    ax.set_title('DGA故障诊断 - n_estimators参数调优实验', fontsize=14, fontweight='bold')
    ax.set_xticks(n_estimators_list)
    ax.set_xlim(0, max(n_estimators_list) + 50)
    ax.set_ylim(min(accuracies) - 0.02, max(accuracies) + 0.02)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend(loc='lower right', fontsize=10)

    best_idx = np.argmax(accuracies)
    best_n_est = n_estimators_list[best_idx]
    best_acc = accuracies[best_idx]
    ax.axhline(y=best_acc, color='r', linestyle='--', alpha=0.5, label=f'最佳准确率: {best_acc:.4f}')
    ax.annotate(f'最佳: n_estimators={best_n_est}\n准确率: {best_acc:.4f}',
                xy=(best_n_est, best_acc),
                xytext=(best_n_est + 80, best_acc - 0.03),
                arrowprops=dict(arrowstyle='->', color='red'),
                fontsize=10,
                color='red',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

    plt.tight_layout()

    output_path = os.path.join(os.path.dirname(__file__), 'n_estimators_accuracy.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"      图表已保存: {output_path}")

    print("\n" + "=" * 60)
    print("实验结果汇总")
    print("=" * 60)
    print(f"{'n_estimators':<15} {'准确率':<15} {'错误率':<15}")
    print("-" * 45)
    for r in results_detail:
        print(f"{r['n_estimators']:<15} {r['accuracy']:<15.4f} {r['error_rate']:<15.4f}")
    print("-" * 45)
    print(f"\n最佳参数: n_estimators = {best_n_est}")
    print(f"最高准确率: {best_acc:.4f}")
    print("=" * 60)

    plt.show()

    return results_detail


if __name__ == '__main__':
    run_n_estimators_experiment()
