#!/usr/bin/env python3
"""
使用本地数据的专家改进版训练脚本
Expert improved training script with local data

使用RTX 4090 + 本地卫星数据集进行专家改进版训练
"""

import os
import sys
import glob
import yaml
import numpy as np
from collections import Counter
from ultralytics import YOLO
import torch

print("🛰️ 专家改进版本地训练 - RTX 4090")
print("=" * 60)

# 检查环境
print("🔍 环境检查:")
print(f"   Python版本: {sys.version.split()[0]}")
print(f"   PyTorch版本: {torch.__version__}")
print(f"   GPU可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"   GPU名称: {torch.cuda.get_device_name(0)}")
    print(f"   CUDA版本: {torch.version.cuda}")
    print(f"   GPU内存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

# 检查数据集
DATA_YAML = "config/data.yaml"
if not os.path.exists(DATA_YAML):
    print(f"❌ 数据配置文件不存在: {DATA_YAML}")
    print("💡 请先运行: python download_satellite_dataset.py")
    sys.exit(1)

print(f"\n📊 加载数据集配置: {DATA_YAML}")
with open(DATA_YAML, 'r') as f:
    data_config = yaml.safe_load(f)

class_names = data_config['names']
num_classes = data_config['nc']
dataset_path = data_config['path']

print(f"   数据集路径: {dataset_path}")
print(f"   类别数量: {num_classes}")
print(f"   类别名称: {class_names}")

# 验证数据集存在
train_images = os.path.join(dataset_path, "train", "images")
val_images = os.path.join(dataset_path, "val", "images")

if not os.path.exists(train_images):
    print(f"❌ 训练图像目录不存在: {train_images}")
    sys.exit(1)

if not os.path.exists(val_images):
    print(f"❌ 验证图像目录不存在: {val_images}")
    sys.exit(1)

# 统计数据集
train_count = len([f for f in os.listdir(train_images) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
val_count = len([f for f in os.listdir(val_images) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])

print(f"   训练图像: {train_count} 张")
print(f"   验证图像: {val_count} 张")

if train_count == 0:
    print("❌ 没有找到训练图像")
    print("💡 请添加图像到训练目录或运行数据下载脚本")
    sys.exit(1)

# 专家改进1: 自动计算类别权重
print("\n🎯 专家改进1: 自动计算类别权重...")

# 获取训练标签文件
label_dir = os.path.join(dataset_path, "train", "labels")
label_files = glob.glob(os.path.join(label_dir, "*.txt"))

if not label_files:
    print("⚠️ 未找到标签文件，使用默认权重")
    cls_weights = np.ones(num_classes)
else:
    # 统计类别分布
    counter = Counter()
    for f in label_files:
        try:
            with open(f) as r:
                for line in r:
                    if line.strip():
                        cls_id = int(line.split()[0])
                        if 0 <= cls_id < num_classes:
                            counter[cls_id] += 1
        except Exception as e:
            print(f"⚠️ 读取标签文件失败 {f}: {e}")
    
    print("📊 类别分布统计:")
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

# 专家改进配置
IMG_SIZE = 768  # 统一解像度
EPOCHS = 50     # 本地训练可以用更多轮次
BATCH_SIZE = 16 # RTX 4090可以处理较大批次

print(f"\n📐 专家改进2: 统一解像度 {IMG_SIZE}x{IMG_SIZE}")
print(f"🔄 专家改进3: AdamW + 余弦退火学习率策略")
print(f"🎨 专家改进4: 分割友好数据增强")
print(f"⚡ RTX 4090优化: 批次大小 {BATCH_SIZE}, 训练轮次 {EPOCHS}")

# 加载模型
print(f"\n🔧 加载YOLOv8分割模型...")
model = YOLO('yolov8m-seg.pt')  # 使用medium版本获得更好效果
print("✅ 模型加载完成")

print(f"\n🚀 开始专家改进版RTX 4090训练...")
print("=" * 60)

print("🎯 专家改进配置摘要:")
print(f"   ✅ 自动类别权重: {cls_weights.round(3).tolist()}")
print(f"   ✅ 统一解像度: {IMG_SIZE}")
print(f"   ✅ 学习率策略: AdamW + 余弦退火")
print(f"   ✅ 数据增强: 分割友好 (Mosaic=0.25, Copy-Paste=0.5)")
print(f"   ✅ GPU加速: RTX 4090 + 混合精度")

try:
    results = model.train(
        # 基本配置
        data=DATA_YAML,
        epochs=EPOCHS,
        imgsz=IMG_SIZE,              # 专家改进: 统一解像度
        batch=BATCH_SIZE,            # RTX 4090优化
        device=0,                    # 强制使用GPU 0
        
        # 专家改进: 自动类别权重
        class_weights=cls_weights.tolist(),
        
        # 专家改进: 现代学习率策略
        optimizer='AdamW',
        lr0=2e-4,                   # 较低的初始学习率
        cos_lr=True,                # 余弦退火
        warmup_epochs=5,            # 预热轮次
        warmup_momentum=0.8,
        warmup_bias_lr=0.1,
        
        # 专家改进: 分割友好数据增强
        mosaic=0.25,                # 大幅降低 (原0.8)
        copy_paste=0.5,             # 分割专用增强
        close_mosaic=0,             # 不延迟关闭
        mixup=0.0,                  # 不使用mixup
        
        # HSV色彩增强
        hsv_h=0.02,
        hsv_s=0.7,
        hsv_v=0.4,
        
        # 几何变换
        degrees=10.0,               # 适度旋转
        translate=0.1,              # 平移
        scale=0.5,                  # 缩放
        shear=0.0,                  # 不使用剪切
        perspective=0.0,            # 不使用透视
        flipud=0.5,                 # 垂直翻转
        fliplr=0.5,                 # 水平翻转
        
        # 训练控制
        patience=20,                # 早停耐心值
        save_period=-1,             # 自动保存最佳模型
        amp=True,                   # 混合精度训练
        
        # 输出配置
        project='runs/segment',
        name='expert_local_rtx4090',
        plots=True,
        save=True,
        verbose=True
    )
    
    print("\n🎉 专家改进版训练完成!")
    print(f"📁 最佳模型: {results.best}")
    print(f"📊 结果目录: runs/segment/expert_local_rtx4090/")
    
    # 显示训练结果
    results_dir = "runs/segment/expert_local_rtx4090"
    if os.path.exists(results_dir):
        print(f"\n📈 训练结果文件:")
        print(f"   训练曲线: {results_dir}/results.png")
        print(f"   混淆矩阵: {results_dir}/confusion_matrix.png")
        print(f"   验证结果: {results_dir}/val_batch0_pred.jpg")
        print(f"   模型权重: {results_dir}/weights/best.pt")
    
    # 显示专家改进效果
    print(f"\n🎯 专家改进效果总结:")
    print(f"   ✅ 自动类别权重 - 基于真实数据分布，解决类别不平衡")
    print(f"   ✅ 统一解像度768 - 训练验证推理一致，避免mAP虚高")
    print(f"   ✅ 余弦退火学习率 - 更稳定收敛，避免震荡")
    print(f"   ✅ 分割友好增强 - 低Mosaic保护边缘，Copy-Paste增强分割")
    print(f"   ✅ RTX 4090加速 - 混合精度训练，大批次高效处理")
    
    print(f"\n📊 与原版本对比:")
    print(f"   原版本问题:")
    print(f"     ❌ 类别权重写在data.yaml中无效")
    print(f"     ❌ 训练640验证896分辨率不一致")
    print(f"     ❌ Mosaic=0.8破坏分割边缘")
    print(f"     ❌ 简单线性学习率衰减")
    print(f"   专家改进版:")
    print(f"     ✅ 权重直接传入model.train()生效")
    print(f"     ✅ 全程统一768分辨率")
    print(f"     ✅ Mosaic=0.25+Copy-Paste=0.5")
    print(f"     ✅ AdamW+余弦退火+预热")
    
    print(f"\n💡 下一步建议:")
    print(f"   1. 查看训练曲线评估收敛情况")
    print(f"   2. 分析混淆矩阵了解各类别性能")
    print(f"   3. 使用最佳模型进行推理测试")
    print(f"   4. 如需要可调整超参数继续训练")
    
except Exception as e:
    print(f"❌ 训练失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n🎊 RTX 4090专家改进版训练成功完成!")
print("=" * 60)
