#!/usr/bin/env python3
"""
继续训练监控脚本
Continue Training Monitor Script

专门监控继续训练的进展，分析是否有额外的性能提升
"""

import os
import time
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import json
from datetime import datetime

def monitor_continue_training():
    """监控继续训练进度"""
    
    # 基线数据
    baseline_dir = Path("runs/segment/improved_training_compatible")
    baseline_csv = baseline_dir / "results.csv"
    
    # 继续训练数据
    continue_dir = Path("runs/segment/continue_training_optimized")
    continue_csv = continue_dir / "results.csv"
    
    print("🔍 继续训练监控启动...")
    print(f"基线目录: {baseline_dir}")
    print(f"继续训练目录: {continue_dir}")
    
    # 读取基线性能
    if baseline_csv.exists():
        baseline_df = pd.read_csv(baseline_csv)
        baseline_metrics = baseline_df.iloc[-1]
        baseline_map50 = baseline_metrics['metrics/mAP50(B)']
        baseline_map50_95 = baseline_metrics['metrics/mAP50-95(B)']
        
        print(f"\n📊 基线性能 (7 epochs):")
        print(f"   mAP@0.5: {baseline_map50:.4f}")
        print(f"   mAP@0.5:0.95: {baseline_map50_95:.4f}")
        print(f"   目标提升: >1% (mAP@0.5 > {baseline_map50*1.01:.4f})")
    else:
        print("❌ 未找到基线数据")
        return
    
    last_epoch = 0
    monitoring_data = []
    
    while True:
        try:
            if continue_csv.exists():
                # 读取继续训练结果
                df = pd.read_csv(continue_csv)
                current_epoch = len(df)
                
                if current_epoch > last_epoch:
                    # 新的epoch完成
                    latest_row = df.iloc[-1]
                    
                    # 计算相对于基线的改善
                    current_map50 = latest_row['metrics/mAP50(B)']
                    current_map50_95 = latest_row['metrics/mAP50-95(B)']
                    
                    map50_improvement = ((current_map50 - baseline_map50) / baseline_map50) * 100
                    map50_95_improvement = ((current_map50_95 - baseline_map50_95) / baseline_map50_95) * 100
                    
                    # 记录数据
                    epoch_data = {
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'epoch': current_epoch,
                        'train_box_loss': latest_row.get('train/box_loss', 0),
                        'train_seg_loss': latest_row.get('train/seg_loss', 0),
                        'train_cls_loss': latest_row.get('train/cls_loss', 0),
                        'val_box_loss': latest_row.get('val/box_loss', 0),
                        'val_seg_loss': latest_row.get('val/seg_loss', 0),
                        'val_cls_loss': latest_row.get('val/cls_loss', 0),
                        'metrics_mAP50_B': current_map50,
                        'metrics_mAP50_95_B': current_map50_95,
                        'map50_improvement_percent': map50_improvement,
                        'map50_95_improvement_percent': map50_95_improvement,
                        'lr_pg0': latest_row.get('lr/pg0', 0)
                    }
                    
                    monitoring_data.append(epoch_data)
                    
                    # 打印进度
                    print(f"\n📊 继续训练 Epoch {current_epoch}/22:")
                    print(f"   当前mAP@0.5: {current_map50:.4f} (基线: {baseline_map50:.4f})")
                    print(f"   mAP@0.5改善: {map50_improvement:+.2f}%")
                    print(f"   当前mAP@0.5:0.95: {current_map50_95:.4f} (基线: {baseline_map50_95:.4f})")
                    print(f"   mAP@0.5:0.95改善: {map50_95_improvement:+.2f}%")
                    print(f"   训练损失: box={epoch_data['train_box_loss']:.4f}, seg={epoch_data['train_seg_loss']:.4f}")
                    print(f"   学习率: {epoch_data['lr_pg0']:.6f}")
                    
                    # 判断改善情况
                    if map50_improvement >= 1.0:
                        print(f"   🎉 显著改善! 已达到1%目标")
                    elif map50_improvement >= 0.5:
                        print(f"   ⚖️ 小幅改善，继续观察")
                    elif map50_improvement >= 0.0:
                        print(f"   📈 微小改善")
                    else:
                        print(f"   ⚠️ 性能下降，可能需要早停")
                    
                    # 保存监控数据
                    monitoring_df = pd.DataFrame(monitoring_data)
                    monitoring_df.to_csv('results/continue_training_monitor.csv', index=False)
                    
                    # 生成对比图表
                    if current_epoch >= 2:
                        generate_comparison_plots(monitoring_df, baseline_map50, baseline_map50_95)
                    
                    last_epoch = current_epoch
                    
                    # 检查是否训练完成
                    if current_epoch >= 22:
                        print(f"\n🎉 继续训练完成! 总共{current_epoch}个epochs")
                        break
            
            # 等待10秒再检查
            time.sleep(10)
            
        except KeyboardInterrupt:
            print(f"\n⏹️ 监控被用户中断")
            break
        except Exception as e:
            print(f"⚠️ 监控错误: {e}")
            time.sleep(10)
    
    # 生成最终分析报告
    if monitoring_data:
        generate_final_analysis(monitoring_data, baseline_map50, baseline_map50_95)

def generate_comparison_plots(df, baseline_map50, baseline_map50_95):
    """生成对比图表"""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Continue Training Progress vs Baseline', fontsize=16)
    
    epochs = df['epoch']
    
    # mAP@0.5 对比
    ax = axes[0, 0]
    ax.plot(epochs, df['metrics_mAP50_B'], label='Continue Training', color='red', linewidth=2)
    ax.axhline(y=baseline_map50, color='blue', linestyle='--', label=f'Baseline ({baseline_map50:.4f})')
    ax.axhline(y=baseline_map50*1.01, color='green', linestyle=':', label=f'Target (+1%)')
    ax.set_title('mAP@0.5 Comparison')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('mAP@0.5')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # mAP@0.5:0.95 对比
    ax = axes[0, 1]
    ax.plot(epochs, df['metrics_mAP50_95_B'], label='Continue Training', color='red', linewidth=2)
    ax.axhline(y=baseline_map50_95, color='blue', linestyle='--', label=f'Baseline ({baseline_map50_95:.4f})')
    ax.set_title('mAP@0.5:0.95 Comparison')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('mAP@0.5:0.95')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 改善百分比
    ax = axes[1, 0]
    ax.plot(epochs, df['map50_improvement_percent'], label='mAP@0.5 Improvement', color='green', linewidth=2)
    ax.plot(epochs, df['map50_95_improvement_percent'], label='mAP@0.5:0.95 Improvement', color='orange', linewidth=2)
    ax.axhline(y=1.0, color='red', linestyle='--', label='1% Target')
    ax.set_title('Performance Improvement (%)')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Improvement (%)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 损失对比
    ax = axes[1, 1]
    ax.plot(epochs, df['train_box_loss'], label='Box Loss', color='blue')
    ax.plot(epochs, df['train_seg_loss'], label='Seg Loss', color='red')
    ax.plot(epochs, df['train_cls_loss'], label='Cls Loss', color='green')
    ax.set_title('Training Losses')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Loss')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('results/continue_training_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def generate_final_analysis(monitoring_data, baseline_map50, baseline_map50_95):
    """生成最终分析报告"""
    
    print(f"\n📋 生成继续训练最终分析...")
    
    df = pd.DataFrame(monitoring_data)
    final_epoch = df.iloc[-1]
    
    final_map50 = final_epoch['metrics_mAP50_B']
    final_map50_95 = final_epoch['metrics_mAP50_95_B']
    final_improvement_50 = final_epoch['map50_improvement_percent']
    final_improvement_50_95 = final_epoch['map50_95_improvement_percent']
    
    # 生成分析报告
    report = []
    report.append("# 🔄 继续训练最终分析报告")
    report.append("=" * 50)
    report.append("")
    report.append(f"**分析完成时间**: {final_epoch['timestamp']}")
    report.append(f"**继续训练轮数**: {final_epoch['epoch']}")
    report.append("")
    
    # 性能对比
    report.append("## 📊 性能对比分析")
    report.append("")
    report.append("| 指标 | 基线 (7 epochs) | 继续训练后 | 改善幅度 |")
    report.append("|------|------------------|------------|----------|")
    report.append(f"| mAP@0.5 | {baseline_map50:.4f} | {final_map50:.4f} | {final_improvement_50:+.2f}% |")
    report.append(f"| mAP@0.5:0.95 | {baseline_map50_95:.4f} | {final_map50_95:.4f} | {final_improvement_50_95:+.2f}% |")
    report.append("")
    
    # 结论和建议
    report.append("## 🎯 结论和建议")
    report.append("")
    
    if final_improvement_50 >= 1.0:
        report.append("### ✅ 继续训练成功!")
        report.append(f"- mAP@0.5提升了{final_improvement_50:.2f}%，达到了1%的目标")
        report.append("- **建议**: 继续训练是值得的，可以考虑进一步优化")
    elif final_improvement_50 >= 0.5:
        report.append("### ⚖️ 继续训练有小幅收益")
        report.append(f"- mAP@0.5提升了{final_improvement_50:.2f}%，有一定改善")
        report.append("- **建议**: 边际收益较小，可以停止或根据需求决定")
    elif final_improvement_50 >= 0.0:
        report.append("### 📈 继续训练收益微小")
        report.append(f"- mAP@0.5提升了{final_improvement_50:.2f}%，改善很小")
        report.append("- **建议**: 收益不明显，建议停止继续训练")
    else:
        report.append("### ⚠️ 继续训练无收益")
        report.append(f"- mAP@0.5下降了{abs(final_improvement_50):.2f}%")
        report.append("- **建议**: 使用之前的最佳模型，停止继续训练")
    
    report.append("")
    report.append("## 📈 训练趋势分析")
    report.append("")
    
    # 分析趋势
    if len(df) >= 3:
        recent_trend = df.tail(3)['map50_improvement_percent'].diff().mean()
        if recent_trend > 0:
            report.append("- **趋势**: 性能仍在改善中")
        elif recent_trend < -0.1:
            report.append("- **趋势**: 性能开始下降")
        else:
            report.append("- **趋势**: 性能趋于稳定")
    
    # 保存报告
    with open('results/continue_training_final_analysis.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"📋 最终分析报告已保存: results/continue_training_final_analysis.md")
    
    # 保存JSON数据
    analysis_data = {
        'baseline_performance': {
            'mAP50': float(baseline_map50),
            'mAP50_95': float(baseline_map50_95)
        },
        'final_performance': {
            'mAP50': float(final_map50),
            'mAP50_95': float(final_map50_95)
        },
        'improvements': {
            'mAP50_percent': float(final_improvement_50),
            'mAP50_95_percent': float(final_improvement_50_95)
        },
        'conclusion': 'beneficial' if final_improvement_50 >= 1.0 else 'marginal' if final_improvement_50 >= 0.5 else 'minimal'
    }
    
    with open('results/continue_training_analysis.json', 'w') as f:
        json.dump(analysis_data, f, indent=2)
    
    print(f"📊 分析数据已保存: results/continue_training_analysis.json")

if __name__ == "__main__":
    # 确保结果目录存在
    Path("results").mkdir(exist_ok=True)
    
    print("🚀 启动继续训练监控...")
    monitor_continue_training()
