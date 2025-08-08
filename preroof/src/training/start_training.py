#!/usr/bin/env python3
"""
快速启动训练脚本
Quick start training script
"""

import os
import sys
import subprocess
from pathlib import Path
import time

def check_requirements():
    """检查训练前的要求"""
    print("🔍 检查训练环境...")
    
    # 检查数据集
    data_path = Path("data/raw/new-2-1")
    if not data_path.exists():
        print("❌ 数据集不存在: data/raw/new-2-1")
        return False
    
    train_images = list((data_path / "train" / "images").glob("*.jpg"))
    if len(train_images) == 0:
        print("❌ 训练图像不存在")
        return False
    
    print(f"✅ 数据集检查通过: {len(train_images)} 张训练图像")
    
    # 检查预训练模型
    model_path = Path("models/pretrained/yolov8m-seg.pt")
    if not model_path.exists():
        print("❌ 预训练模型不存在: models/pretrained/yolov8m-seg.pt")
        return False
    
    print("✅ 预训练模型检查通过")
    
    # 检查训练脚本
    script_path = Path("train_expert_correct_solution.py")
    if not script_path.exists():
        print("❌ 训练脚本不存在: train_expert_correct_solution.py")
        return False
    
    print("✅ 训练脚本检查通过")
    
    return True

def start_training():
    """启动训练"""
    print("\n🚀 启动专家改进版训练...")
    print("="*50)
    
    # 记录开始时间
    start_time = time.time()
    
    try:
        # 运行训练脚本
        result = subprocess.run([
            sys.executable, "train_expert_correct_solution.py"
        ], check=True, capture_output=False)
        
        # 计算训练时间
        end_time = time.time()
        duration = end_time - start_time
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        
        print(f"\n🎉 训练完成!")
        print(f"⏱️ 总用时: {hours}小时 {minutes}分钟")
        
        # 检查训练结果
        check_results()
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 训练失败: {e}")
        return False
    except KeyboardInterrupt:
        print(f"\n⏹️ 训练被用户中断")
        return False
    
    return True

def check_results():
    """检查训练结果"""
    print("\n📊 检查训练结果...")
    
    runs_dir = Path("runs/segment")
    if not runs_dir.exists():
        print("❌ 训练结果目录不存在")
        return
    
    # 找到最新的训练结果
    latest_run = None
    latest_time = 0
    
    for run_dir in runs_dir.iterdir():
        if run_dir.is_dir():
            weights_dir = run_dir / "weights"
            if weights_dir.exists() and any(weights_dir.iterdir()):
                mtime = run_dir.stat().st_mtime
                if mtime > latest_time:
                    latest_time = mtime
                    latest_run = run_dir
    
    if latest_run:
        print(f"✅ 找到训练结果: {latest_run.name}")
        
        # 检查权重文件
        weights_dir = latest_run / "weights"
        best_pt = weights_dir / "best.pt"
        last_pt = weights_dir / "last.pt"
        
        if best_pt.exists():
            size_mb = best_pt.stat().st_size / (1024 * 1024)
            print(f"   📦 最佳模型: best.pt ({size_mb:.1f}MB)")
        
        if last_pt.exists():
            size_mb = last_pt.stat().st_size / (1024 * 1024)
            print(f"   📦 最终模型: last.pt ({size_mb:.1f}MB)")
        
        # 检查训练图表
        results_png = latest_run / "results.png"
        if results_png.exists():
            print(f"   📈 训练图表: results.png")
        
        print(f"\n📁 完整结果路径: {latest_run}")
        
    else:
        print("❌ 未找到有效的训练结果")

def main():
    """主函数"""
    print("🏠 屋顶检测项目 - 快速启动训练")
    print("="*50)
    
    # 检查环境
    if not check_requirements():
        print("\n❌ 环境检查失败，请先解决上述问题")
        return
    
    # 确认开始训练
    print(f"\n📋 训练配置:")
    print(f"   - 模型: YOLOv8m-seg")
    print(f"   - 图像尺寸: 768x768")
    print(f"   - 批次大小: 16")
    print(f"   - 学习率: 0.005")
    print(f"   - Epochs: 60")
    print(f"   - 预计时间: 2-3小时")
    
    response = input(f"\n🤔 确认开始训练? (y/N): ").strip().lower()
    if response not in ['y', 'yes', '是']:
        print("⏹️ 训练已取消")
        return
    
    # 开始训练
    success = start_training()
    
    if success:
        print(f"\n🎊 训练流程完成!")
        print(f"💡 下一步可以:")
        print(f"   1. 查看训练结果图表")
        print(f"   2. 运行模型评估")
        print(f"   3. 生成可视化结果")
    else:
        print(f"\n😞 训练未能完成，请检查错误信息")

if __name__ == "__main__":
    main()
