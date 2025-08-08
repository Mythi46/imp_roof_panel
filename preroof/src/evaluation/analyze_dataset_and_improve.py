#!/usr/bin/env python3
"""
数据集分析和改进训练脚本
Dataset Analysis and Improved Training Script

基于训练结果分析，实施系统性改进方案
"""

import os
import sys
import yaml
import glob
from collections import Counter, defaultdict
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from ultralytics import YOLO

def analyze_class_distribution(yaml_path):
    """分析类别分布并计算建议权重"""
    print("🔍 分析类别分布...")
    
    with open(yaml_path) as f: 
        cfg = yaml.safe_load(f)
    
    label_dir = os.path.join(os.path.dirname(yaml_path), "train/labels")
    counter = Counter()
    total_images = 0
    
    # 统计每个类别的实例数
    for f in glob.glob(f"{label_dir}/*.txt"):
        total_images += 1
        with open(f) as fp:
            for line in fp:
                if line.strip():
                    cls = int(line.split()[0])
                    counter[cls] += 1
    
    print(f"📊 数据集统计:")
    print(f"   总图像数: {total_images}")
    print(f"   总实例数: {sum(counter.values())}")
    print(f"   类别分布: {dict(counter)}")
    print(f"   类别名称: {cfg['names']}")
    
    # 计算类别权重 (逆频率权重)
    total_instances = sum(counter.values())
    num_classes = len(cfg['names'])
    weights = []
    
    print(f"\n📈 类别详细分析:")
    for i in range(num_classes):
        class_name = cfg['names'][i]
        count = counter.get(i, 0)
        
        if count > 0:
            # 逆频率权重计算
            weight = total_instances / (num_classes * count)
            percentage = (count / total_instances) * 100
            print(f"   {class_name}: {count} 实例 ({percentage:.1f}%) -> 权重: {weight:.2f}")
        else:
            weight = 1.0
            print(f"   {class_name}: 0 实例 (0.0%) -> 权重: {weight:.2f}")
        
        weights.append(round(weight, 2))
    
    print(f"\n🎯 建议的class_weights: {weights}")
    
    # 可视化类别分布
    plt.figure(figsize=(10, 6))
    classes = [cfg['names'][i] for i in range(num_classes)]
    counts = [counter.get(i, 0) for i in range(num_classes)]
    
    plt.bar(classes, counts)
    plt.title('类别分布 (Class Distribution)')
    plt.xlabel('类别 (Classes)')
    plt.ylabel('实例数 (Instance Count)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # 保存图表
    plt.savefig('results/class_distribution.png', dpi=300, bbox_inches='tight')
    print(f"📊 类别分布图已保存: results/class_distribution.png")
    
    return weights, counter, cfg

def check_annotation_quality(yaml_path, sample_ratio=0.05):
    """检查标注质量"""
    print(f"\n🔍 检查标注质量 (抽样比例: {sample_ratio*100:.1f}%)...")
    
    with open(yaml_path) as f: 
        cfg = yaml.safe_load(f)
    
    label_dir = os.path.join(os.path.dirname(yaml_path), "train/labels")
    label_files = glob.glob(f"{label_dir}/*.txt")
    
    # 抽样检查
    sample_size = max(1, int(len(label_files) * sample_ratio))
    sample_files = np.random.choice(label_files, sample_size, replace=False)
    
    issues = []
    
    for label_file in sample_files:
        with open(label_file) as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            if line.strip():
                parts = line.strip().split()
                if len(parts) < 5:
                    issues.append(f"{label_file}:{i+1} - 格式错误: {line.strip()}")
                    continue
                
                try:
                    cls, x, y, w, h = map(float, parts[:5])
                    
                    # 检查坐标范围
                    if not (0 <= x <= 1 and 0 <= y <= 1 and 0 <= w <= 1 and 0 <= h <= 1):
                        issues.append(f"{label_file}:{i+1} - 坐标超出范围: {line.strip()}")
                    
                    # 检查异常尺寸
                    if w < 0.001 or h < 0.001:
                        issues.append(f"{label_file}:{i+1} - 目标过小: w={w:.4f}, h={h:.4f}")
                    elif w > 0.8 or h > 0.8:
                        issues.append(f"{label_file}:{i+1} - 目标过大: w={w:.4f}, h={h:.4f}")
                        
                except ValueError:
                    issues.append(f"{label_file}:{i+1} - 数值解析错误: {line.strip()}")
    
    print(f"📋 标注质量检查结果:")
    print(f"   检查文件数: {sample_size}")
    print(f"   发现问题数: {len(issues)}")
    
    if issues:
        print(f"   前10个问题:")
        for issue in issues[:10]:
            print(f"     {issue}")
        
        # 保存完整问题列表
        with open('results/annotation_issues.txt', 'w', encoding='utf-8') as f:
            f.write("标注质量问题报告\n")
            f.write("="*50 + "\n\n")
            for issue in issues:
                f.write(f"{issue}\n")
        
        print(f"   完整问题列表已保存: results/annotation_issues.txt")
    else:
        print(f"   ✅ 未发现明显问题")
    
    return issues

def create_improved_training_script():
    """创建改进的训练脚本"""
    print(f"\n🚀 创建改进的训练脚本...")
    
    script_content = '''#!/usr/bin/env python3
"""
改进版训练脚本 - 基于结果分析优化
Improved Training Script - Optimized Based on Results Analysis
"""

from ultralytics import YOLO
import torch

def train_improved_model():
    """使用改进配置训练模型"""
    
    print("🚀 开始改进版训练...")
    
    # 检查GPU
    device = 0 if torch.cuda.is_available() else 'cpu'
    print(f"使用设备: {device}")
    
    # 数据配置
    DATA_YAML = "data/raw/new-2-1/data.yaml"
    
    # 基于分析结果的类别权重 (需要根据实际分析结果调整)
    class_weights = [1.4, 1.2, 1.3, 0.6]  # 示例权重，请根据分析结果调整
    
    # 使用更大的模型以提升特征分辨率
    model = YOLO("models/pretrained/yolov8l-seg.pt")  # 从m升级到l
    
    # 训练配置
    results = model.train(
        # 基本配置
        data=DATA_YAML,
        epochs=60,
        imgsz=896,                    # 增大图像尺寸 (从768到896)
        batch=16,
        device=device,
        
        # 优化器配置
        optimizer='AdamW',
        lr0=1e-4,                     # 降低初始学习率
        lrf=0.01,
        momentum=0.937,
        weight_decay=0.0005,
        cos_lr=True,                  # 余弦退火学习率
        warmup_epochs=3,              # 减少warmup epochs
        
        # 类别平衡策略
        class_weights=class_weights,   # 显式传递类别权重
        sampler='weighted',           # 启用加权采样
        
        # 损失函数权重优化
        cls=1.2,                      # 分类损失权重
        box=5.0,                      # 边框损失权重 (从7.5降低)
        dfl=2.5,                      # 分布损失权重 (从1.5提升)
        
        # IoU配置优化
        iou_type='giou',              # 使用GIoU (更适合长条形目标)
        iou=0.45,                     # 提升正样本阈值
        
        # 数据增强策略
        mosaic=0.7,                   # 增强mosaic
        copy_paste=0.2,               # 启用copy-paste增强
        close_mosaic=10,              # 最后10个epoch关闭mosaic
        degrees=12,                   # 旋转增强
        translate=0.1,                # 平移增强
        scale=0.5,                    # 缩放增强
        shear=2.0,                    # 剪切增强
        flipud=0.3,                   # 垂直翻转
        fliplr=0.5,                   # 水平翻转
        hsv_h=0.02,                   # 色调增强
        hsv_s=0.6,                    # 饱和度增强
        hsv_v=0.4,                    # 亮度增强
        
        # 训练稳定性
        ema_decay=0.995,              # EMA衰减
        patience=25,
        save_period=-1,
        amp=True,
        workers=0,                    # Windows兼容
        cache=True,
        
        # 输出配置
        project='runs/segment',
        name='improved_training_v2',
        plots=True,
        save=True,
        resume=False
    )
    
    print("🎉 训练完成!")
    return results

if __name__ == "__main__":
    results = train_improved_model()
'''
    
    with open('train_improved_v2.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ 改进训练脚本已创建: train_improved_v2.py")

def main():
    """主函数"""
    print("🏠 屋顶检测项目 - 数据集分析和改进方案")
    print("="*60)
    
    # 确保结果目录存在
    Path("results").mkdir(exist_ok=True)
    
    # 数据集路径
    yaml_path = "data/raw/new-2-1/data.yaml"
    
    if not os.path.exists(yaml_path):
        print(f"❌ 数据集配置文件不存在: {yaml_path}")
        return
    
    # 1. 分析类别分布
    weights, counter, cfg = analyze_class_distribution(yaml_path)
    
    # 2. 检查标注质量
    issues = check_annotation_quality(yaml_path)
    
    # 3. 创建改进的训练脚本
    create_improved_training_script()
    
    # 4. 生成改进建议报告
    print(f"\n📋 改进建议总结:")
    print(f"="*40)
    
    # 类别不平衡分析
    total_instances = sum(counter.values())
    imbalance_ratio = max(counter.values()) / min(counter.values()) if counter.values() else 1
    
    print(f"🎯 类别不平衡分析:")
    print(f"   不平衡比例: {imbalance_ratio:.1f}:1")
    if imbalance_ratio > 10:
        print(f"   ⚠️ 严重不平衡，强烈建议使用class_weights和数据增强")
    elif imbalance_ratio > 3:
        print(f"   ⚠️ 中度不平衡，建议使用class_weights")
    else:
        print(f"   ✅ 相对平衡")
    
    print(f"\n🔧 建议的改进措施:")
    print(f"   1. 使用计算出的class_weights: {weights}")
    print(f"   2. 启用copy_paste数据增强")
    print(f"   3. 升级到yolov8l-seg.pt模型")
    print(f"   4. 调整损失权重: box=5.0, cls=1.2, dfl=2.5")
    print(f"   5. 使用GIoU损失: iou_type='giou'")
    
    if issues:
        print(f"   6. ⚠️ 修复{len(issues)}个标注质量问题")
    
    print(f"\n🚀 下一步:")
    print(f"   1. 运行: python train_improved_v2.py")
    print(f"   2. 监控训练进度和指标")
    print(f"   3. 对比改进前后的结果")
    
    print(f"\n✅ 分析完成! 详细结果保存在 results/ 目录")

if __name__ == "__main__":
    main()
