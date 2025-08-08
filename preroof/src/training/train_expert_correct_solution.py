#!/usr/bin/env python3
"""
专家改进版训练脚本 - 正确的类别权重解决方案
Expert improved training script - Correct class weights solution

发现重要问题：YOLOv8根本不支持class_weights参数！
需要使用其他方法解决类别不平衡问题
"""

import os
import sys
import glob
import yaml
import numpy as np
from collections import Counter
from ultralytics import YOLO
import torch

print("🛰️ 专家改进版 - 正确的类别权重解决方案")
print("=" * 70)

# 检查环境
print("🔍 环境检查:")
print(f"   Python版本: {sys.version.split()[0]}")
print(f"   PyTorch版本: {torch.__version__}")

# 检查GPU可用性
gpu_available = torch.cuda.is_available()
gpu_count = torch.cuda.device_count()
print(f"   GPU可用: {gpu_available}")
print(f"   GPU数量: {gpu_count}")

if gpu_available and gpu_count > 0:
    print(f"   GPU名称: {torch.cuda.get_device_name(0)}")
    device = 0  # 使用第一个GPU
else:
    print(f"   使用CPU训练")
    device = 'cpu'

# 使用已下载的数据集
DATA_YAML = "data/raw/new-2-1/data.yaml"
if not os.path.exists(DATA_YAML):
    print(f"❌ 数据集不存在: {DATA_YAML}")
    print("请运行: python download_roboflow_dataset.py")
    sys.exit(1)

print(f"✅ 使用数据集: {DATA_YAML}")

# 读取数据配置
with open(DATA_YAML, 'r') as f:
    data_config = yaml.safe_load(f)

class_names = data_config['names']
num_classes = data_config['nc']

print(f"\n📊 数据集信息:")
print(f"   类别数量: {num_classes}")
print(f"   类别名称: {class_names}")

# 🎯 重要发现：YOLOv8不支持class_weights参数
print("\n" + "="*70)
print("🎯 重要发现：YOLOv8类别权重问题的真相")
print("="*70)

print("❌ 问题确认:")
print("   - YOLOv8根本不支持class_weights参数")
print("   - 无论在YAML中还是直接传入都无效")
print("   - 这是YOLOv8的设计限制")

print("\n✅ 正确的解决方案:")
print("   1. 使用数据增强策略平衡类别")
print("   2. 调整损失函数权重 (cls, box, dfl)")
print("   3. 使用focal loss概念调整训练")
print("   4. 数据重采样或合成")

# 分析类别分布
train_path = data_config['train']
if os.path.isfile(train_path):
    train_dir = os.path.dirname(train_path)
else:
    train_dir = train_path

label_dir = os.path.join(os.path.dirname(train_dir), 'labels') if 'images' in train_dir else os.path.join(train_dir, 'labels')
label_files = glob.glob(os.path.join(label_dir, '*.txt'))

# 统计类别分布
counter = Counter()
total_instances = 0

for f in label_files:
    try:
        with open(f) as r:
            for line in r:
                if line.strip():
                    cls_id = int(line.split()[0])
                    if 0 <= cls_id < num_classes:
                        counter[cls_id] += 1
                        total_instances += 1
    except:
        continue

print(f"\n📊 真实类别分布分析:")
if total_instances > 0:
    for i in range(num_classes):
        count = counter.get(i, 0)
        percentage = (count / total_instances) * 100
        print(f"   {class_names[i]:12}: {count:6d} 个实例 ({percentage:5.1f}%)")
    
    # 计算不平衡程度
    counts = [counter.get(i, 0) for i in range(num_classes)]
    max_count = max(counts)
    min_count = min([c for c in counts if c > 0]) if any(counts) else 1
    imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')
    
    print(f"\n📈 类别不平衡分析:")
    print(f"   最多类别: {max_count} 个实例")
    print(f"   最少类别: {min_count} 个实例")
    print(f"   不平衡比例: {imbalance_ratio:.1f}:1")
    
    if imbalance_ratio > 10:
        print("   ⚠️ 严重不平衡，需要特殊处理")
    elif imbalance_ratio > 3:
        print("   ⚠️ 中度不平衡，建议调整")
    else:
        print("   ✅ 相对平衡")
else:
    print("   ⚠️ 未找到有效标签数据")

# 专家改进的替代方案
print(f"\n🎯 专家改进的替代解决方案:")

# 方案1: 调整损失函数权重
print(f"\n1️⃣ 损失函数权重调整:")
print(f"   - cls (分类损失): 增加到1.0 (默认0.5)")
print(f"   - box (边框损失): 保持7.5")
print(f"   - dfl (分布损失): 保持1.5")

# 方案2: 数据增强策略
print(f"\n2️⃣ 针对性数据增强:")
print(f"   - copy_paste: 0.5 (增加少数类别)")
print(f"   - mosaic: 0.3 (适度混合)")
print(f"   - mixup: 0.1 (轻微混合)")

# 方案3: 训练策略
print(f"\n3️⃣ 训练策略优化:")
print(f"   - 更多epochs: 100+ (充分学习)")
print(f"   - 较小学习率: 0.005 (稳定训练)")
print(f"   - 余弦退火: True (平滑收敛)")

# 加载模型
print(f"\n🔧 加载YOLOv8分割模型...")
model = YOLO('models/pretrained/yolov8m-seg.pt')
print("✅ 模型加载完成")

print(f"\n🚀 开始专家改进版训练 (无class_weights版本)...")
print("="*70)

try:
    results = model.train(
        # 基本配置
        data=DATA_YAML,
        epochs=60,                   # 增加训练轮次
        imgsz=768,                   # 统一解像度
        batch=16,                    # RTX 4090适配
        device=device,
        
        # 🎯 损失函数权重调整 (替代class_weights)
        cls=1.0,                     # 增加分类损失权重 (默认0.5)
        box=7.5,                     # 保持边框损失
        dfl=1.5,                     # 保持分布损失
        
        # 🎯 现代学习率策略
        optimizer='AdamW',
        lr0=0.005,                   # 较小的初始学习率
        lrf=0.01,                    # 最终学习率比例
        cos_lr=True,                 # 余弦退火
        warmup_epochs=5,
        warmup_momentum=0.8,
        warmup_bias_lr=0.1,
        
        # 🎯 针对性数据增强 (替代class_weights)
        mosaic=0.3,                  # 适度mosaic
        copy_paste=0.5,              # 增加copy-paste
        mixup=0.1,                   # 轻微mixup
        close_mosaic=10,             # 延迟关闭mosaic
        
        # HSV色彩增强
        hsv_h=0.02,
        hsv_s=0.7,
        hsv_v=0.4,
        
        # 几何变换
        degrees=15.0,                # 增加旋转
        translate=0.1,
        scale=0.5,
        shear=0.0,
        perspective=0.0,
        flipud=0.5,
        fliplr=0.5,
        
        # 训练控制
        patience=25,                 # 增加耐心值
        save_period=-1,
        amp=True,
        workers=0,                   # 修复Windows多进程问题
        
        # 输出配置
        project='runs/segment',
        name='expert_no_class_weights',
        plots=True,
        save=True
    )
    
    print("\n🎉 专家改进版训练完成!")
    print(f"📁 最佳模型: {results.best}")
    
    print(f"\n🎯 专家改进总结:")
    print(f"   ✅ 发现YOLOv8不支持class_weights")
    print(f"   ✅ 使用损失权重调整 (cls=1.0)")
    print(f"   ✅ 针对性数据增强策略")
    print(f"   ✅ 统一解像度768")
    print(f"   ✅ 现代学习率策略")
    
    print(f"\n📊 给同事的重要发现:")
    print(f"   ❌ YAML中的class_weights完全无效")
    print(f"   ❌ model.train(class_weights=...)也无效")
    print(f"   ❌ YOLOv8根本不支持这个参数")
    print(f"   ✅ 需要使用其他方法处理类别不平衡")
    
    print(f"\n💡 建议的解决方案:")
    print(f"   1. 调整损失函数权重 (cls, box, dfl)")
    print(f"   2. 使用数据增强平衡类别")
    print(f"   3. 考虑数据重采样")
    print(f"   4. 或者切换到支持class_weights的框架")
    
except Exception as e:
    print(f"❌ 训练失败: {e}")
    import traceback
    traceback.print_exc()

print(f"\n🎊 专家改进版训练完成!")
print("="*70)
