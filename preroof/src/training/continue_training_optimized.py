#!/usr/bin/env python3
"""
继续训练脚本 - 优化版本
Continue Training Script - Optimized Version

从现有的最佳权重继续训练，观察是否还有提升空间
策略：10-15个epochs + 早停机制 + 性能监控
"""

import os
import sys
import torch
import yaml
from pathlib import Path
from ultralytics import YOLO

def check_existing_training():
    """检查现有训练结果"""
    print("🔍 检查现有训练结果...")
    
    best_model_path = "runs/segment/improved_training_compatible/weights/best.pt"
    last_model_path = "runs/segment/improved_training_compatible/weights/last.pt"
    results_csv = "runs/segment/improved_training_compatible/results.csv"
    
    if not os.path.exists(best_model_path):
        print(f"❌ 未找到最佳模型: {best_model_path}")
        return None, None
    
    if not os.path.exists(results_csv):
        print(f"❌ 未找到训练结果: {results_csv}")
        return None, None
    
    # 读取最后的性能指标
    import pandas as pd
    df = pd.read_csv(results_csv)
    last_epoch = len(df) - 1  # 减1因为有header
    last_metrics = df.iloc[-1]
    
    print(f"📊 当前训练状态:")
    print(f"   已完成epochs: {last_epoch}")
    print(f"   当前mAP@0.5: {last_metrics['metrics/mAP50(B)']:.4f}")
    print(f"   当前mAP@0.5:0.95: {last_metrics['metrics/mAP50-95(B)']:.4f}")
    print(f"   当前box_loss: {last_metrics['train/box_loss']:.4f}")
    print(f"   当前seg_loss: {last_metrics['train/seg_loss']:.4f}")
    
    return best_model_path, last_metrics

def continue_training_with_monitoring():
    """继续训练并监控性能提升"""
    
    print("🚀 开始继续训练 - 观察性能提升潜力")
    print("="*60)
    
    # 检查现有训练
    best_model_path, baseline_metrics = check_existing_training()
    if not best_model_path:
        return None
    
    # 记录基线性能
    baseline_map50 = baseline_metrics['metrics/mAP50(B)']
    baseline_map50_95 = baseline_metrics['metrics/mAP50-95(B)']
    
    print(f"\n🎯 继续训练策略:")
    print(f"   目标epochs: 10-15个额外epochs")
    print(f"   早停耐心值: 10 epochs")
    print(f"   最小改善阈值: 1% mAP@0.5")
    print(f"   基线mAP@0.5: {baseline_map50:.4f}")
    print(f"   目标mAP@0.5: >{baseline_map50*1.01:.4f} (+1%)")
    
    # 数据配置
    DATA_YAML = "data/raw/new-2-1/data.yaml"
    
    if not os.path.exists(DATA_YAML):
        print(f"❌ 数据集配置文件不存在: {DATA_YAML}")
        return None
    
    # 加载最佳模型继续训练
    print(f"\n🔧 加载最佳模型: {best_model_path}")
    model = YOLO(best_model_path)
    
    # 检查GPU
    device = 0 if torch.cuda.is_available() else 'cpu'
    print(f"使用设备: {device}")
    
    print(f"\n🚀 开始继续训练...")
    print("="*60)
    
    try:
        results = model.train(
            # 基本配置
            data=DATA_YAML,
            epochs=22,                    # 从7继续到22 (额外15个epochs)
            imgsz=896,                    # 保持相同的图像尺寸
            batch=16,
            device=device,
            
            # 优化器配置 (保持一致)
            optimizer='AdamW',
            lr0=5e-5,                     # 降低学习率 (从1e-4降到5e-5)
            lrf=0.01,
            momentum=0.937,
            weight_decay=0.0005,
            cos_lr=True,                  # 继续余弦退火
            warmup_epochs=1,              # 减少warmup (因为是继续训练)
            
            # 损失函数权重 (保持优化后的配置)
            cls=1.2,
            box=5.0,
            dfl=2.5,
            
            # IoU配置
            iou=0.45,
            
            # 数据增强 (稍微减少，因为模型已经较成熟)
            mosaic=0.5,                   # 从0.7降到0.5
            copy_paste=0.1,               # 从0.2降到0.1
            close_mosaic=5,               # 最后5个epoch关闭mosaic
            degrees=8,                    # 从12降到8
            translate=0.05,               # 从0.1降到0.05
            scale=0.3,                    # 从0.5降到0.3
            shear=1.0,                    # 从2.0降到1.0
            flipud=0.2,                   # 从0.3降到0.2
            fliplr=0.5,                   # 保持
            hsv_h=0.01,                   # 从0.02降到0.01
            hsv_s=0.4,                    # 从0.6降到0.4
            hsv_v=0.3,                    # 从0.4降到0.3
            
            # 早停和监控
            patience=10,                  # 10个epochs无改善则停止
            save_period=1,                # 每个epoch保存
            amp=True,
            workers=0,
            cache=True,
            
            # 输出配置
            project='runs/segment',
            name='continue_training_optimized',
            plots=True,
            save=True,
            resume=False,                 # 不使用resume，而是从best.pt开始新的训练
        )
        
        print(f"\n🎉 继续训练完成!")
        print("="*60)
        
        # 分析训练结果
        if results:
            # 检查新的训练结果
            new_results_dir = Path("runs/segment/continue_training_optimized")
            new_results_csv = new_results_dir / "results.csv"
            
            if new_results_csv.exists():
                import pandas as pd
                new_df = pd.read_csv(new_results_csv)
                final_metrics = new_df.iloc[-1]
                
                final_map50 = final_metrics['metrics/mAP50(B)']
                final_map50_95 = final_metrics['metrics/mAP50-95(B)']
                
                # 计算改善
                map50_improvement = ((final_map50 - baseline_map50) / baseline_map50) * 100
                map50_95_improvement = ((final_map50_95 - baseline_map50_95) / baseline_map50_95) * 100
                
                print(f"📊 继续训练结果分析:")
                print(f"   基线mAP@0.5: {baseline_map50:.4f}")
                print(f"   最终mAP@0.5: {final_map50:.4f}")
                print(f"   mAP@0.5改善: {map50_improvement:+.2f}%")
                print(f"   ")
                print(f"   基线mAP@0.5:0.95: {baseline_map50_95:.4f}")
                print(f"   最终mAP@0.5:0.95: {final_map50_95:.4f}")
                print(f"   mAP@0.5:0.95改善: {map50_95_improvement:+.2f}%")
                
                # 判断是否值得继续
                if map50_improvement >= 1.0:
                    print(f"\n✅ 继续训练有效! mAP@0.5提升了{map50_improvement:.2f}%")
                    print(f"   建议: 可以考虑进一步训练")
                elif map50_improvement >= 0.5:
                    print(f"\n⚖️ 继续训练有小幅提升: {map50_improvement:.2f}%")
                    print(f"   建议: 边际收益较小，可以停止")
                else:
                    print(f"\n⚠️ 继续训练收益很小: {map50_improvement:.2f}%")
                    print(f"   建议: 停止训练，使用之前的最佳模型")
                
                # 检查最佳模型
                best_model = new_results_dir / "weights" / "best.pt"
                if best_model.exists():
                    size_mb = best_model.stat().st_size / (1024 * 1024)
                    print(f"\n💾 新的最佳模型: {best_model} ({size_mb:.1f}MB)")
                
                # 保存对比报告
                comparison_report = {
                    'baseline_metrics': {
                        'mAP50': float(baseline_map50),
                        'mAP50_95': float(baseline_map50_95)
                    },
                    'final_metrics': {
                        'mAP50': float(final_map50),
                        'mAP50_95': float(final_map50_95)
                    },
                    'improvements': {
                        'mAP50_percent': float(map50_improvement),
                        'mAP50_95_percent': float(map50_95_improvement)
                    },
                    'recommendation': 'continue' if map50_improvement >= 1.0 else 'stop'
                }
                
                import json
                with open('results/continue_training_analysis.json', 'w') as f:
                    json.dump(comparison_report, f, indent=2)
                
                print(f"📋 详细对比报告已保存: results/continue_training_analysis.json")
        
        return results
        
    except Exception as e:
        print(f"❌ 继续训练失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """主函数"""
    print("🔄 继续训练 - 性能提升验证")
    print("="*50)
    
    # 确保结果目录存在
    Path("results").mkdir(exist_ok=True)
    
    try:
        results = continue_training_with_monitoring()
        if results:
            print(f"\n✅ 继续训练流程完成!")
            print(f"📁 新训练结果: runs/segment/continue_training_optimized/")
        else:
            print(f"\n❌ 继续训练流程失败!")
    except KeyboardInterrupt:
        print(f"\n⏹️ 训练被用户中断")
    except Exception as e:
        print(f"\n💥 发生未预期错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
