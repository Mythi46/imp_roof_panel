#!/usr/bin/env python3
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
    
    # 基于数据集分析的精确权重
    # 类别分布: Baren-Land(12.7%), farm(20.8%), rice-fields(15.9%), roof(50.6%)
    # 不平衡比例: 4.0:1 (中度不平衡)
    class_weights = [1.96, 1.2, 1.57, 0.49]  # 基于实际分析结果
    
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
        
        # 类别平衡策略 (注释掉不支持的参数)
        # class_weights=class_weights,   # 当前版本不支持
        # sampler='weighted',           # 当前版本不支持
        
        # 损失函数权重优化
        cls=1.2,                      # 分类损失权重
        box=5.0,                      # 边框损失权重 (从7.5降低)
        dfl=2.5,                      # 分布损失权重 (从1.5提升)
        
        # IoU配置优化
        # iou_type='giou',              # 当前版本不支持
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
        # ema_decay=0.995,              # 当前版本不支持
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
