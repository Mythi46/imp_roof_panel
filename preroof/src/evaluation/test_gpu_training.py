#!/usr/bin/env python3
"""
GPU训练测试脚本
"""

import torch
from ultralytics import YOLO

print("🔍 GPU环境测试")
print("=" * 30)

# 检查GPU
print(f"GPU可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU名称: {torch.cuda.get_device_name(0)}")
    print(f"GPU内存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    print(f"CUDA版本: {torch.version.cuda}")

# 测试YOLO模型加载
print("\n🔧 测试YOLO模型...")
try:
    model = YOLO('yolov8n.pt')  # 下载最小的模型
    print("✅ YOLO模型加载成功")
    
    # 测试GPU训练
    print("\n🚀 测试GPU训练...")
    results = model.train(
        data='coco8.yaml',  # 使用内置的小数据集
        epochs=1,           # 只训练1轮测试
        imgsz=640,
        batch=4,
        device=0,           # 强制使用GPU 0
        project='test_runs',
        name='gpu_test',
        verbose=True
    )
    
    print("🎉 GPU训练测试成功!")
    print(f"最佳模型: {results.best}")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ GPU环境测试完成")
