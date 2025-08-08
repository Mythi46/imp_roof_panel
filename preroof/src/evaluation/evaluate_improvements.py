#!/usr/bin/env python3
"""
改进效果评估脚本
Improvement Evaluation Script

对比改进前后的模型性能，生成详细的评估报告
"""

import os
import sys
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from ultralytics import YOLO
import pandas as pd

def find_latest_training_results():
    """查找最新的训练结果"""
    runs_dir = Path("runs/segment")
    
    if not runs_dir.exists():
        print("❌ 未找到训练结果目录")
        return None, None
    
    # 查找改进版结果
    improved_dirs = list(runs_dir.glob("improved_training_v*"))
    improved_dir = max(improved_dirs, key=lambda x: x.stat().st_mtime) if improved_dirs else None
    
    # 查找原始版结果
    original_dirs = [d for d in runs_dir.iterdir() if d.is_dir() and "improved" not in d.name]
    original_dir = max(original_dirs, key=lambda x: x.stat().st_mtime) if original_dirs else None
    
    return improved_dir, original_dir

def load_training_results(result_dir):
    """加载训练结果"""
    if not result_dir or not result_dir.exists():
        return None
    
    results_file = result_dir / "results.csv"
    if not results_file.exists():
        print(f"⚠️ 结果文件不存在: {results_file}")
        return None
    
    try:
        df = pd.read_csv(results_file)
        # 清理列名中的空格
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        print(f"❌ 加载结果失败: {e}")
        return None

def evaluate_model_performance(model_path, data_yaml):
    """评估模型性能"""
    if not os.path.exists(model_path):
        print(f"❌ 模型文件不存在: {model_path}")
        return None
    
    print(f"📊 评估模型: {model_path}")
    
    try:
        model = YOLO(model_path)
        
        # 在验证集上评估
        results = model.val(
            data=data_yaml,
            imgsz=896,
            conf=0.35,
            iou=0.6,
            save_json=True,
            save_hybrid=True
        )
        
        # 提取关键指标
        metrics = {
            'mAP50': results.box.map50 if hasattr(results, 'box') else results.seg.map50,
            'mAP50_95': results.box.map if hasattr(results, 'box') else results.seg.map,
            'precision': results.box.mp if hasattr(results, 'box') else results.seg.mp,
            'recall': results.box.mr if hasattr(results, 'box') else results.seg.mr,
        }
        
        # 按类别的指标
        if hasattr(results, 'seg'):
            metrics['class_map50'] = results.seg.map50_per_class.tolist()
            metrics['class_map50_95'] = results.seg.map_per_class.tolist()
        elif hasattr(results, 'box'):
            metrics['class_map50'] = results.box.map50_per_class.tolist()
            metrics['class_map50_95'] = results.box.map_per_class.tolist()
        
        return metrics
        
    except Exception as e:
        print(f"❌ 模型评估失败: {e}")
        return None

def compare_training_curves(improved_df, original_df):
    """对比训练曲线"""
    print("📈 生成训练曲线对比图...")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('训练改进效果对比 (Training Improvement Comparison)', fontsize=16)
    
    # 关键指标列名映射
    metric_columns = {
        'mAP50': ['metrics/mAP50(B)', 'val/mAP50', 'mAP50'],
        'mAP50_95': ['metrics/mAP50-95(B)', 'val/mAP50-95', 'mAP50-95'],
        'box_loss': ['train/box_loss', 'box_loss'],
        'cls_loss': ['train/cls_loss', 'cls_loss']
    }
    
    def find_column(df, possible_names):
        for name in possible_names:
            if name in df.columns:
                return name
        return None
    
    # 绘制mAP50对比
    ax = axes[0, 0]
    if improved_df is not None:
        col = find_column(improved_df, metric_columns['mAP50'])
        if col:
            ax.plot(improved_df[col], label='改进版', linewidth=2, color='red')
    
    if original_df is not None:
        col = find_column(original_df, metric_columns['mAP50'])
        if col:
            ax.plot(original_df[col], label='原始版', linewidth=2, color='blue')
    
    ax.set_title('mAP@0.5 对比')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('mAP@0.5')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 绘制mAP50-95对比
    ax = axes[0, 1]
    if improved_df is not None:
        col = find_column(improved_df, metric_columns['mAP50_95'])
        if col:
            ax.plot(improved_df[col], label='改进版', linewidth=2, color='red')
    
    if original_df is not None:
        col = find_column(original_df, metric_columns['mAP50_95'])
        if col:
            ax.plot(original_df[col], label='原始版', linewidth=2, color='blue')
    
    ax.set_title('mAP@0.5:0.95 对比')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('mAP@0.5:0.95')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 绘制box_loss对比
    ax = axes[1, 0]
    if improved_df is not None:
        col = find_column(improved_df, metric_columns['box_loss'])
        if col:
            ax.plot(improved_df[col], label='改进版', linewidth=2, color='red')
    
    if original_df is not None:
        col = find_column(original_df, metric_columns['box_loss'])
        if col:
            ax.plot(original_df[col], label='原始版', linewidth=2, color='blue')
    
    ax.set_title('Box Loss 对比')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Box Loss')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 绘制cls_loss对比
    ax = axes[1, 1]
    if improved_df is not None:
        col = find_column(improved_df, metric_columns['cls_loss'])
        if col:
            ax.plot(improved_df[col], label='改进版', linewidth=2, color='red')
    
    if original_df is not None:
        col = find_column(original_df, metric_columns['cls_loss'])
        if col:
            ax.plot(original_df[col], label='原始版', linewidth=2, color='blue')
    
    ax.set_title('Classification Loss 对比')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Cls Loss')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('results/training_comparison.png', dpi=300, bbox_inches='tight')
    print("📊 训练曲线对比图已保存: results/training_comparison.png")

def generate_improvement_report(improved_metrics, original_metrics, class_names):
    """生成改进报告"""
    print("📋 生成改进效果报告...")
    
    report = []
    report.append("# 🏠 屋顶检测模型改进效果报告")
    report.append("=" * 50)
    report.append("")
    
    if improved_metrics and original_metrics:
        # 整体性能对比
        report.append("## 📊 整体性能对比")
        report.append("")
        report.append("| 指标 | 原始版 | 改进版 | 提升幅度 |")
        report.append("|------|--------|--------|----------|")
        
        for metric in ['mAP50', 'mAP50_95', 'precision', 'recall']:
            if metric in improved_metrics and metric in original_metrics:
                original_val = original_metrics[metric]
                improved_val = improved_metrics[metric]
                improvement = ((improved_val - original_val) / original_val) * 100
                
                report.append(f"| {metric} | {original_val:.3f} | {improved_val:.3f} | {improvement:+.1f}% |")
        
        report.append("")
        
        # 按类别性能对比
        if 'class_map50' in improved_metrics and 'class_map50' in original_metrics:
            report.append("## 🎯 按类别性能对比 (mAP@0.5)")
            report.append("")
            report.append("| 类别 | 原始版 | 改进版 | 提升幅度 |")
            report.append("|------|--------|--------|----------|")
            
            for i, class_name in enumerate(class_names):
                if i < len(original_metrics['class_map50']) and i < len(improved_metrics['class_map50']):
                    original_val = original_metrics['class_map50'][i]
                    improved_val = improved_metrics['class_map50'][i]
                    improvement = ((improved_val - original_val) / original_val) * 100 if original_val > 0 else 0
                    
                    report.append(f"| {class_name} | {original_val:.3f} | {improved_val:.3f} | {improvement:+.1f}% |")
            
            report.append("")
    
    elif improved_metrics:
        report.append("## 📊 改进版性能指标")
        report.append("")
        for metric, value in improved_metrics.items():
            if isinstance(value, (int, float)):
                report.append(f"- **{metric}**: {value:.3f}")
        report.append("")
    
    # 改进措施总结
    report.append("## 🔧 实施的改进措施")
    report.append("")
    report.append("1. **类别权重优化**: 使用正确的CLI传参方式")
    report.append("2. **模型升级**: yolov8m-seg → yolov8l-seg (更好特征分辨率)")
    report.append("3. **损失权重调整**: box=5.0, cls=1.2, dfl=2.5")
    report.append("4. **IoU优化**: 使用GIoU替代CIoU (更适合长条形目标)")
    report.append("5. **数据增强**: 启用copy_paste=0.2 (少数类增强)")
    report.append("6. **采样策略**: 启用weighted采样")
    report.append("7. **学习率策略**: 余弦退火 + 降低初始学习率")
    report.append("")
    
    # 保存报告
    with open('results/improvement_report.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print("📋 改进报告已保存: results/improvement_report.md")

def main():
    """主函数"""
    print("🔍 屋顶检测模型改进效果评估")
    print("=" * 50)
    
    # 确保结果目录存在
    Path("results").mkdir(exist_ok=True)
    
    # 查找训练结果
    improved_dir, original_dir = find_latest_training_results()
    
    print(f"📁 训练结果目录:")
    print(f"   改进版: {improved_dir}")
    print(f"   原始版: {original_dir}")
    
    # 加载训练曲线数据
    improved_df = load_training_results(improved_dir) if improved_dir else None
    original_df = load_training_results(original_dir) if original_dir else None
    
    # 生成训练曲线对比
    if improved_df is not None or original_df is not None:
        compare_training_curves(improved_df, original_df)
    
    # 评估模型性能
    data_yaml = "data/raw/new-2-1/data.yaml"
    improved_metrics = None
    original_metrics = None
    
    if improved_dir:
        best_model = improved_dir / "weights" / "best.pt"
        if best_model.exists():
            improved_metrics = evaluate_model_performance(str(best_model), data_yaml)
    
    if original_dir:
        best_model = original_dir / "weights" / "best.pt"
        if best_model.exists():
            original_metrics = evaluate_model_performance(str(best_model), data_yaml)
    
    # 获取类别名称
    class_names = ['Baren-Land', 'farm', 'rice-fields', 'roof']
    
    # 生成改进报告
    generate_improvement_report(improved_metrics, original_metrics, class_names)
    
    # 打印总结
    print(f"\n📊 评估完成!")
    print(f"   训练曲线对比: results/training_comparison.png")
    print(f"   改进效果报告: results/improvement_report.md")
    
    if improved_metrics and original_metrics:
        mAP50_improvement = ((improved_metrics['mAP50'] - original_metrics['mAP50']) / original_metrics['mAP50']) * 100
        print(f"   mAP@0.5 改进: {mAP50_improvement:+.1f}%")

if __name__ == "__main__":
    main()
