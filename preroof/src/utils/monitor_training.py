#!/usr/bin/env python3
"""
训练监控脚本
Training Monitor Script

实时监控训练进度，保存关键指标和状态
"""

import os
import time
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import json
from datetime import datetime

def monitor_training_progress():
    """监控训练进度"""
    
    training_dir = Path("runs/segment/improved_training_compatible")
    results_csv = training_dir / "results.csv"
    
    print("🔍 训练监控启动...")
    print(f"监控目录: {training_dir}")
    
    last_epoch = 0
    monitoring_data = []
    
    while True:
        try:
            if results_csv.exists():
                # 读取训练结果
                df = pd.read_csv(results_csv)
                current_epoch = len(df)
                
                if current_epoch > last_epoch:
                    # 新的epoch完成
                    latest_row = df.iloc[-1]
                    
                    # 提取关键指标
                    epoch_data = {
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'epoch': current_epoch,
                        'train_box_loss': latest_row.get('train/box_loss', 0),
                        'train_seg_loss': latest_row.get('train/seg_loss', 0),
                        'train_cls_loss': latest_row.get('train/cls_loss', 0),
                        'train_dfl_loss': latest_row.get('train/dfl_loss', 0),
                        'val_box_loss': latest_row.get('val/box_loss', 0),
                        'val_seg_loss': latest_row.get('val/seg_loss', 0),
                        'val_cls_loss': latest_row.get('val/cls_loss', 0),
                        'val_dfl_loss': latest_row.get('val/dfl_loss', 0),
                        'metrics_precision_B': latest_row.get('metrics/precision(B)', 0),
                        'metrics_recall_B': latest_row.get('metrics/recall(B)', 0),
                        'metrics_mAP50_B': latest_row.get('metrics/mAP50(B)', 0),
                        'metrics_mAP50_95_B': latest_row.get('metrics/mAP50-95(B)', 0),
                        'lr_pg0': latest_row.get('lr/pg0', 0),
                        'lr_pg1': latest_row.get('lr/pg1', 0),
                        'lr_pg2': latest_row.get('lr/pg2', 0)
                    }
                    
                    monitoring_data.append(epoch_data)
                    
                    # 打印进度
                    print(f"\n📊 Epoch {current_epoch}/60 完成:")
                    print(f"   训练损失: box={epoch_data['train_box_loss']:.4f}, seg={epoch_data['train_seg_loss']:.4f}, cls={epoch_data['train_cls_loss']:.4f}")
                    print(f"   验证损失: box={epoch_data['val_box_loss']:.4f}, seg={epoch_data['val_seg_loss']:.4f}, cls={epoch_data['val_cls_loss']:.4f}")
                    print(f"   验证指标: mAP50={epoch_data['metrics_mAP50_B']:.4f}, mAP50-95={epoch_data['metrics_mAP50_95_B']:.4f}")
                    print(f"   学习率: {epoch_data['lr_pg0']:.6f}")
                    
                    # 保存监控数据
                    monitoring_df = pd.DataFrame(monitoring_data)
                    monitoring_df.to_csv('results/training_monitor.csv', index=False)
                    
                    # 生成实时图表
                    if current_epoch >= 2:
                        generate_realtime_plots(monitoring_df)
                    
                    last_epoch = current_epoch
                    
                    # 检查是否训练完成
                    if current_epoch >= 60:
                        print(f"\n🎉 训练完成! 总共{current_epoch}个epochs")
                        break
            
            # 等待10秒再检查
            time.sleep(10)
            
        except KeyboardInterrupt:
            print(f"\n⏹️ 监控被用户中断")
            break
        except Exception as e:
            print(f"⚠️ 监控错误: {e}")
            time.sleep(10)
    
    # 生成最终报告
    if monitoring_data:
        generate_final_report(monitoring_data)

def generate_realtime_plots(df):
    """生成实时训练图表"""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('实时训练监控 (Real-time Training Monitor)', fontsize=16)
    
    epochs = df['epoch']
    
    # 损失曲线
    ax = axes[0, 0]
    ax.plot(epochs, df['train_box_loss'], label='Train Box Loss', color='blue')
    ax.plot(epochs, df['val_box_loss'], label='Val Box Loss', color='red')
    ax.set_title('Box Loss')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Loss')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 分类损失
    ax = axes[0, 1]
    ax.plot(epochs, df['train_cls_loss'], label='Train Cls Loss', color='blue')
    ax.plot(epochs, df['val_cls_loss'], label='Val Cls Loss', color='red')
    ax.set_title('Classification Loss')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Loss')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # mAP指标
    ax = axes[1, 0]
    ax.plot(epochs, df['metrics_mAP50_B'], label='mAP@0.5', color='green')
    ax.plot(epochs, df['metrics_mAP50_95_B'], label='mAP@0.5:0.95', color='orange')
    ax.set_title('mAP Metrics')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('mAP')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 学习率
    ax = axes[1, 1]
    ax.plot(epochs, df['lr_pg0'], label='Learning Rate', color='purple')
    ax.set_title('Learning Rate Schedule')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Learning Rate')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('results/realtime_training_monitor.png', dpi=300, bbox_inches='tight')
    plt.close()

def generate_final_report(monitoring_data):
    """生成最终训练报告"""
    
    print(f"\n📋 生成最终训练报告...")
    
    df = pd.DataFrame(monitoring_data)
    final_epoch = df.iloc[-1]
    
    # 计算改进指标
    initial_epoch = df.iloc[0] if len(df) > 1 else final_epoch
    
    report = []
    report.append("# 🏠 改进版训练最终报告")
    report.append("=" * 50)
    report.append("")
    report.append(f"**训练完成时间**: {final_epoch['timestamp']}")
    report.append(f"**总训练轮数**: {final_epoch['epoch']}")
    report.append("")
    
    # 最终性能指标
    report.append("## 📊 最终性能指标")
    report.append("")
    report.append("| 指标 | 数值 |")
    report.append("|------|------|")
    report.append(f"| mAP@0.5 | {final_epoch['metrics_mAP50_B']:.4f} |")
    report.append(f"| mAP@0.5:0.95 | {final_epoch['metrics_mAP50_95_B']:.4f} |")
    report.append(f"| Precision | {final_epoch['metrics_precision_B']:.4f} |")
    report.append(f"| Recall | {final_epoch['metrics_recall_B']:.4f} |")
    report.append("")
    
    # 损失收敛情况
    report.append("## 📉 损失收敛情况")
    report.append("")
    report.append("| 损失类型 | 初始值 | 最终值 | 改善幅度 |")
    report.append("|----------|--------|--------|----------|")
    
    for loss_type in ['box_loss', 'seg_loss', 'cls_loss', 'dfl_loss']:
        initial_val = initial_epoch[f'train_{loss_type}']
        final_val = final_epoch[f'train_{loss_type}']
        improvement = ((initial_val - final_val) / initial_val) * 100
        report.append(f"| {loss_type} | {initial_val:.4f} | {final_val:.4f} | {improvement:.1f}% |")
    
    report.append("")
    
    # 训练配置总结
    report.append("## 🔧 训练配置总结")
    report.append("")
    report.append("- **模型**: YOLOv8l-seg (45.9M参数)")
    report.append("- **图像尺寸**: 896x896")
    report.append("- **批次大小**: 16")
    report.append("- **优化器**: AdamW")
    report.append("- **学习率**: 1e-4 (余弦退火)")
    report.append("- **损失权重**: cls=1.2, box=5.0, dfl=2.5")
    report.append("- **数据增强**: copy_paste=0.2, mosaic=0.7")
    report.append("")
    
    # 保存报告
    with open('results/final_training_report.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"📋 最终报告已保存: results/final_training_report.md")
    
    # 保存训练配置JSON
    config_summary = {
        'training_completed': final_epoch['timestamp'],
        'total_epochs': final_epoch['epoch'],
        'final_metrics': {
            'mAP50': final_epoch['metrics_mAP50_B'],
            'mAP50_95': final_epoch['metrics_mAP50_95_B'],
            'precision': final_epoch['metrics_precision_B'],
            'recall': final_epoch['metrics_recall_B']
        },
        'final_losses': {
            'box_loss': final_epoch['train_box_loss'],
            'seg_loss': final_epoch['train_seg_loss'],
            'cls_loss': final_epoch['train_cls_loss'],
            'dfl_loss': final_epoch['train_dfl_loss']
        },
        'improvements_implemented': [
            'Upgraded to YOLOv8l-seg',
            'Increased image size to 896',
            'Optimized loss weights (cls=1.2, box=5.0, dfl=2.5)',
            'Enhanced data augmentation (copy_paste=0.2)',
            'Cosine annealing learning rate',
            'AdamW optimizer'
        ]
    }
    
    with open('results/training_summary.json', 'w') as f:
        json.dump(config_summary, f, indent=2)
    
    print(f"📊 训练总结已保存: results/training_summary.json")

if __name__ == "__main__":
    # 确保结果目录存在
    Path("results").mkdir(exist_ok=True)
    
    print("🚀 启动训练监控...")
    monitor_training_progress()
