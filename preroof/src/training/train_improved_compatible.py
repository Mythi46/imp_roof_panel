#!/usr/bin/env python3
"""
改进版训练脚本 - 兼容版本
Improved Training Script - Compatible Version

基于数据集分析结果，使用当前Ultralytics版本支持的参数
"""

import os
import sys
import torch
import yaml
from pathlib import Path
from ultralytics import YOLO

def check_environment():
    """检查训练环境"""
    print("🔍 环境检查...")
    print(f"   Python版本: {sys.version.split()[0]}")
    print(f"   PyTorch版本: {torch.__version__}")
    
    # 检查GPU
    gpu_available = torch.cuda.is_available()
    gpu_count = torch.cuda.device_count()
    print(f"   GPU可用: {gpu_available}")
    print(f"   GPU数量: {gpu_count}")
    
    if gpu_available and gpu_count > 0:
        print(f"   GPU名称: {torch.cuda.get_device_name(0)}")
        device = 0
    else:
        print(f"   使用CPU训练")
        device = 'cpu'
    
    return device

def train_improved_model():
    """使用改进配置训练模型"""
    
    print("🚀 屋顶检测改进版训练 - 兼容版本")
    print("="*60)
    
    # 环境检查
    device = check_environment()
    
    # 数据配置
    DATA_YAML = "data/raw/new-2-1/data.yaml"
    
    if not os.path.exists(DATA_YAML):
        print(f"❌ 数据集配置文件不存在: {DATA_YAML}")
        return None
    
    # 基于数据集分析的配置
    print(f"📊 数据集分析结果:")
    print(f"   类别分布: Baren-Land(12.7%), farm(20.8%), rice-fields(15.9%), roof(50.6%)")
    print(f"   不平衡比例: 4.0:1")
    print(f"   建议权重: [1.96, 1.2, 1.57, 0.49]")
    print(f"   标注质量问题: 2696个")
    
    print(f"\n🎯 改进配置说明:")
    print(f"   模型: yolov8l-seg.pt (升级版，更好特征分辨率)")
    print(f"   图像尺寸: 896 (从768提升)")
    print(f"   损失权重: box=5.0, cls=1.2, dfl=2.5 (优化版)")
    print(f"   数据增强: copy_paste=0.2 (少数类增强)")
    print(f"   学习率策略: 余弦退火 + 降低初始学习率")
    
    # 检查模型文件
    model_path = "models/pretrained/yolov8l-seg.pt"
    if not os.path.exists(model_path):
        print(f"⚠️ 模型文件不存在: {model_path}")
        print(f"   尝试使用yolov8m-seg.pt...")
        model_path = "models/pretrained/yolov8m-seg.pt"
        if not os.path.exists(model_path):
            print(f"❌ 模型文件不存在: {model_path}")
            return None
    
    print(f"\n🔧 加载模型: {model_path}")
    model = YOLO(model_path)
    
    print(f"\n🚀 开始改进版训练...")
    print("="*60)
    
    try:
        results = model.train(
            # 基本配置
            data=DATA_YAML,
            epochs=60,
            imgsz=896,                    # 增大图像尺寸提升精度
            batch=16,
            device=device,
            
            # 优化器配置
            optimizer='AdamW',            # 更好的优化器
            lr0=1e-4,                     # 降低初始学习率
            lrf=0.01,                     # 最终学习率比例
            momentum=0.937,
            weight_decay=0.0005,
            cos_lr=True,                  # 余弦退火学习率
            warmup_epochs=3,              # 减少warmup epochs
            
            # 损失函数权重优化 (核心改进)
            cls=1.2,                      # 分类损失权重 (从1.0提升)
            box=5.0,                      # 边框损失权重 (从7.5降低)
            dfl=2.5,                      # 分布损失权重 (从1.5提升)
            
            # IoU配置
            iou=0.45,                     # 提升正样本阈值
            
            # 数据增强策略 (针对类别不平衡)
            mosaic=0.7,                   # 增强mosaic
            copy_paste=0.2,               # 启用copy-paste (少数类增强)
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
            patience=25,                  # 早停耐心值
            save_period=-1,
            amp=True,                     # 混合精度训练
            workers=0,                    # Windows兼容性
            cache=True,                   # 缓存数据集
            
            # 输出配置
            project='runs/segment',
            name='improved_training_compatible',
            plots=True,
            save=True,
            resume=False,
        )
        
        print(f"\n🎉 改进版训练完成!")
        print("="*60)
        
        # 训练结果分析
        if results:
            print(f"📊 训练结果:")
            
            # 检查保存的模型
            best_model = Path("runs/segment/improved_training_compatible/weights/best.pt")
            if best_model.exists():
                size_mb = best_model.stat().st_size / (1024 * 1024)
                print(f"   最佳模型: {best_model} ({size_mb:.1f}MB)")
            
            last_model = Path("runs/segment/improved_training_compatible/weights/last.pt")
            if last_model.exists():
                size_mb = last_model.stat().st_size / (1024 * 1024)
                print(f"   最终模型: {last_model} ({size_mb:.1f}MB)")
            
            # 检查训练图表
            results_png = Path("runs/segment/improved_training_compatible/results.png")
            if results_png.exists():
                print(f"   训练图表: {results_png}")
            
            # 检查results.csv
            results_csv = Path("runs/segment/improved_training_compatible/results.csv")
            if results_csv.exists():
                print(f"   训练数据: {results_csv}")
        
        print(f"\n💡 下一步建议:")
        print(f"   1. 查看训练图表: runs/segment/improved_training_compatible/results.png")
        print(f"   2. 运行推理测试验证改进效果")
        print(f"   3. 对比改进前后的mAP指标")
        print(f"   4. 分析各类别的PR曲线")
        
        # 保存训练配置记录
        config_record = {
            'model': model_path,
            'data': DATA_YAML,
            'epochs': 60,
            'imgsz': 896,
            'batch': 16,
            'optimizer': 'AdamW',
            'lr0': 1e-4,
            'cls_weight': 1.2,
            'box_weight': 5.0,
            'dfl_weight': 2.5,
            'copy_paste': 0.2,
            'mosaic': 0.7,
            'improvements': [
                'Upgraded to yolov8l-seg.pt',
                'Increased image size to 896',
                'Optimized loss weights based on analysis',
                'Enhanced data augmentation for class balance',
                'Cosine annealing learning rate',
                'Copy-paste augmentation for minority classes'
            ],
            'expected_improvements': {
                'mAP50': '+8-15%',
                'mAP50_95': '+10-18%',
                'minority_class_recall': '+20-30%'
            }
        }
        
        import json
        with open('runs/segment/improved_training_compatible/training_config.json', 'w') as f:
            json.dump(config_record, f, indent=2)
        
        print(f"   5. 训练配置已保存: runs/segment/improved_training_compatible/training_config.json")
        
        return results
        
    except Exception as e:
        print(f"❌ 训练失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """主函数"""
    try:
        results = train_improved_model()
        if results:
            print(f"\n✅ 改进版训练成功完成!")
            print(f"📁 训练结果保存在: runs/segment/improved_training_compatible/")
        else:
            print(f"\n❌ 改进版训练失败!")
    except KeyboardInterrupt:
        print(f"\n⏹️ 训练被用户中断")
    except Exception as e:
        print(f"\n💥 发生未预期错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
