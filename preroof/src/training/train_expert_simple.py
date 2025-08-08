#!/usr/bin/env python3
"""
简化版专家改进训练脚本
Simplified expert improved training script

直接运行，避免复杂的模块导入
"""

import os
import sys
import glob
import yaml
import numpy as np
from collections import Counter
from ultralytics import YOLO
import torch

print("🛰️ 专家改进版 - 卫星图像分割检测训练")
print("=" * 60)

# 检查环境
print("🔍 环境检查:")
print(f"   Python版本: {sys.version}")
print(f"   PyTorch版本: {torch.__version__}")
print(f"   GPU可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"   GPU名称: {torch.cuda.get_device_name(0)}")
    print(f"   CUDA版本: {torch.version.cuda}")

# 下载数据集
print("\n📥 准备数据集...")
try:
    from roboflow import Roboflow
    
    # 使用同事提供的更新API密钥
    rf = Roboflow(api_key="EkXslogyvSMHiOP3MK94")
    project = rf.workspace("a-imc4u").project("new-2-6zp4h")
    dataset = project.version(1).download("yolov8")
    
    DATA_YAML = os.path.join(dataset.location, "data.yaml")
    print(f"✅ 数据集下载完成: {dataset.location}")
    
except Exception as e:
    print(f"❌ 数据集下载失败: {e}")
    print("💡 请检查网络连接和API密钥")
    sys.exit(1)

# 读取数据配置
with open(DATA_YAML, 'r') as f:
    data_config = yaml.safe_load(f)

class_names = data_config['names']
num_classes = data_config['nc']

print(f"\n📊 数据集信息:")
print(f"   类别数量: {num_classes}")
print(f"   类别名称: {class_names}")
print(f"   0: {class_names[0]} - 裸地")
print(f"   1: {class_names[1]} - 农地")
print(f"   2: {class_names[2]} - 水田")
print(f"   3: {class_names[3]} - 屋顶")

# 专家改进1: 自动计算类别权重
print("\n🎯 专家改进1: 自动计算类别权重...")

# 获取训练标签文件
train_path = data_config['train']
if os.path.isfile(train_path):
    train_dir = os.path.dirname(train_path)
else:
    train_dir = train_path

label_dir = os.path.join(os.path.dirname(train_dir), 'labels') if 'images' in train_dir else os.path.join(train_dir, 'labels')
label_files = glob.glob(os.path.join(label_dir, '*.txt'))

# 统计类别分布
counter = Counter()
for f in label_files:
    with open(f) as r:
        for line in r:
            if line.strip():
                cls_id = int(line.split()[0])
                counter[cls_id] += 1

print("📊 原始类别分布:")
for i in range(num_classes):
    count = counter.get(i, 0)
    print(f"   {class_names[i]:12}: {count:6d} 个实例")

# 有效样本数方法计算权重 (Cui et al., 2019)
beta = 0.999
freq = np.array([counter.get(i, 0) for i in range(num_classes)], dtype=float)
freq = np.maximum(freq, 1)  # 避免除零

eff_num = 1 - np.power(beta, freq)
cls_weights = (1 - beta) / eff_num
cls_weights = cls_weights / cls_weights.mean()  # 归一化

print("\n🎯 自动计算的类别权重:")
for i, (name, weight) in enumerate(zip(class_names, cls_weights)):
    print(f"   {name:12}: {weight:.3f}")

# 专家改进2&3: 统一解像度 + 现代学习率策略
IMG_SIZE = 768  # 统一解像度
print(f"\n📐 专家改进2: 统一解像度 {IMG_SIZE}x{IMG_SIZE}")
print("🔄 专家改进3: 余弦退火 + AdamW 学习率策略")

# 加载模型
print("\n🔧 加载预训练模型...")
model = YOLO('yolov8m-seg.pt')
print("✅ 模型加载完成")

# 专家改进版训练配置
print("\n🚀 开始专家改进版训练...")
print("🎯 专家改进配置:")
print(f"   ✅ 自动类别权重: {cls_weights.round(3).tolist()}")
print(f"   ✅ 统一解像度: {IMG_SIZE}")
print(f"   ✅ 学习率策略: AdamW + 余弦退火")
print(f"   ✅ 数据增强: 分割友好 (低Mosaic + Copy-Paste)")

try:
    results = model.train(
        # 基本配置
        data=DATA_YAML,
        epochs=30,                   # 本地测试用30轮
        imgsz=IMG_SIZE,              # 专家改进: 统一解像度
        batch=16,                    # RTX 4090可以处理
        device='auto',               # 自动使用GPU
        
        # 专家改进: 自动类别权重
        class_weights=cls_weights.tolist(),
        
        # 专家改进: 现代学习率策略
        optimizer='AdamW',
        lr0=2e-4,
        cos_lr=True,
        warmup_epochs=3,
        warmup_momentum=0.8,
        warmup_bias_lr=0.1,
        
        # 专家改进: 分割友好数据增强
        mosaic=0.25,                 # 大幅降低 (原0.8)
        copy_paste=0.5,              # 分割专用增强
        close_mosaic=0,
        mixup=0.0,
        
        # HSV色彩增强
        hsv_h=0.02,
        hsv_s=0.7,
        hsv_v=0.4,
        
        # 几何变换
        degrees=10.0,
        translate=0.1,
        scale=0.5,
        shear=0.0,
        perspective=0.0,
        flipud=0.5,
        fliplr=0.5,
        
        # 训练控制
        patience=15,
        save_period=-1,
        amp=True,                    # 混合精度训练
        
        # 输出配置
        project='runs/segment',
        name='expert_rtx4090',
        plots=True,
        save=True
    )
    
    print("\n🎉 专家改进版训练完成!")
    print(f"📁 最佳模型: {results.best}")
    print(f"📊 结果目录: runs/segment/expert_rtx4090/")
    
    # 显示改进效果
    print("\n🎯 专家改进效果总结:")
    print("   ✅ 自动类别权重 - 基于真实数据分布")
    print("   ✅ 统一解像度768 - 训练验证一致")
    print("   ✅ 余弦退火学习率 - 更稳定收敛")
    print("   ✅ 分割友好增强 - 更好边缘质量")
    print("   ✅ RTX 4090加速 - 高效训练")
    
    print("\n💡 下一步:")
    print("   1. 查看训练曲线: runs/segment/expert_rtx4090/results.png")
    print("   2. 查看混淆矩阵: runs/segment/expert_rtx4090/confusion_matrix.png")
    print("   3. 测试推理效果")
    
except Exception as e:
    print(f"❌ 训练失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n🎊 专家改进版训练成功完成!")
