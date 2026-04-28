#!/usr/bin/env python3
"""
模型参数调优测试 - 评估最大深度对分类准确率的影响
在DGA数据集上，使用不同的max_depth值进行实验
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
from config.constants import DGA_FEATURES_DB


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


def train_and_evaluate(X, y, max_depth, random_state=42):
    """
    训练随机森林模型并评估准确率

    Args:
        X: 特征数据
        y: 标签
        max_depth: 最大深度（None表示不限制）
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
        n_estimators=100,
        max_depth=max_depth,
        random_state=random_state,
        n_jobs=-1,
        class_weight='balanced'
    )
    rf_model.fit(X_train_scaled, y_train)

    y_pred = rf_model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)

    return accuracy


def run_max_depth_experiment():
    """
    运行max_depth参数调优实验
    评估不同最大深度对DGA故障分类准确率的影响
    """
    print("=" * 60)
    print("模型参数调优实验 - max_depth对分类准确率的影响")
    print("=" * 60)

    max_depth_list = [5, 10, 15, 20, 25, 30, None]
    depth_labels = ['5', '10', '15', '20', '25', '30', '无限制']
    accuracies = []
    results_detail = []

    print("\n[1/3] 加载DGA数据...")
    X, y = load_dga_data()
    print(f"      数据加载完成: {len(X)} 个样本, {X.shape[1]} 个特征")
    print(f"      故障类型分布: {dict(zip(*np.unique(y, return_counts=True)))}")

    print("\n[2/3] 开始训练实验...")
    print("-" * 60)

    for max_depth, label in zip(max_depth_list, depth_labels):
        accuracy = train_and_evaluate(X, y, max_depth, random_state=42)
        accuracies.append(accuracy)
        results_detail.append({
            'max_depth': max_depth if max_depth else '无限制',
            'max_depth_raw': max_depth,
            'accuracy': accuracy,
            'error_rate': 1 - accuracy
        })
        depth_str = f"max_depth = {label:>8}"
        print(f"      {depth_str} | 准确率 = {accuracy:.4f} | 错误率 = {1-accuracy:.4f}")

    print("-" * 60)

    print("\n[3/3] 生成准确率对比图表...")
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False

    fig, ax = plt.subplots(figsize=(12, 6))

    x_positions = range(len(max_depth_list))
    bars = ax.bar(x_positions, accuracies, color='steelblue', alpha=0.8, edgecolor='black')

    for i, (bar, acc) in enumerate(zip(bars, accuracies)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., height,
                f'{acc:.4f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_xlabel('最大深度 (max_depth)', fontsize=12)
    ax.set_ylabel('分类准确率 (Accuracy)', fontsize=12)
    ax.set_title('DGA故障诊断 - max_depth参数调优实验', fontsize=14, fontweight='bold')
    ax.set_xticks(x_positions)
    ax.set_xticklabels(depth_labels)
    ax.set_ylim(min(accuracies) - 0.02, max(accuracies) + 0.05)
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)

    best_idx = np.argmax(accuracies)
    best_max_depth = max_depth_list[best_idx]
    best_label = depth_labels[best_idx]
    best_acc = accuracies[best_idx]
    bars[best_idx].set_color('green')
    bars[best_idx].set_alpha(1.0)

    ax.annotate(f'最佳: max_depth={best_label}\n准确率: {best_acc:.4f}',
                xy=(best_idx, best_acc),
                xytext=(best_idx + 1.5, best_acc + 0.02),
                arrowprops=dict(arrowstyle='->', color='red'),
                fontsize=10,
                color='red',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

    plt.tight_layout()

    output_path = os.path.join(os.path.dirname(__file__), 'max_depth_accuracy.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"      图表已保存: {output_path}")

    print("\n" + "=" * 60)
    print("实验结果汇总")
    print("=" * 60)
    print(f"{'max_depth':<15} {'准确率':<15} {'错误率':<15}")
    print("-" * 45)
    for r in results_detail:
        print(f"{str(r['max_depth']):<15} {r['accuracy']:<15.4f} {r['error_rate']:<15.4f}")
    print("-" * 45)
    print(f"\n最佳参数: max_depth = {best_label}")
    print(f"最高准确率: {best_acc:.4f}")
    print("=" * 60)

    plt.show()

    return results_detail


if __name__ == '__main__':
    run_max_depth_experiment()
