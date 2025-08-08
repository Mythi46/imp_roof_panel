#!/usr/bin/env python3
"""
项目清理和整理脚本
Project cleanup and organization script
"""

import os
import shutil
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def cleanup_project():
    """清理和整理项目"""
    
    print("🧹 开始清理项目...")
    
    # 1. 清理重复的数据集
    print("\n📁 清理重复数据集...")
    if Path("new-2-1").exists() and Path("data/raw/new-2-1").exists():
        print("   删除根目录下的重复数据集 new-2-1/")
        shutil.rmtree("new-2-1")
        print("   ✅ 已删除重复数据集")
    
    # 2. 清理多余的训练脚本
    print("\n🗂️ 清理多余的训练脚本...")
    training_scripts_to_remove = [
        "train_expert_demo.py",
        "train_expert_fixed_weights.py", 
        "train_expert_simple.py",
        "train_expert_with_local_data.py",
        "validate_class_weights_fix.py",
        "test_gpu_training.py"
    ]
    
    # 创建archive目录保存旧脚本
    archive_dir = Path("archive/old_scripts")
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    for script in training_scripts_to_remove:
        if Path(script).exists():
            shutil.move(script, archive_dir / script)
            print(f"   移动 {script} 到 archive/old_scripts/")
    
    # 3. 清理失败的训练结果
    print("\n🗑️ 清理失败的训练结果...")
    runs_dir = Path("runs/segment")
    if runs_dir.exists():
        for run_dir in runs_dir.iterdir():
            if run_dir.is_dir():
                weights_dir = run_dir / "weights"
                # 如果weights目录为空或不存在，说明训练失败
                if not weights_dir.exists() or not any(weights_dir.iterdir()):
                    print(f"   删除失败的训练结果: {run_dir.name}")
                    shutil.rmtree(run_dir)
    
    # 4. 整理配置文件
    print("\n⚙️ 整理配置文件...")
    
    # 5. 清理多余的下载脚本
    print("\n📥 整理下载脚本...")
    download_scripts = [
        "download_dataset_local.py",
        "download_roboflow_dataset.py", 
        "download_satellite_dataset.py"
    ]
    
    scripts_dir = Path("scripts")
    for script in download_scripts:
        if Path(script).exists():
            shutil.move(script, scripts_dir / script)
            print(f"   移动 {script} 到 scripts/")
    
    # 6. 清理多余的setup文件
    print("\n🔧 整理setup文件...")
    setup_files_to_archive = [
        "setup.bat",
        "setup.sh", 
        "setup_conda_environment.bat",
        "setup_conda_environment.sh",
        "setup_local_environment.py",
        "run_training_with_conda.bat"
    ]
    
    setup_archive = Path("archive/setup_files")
    setup_archive.mkdir(parents=True, exist_ok=True)
    
    for setup_file in setup_files_to_archive:
        if Path(setup_file).exists():
            shutil.move(setup_file, setup_archive / setup_file)
            print(f"   移动 {setup_file} 到 archive/setup_files/")
    
    print("\n✅ 项目清理完成!")

def create_clean_structure():
    """创建清晰的项目结构"""
    
    print("\n📋 创建标准项目结构...")
    
    # 标准目录结构
    directories = [
        "data/raw",
        "data/processed", 
        "models/trained",
        "models/pretrained",
        "results/training",
        "results/evaluation",
        "results/visualization",
        "scripts",
        "config",
        "notebooks",
        "archive"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ 确保目录存在: {directory}")
    
    # 移动预训练模型到正确位置
    pretrained_models = ["yolo11n.pt", "yolov8m-seg.pt"]
    for model in pretrained_models:
        if Path(model).exists():
            shutil.move(model, f"models/pretrained/{model}")
            print(f"   移动预训练模型: {model} -> models/pretrained/")

def create_main_readme():
    """创建主要的README文件"""
    
    readme_content = """# 🏠 屋顶检测项目 (Roof Detection Project)

## 📋 项目概述

这是一个基于YOLOv8的屋顶分割检测项目，专门用于识别和分割航拍图像中的不同类型屋顶。

### 🎯 检测类别
- `Baren-Land`: 裸地
- `farm`: 农田  
- `rice-fields`: 稻田
- `roof`: 屋顶

## 📁 项目结构

```
roof-detection/
├── data/                    # 数据目录
│   ├── raw/                # 原始数据
│   └── processed/          # 处理后的数据
├── models/                 # 模型目录
│   ├── pretrained/        # 预训练模型
│   └── trained/           # 训练好的模型
├── results/               # 结果目录
│   ├── training/         # 训练结果
│   ├── evaluation/       # 评估结果
│   └── visualization/    # 可视化结果
├── scripts/              # 脚本目录
├── config/               # 配置文件
├── notebooks/            # Jupyter笔记本
└── archive/              # 归档文件
```

## 🚀 快速开始

### 1. 环境设置
```bash
pip install -r requirements.txt
```

### 2. 数据准备
数据集已包含在 `data/raw/new-2-1/` 目录中。

### 3. 开始训练
```bash
python train_expert_correct_solution.py
```

### 4. 可视化结果
```bash
python generate_visualization_results.py
```

## 📊 训练配置

当前使用的专家改进配置：
- **模型**: YOLOv8m-seg (分割模型)
- **图像尺寸**: 768x768
- **批次大小**: 16
- **学习率**: 0.005 (AdamW优化器)
- **损失权重**: cls=1.0, box=7.5, dfl=1.5
- **数据增强**: copy_paste=0.5, mosaic=0.3, mixup=0.1

## 🔧 重要说明

### YOLOv8类别权重问题
⚠️ **重要发现**: YOLOv8不支持`class_weights`参数！

**解决方案**:
1. 调整损失函数权重 (cls, box, dfl)
2. 使用数据增强策略平衡类别
3. 优化训练策略 (学习率、epochs等)

## 📈 性能优化

- 使用余弦退火学习率调度
- 增加分类损失权重以改善类别不平衡
- 针对性数据增强策略
- 早停机制防止过拟合

## 📝 更新日志

- **2024-07-29**: 项目重构和清理
- **2024-07-29**: 修复YOLOv8类别权重问题
- **2024-07-29**: 优化训练配置和数据增强策略

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

MIT License
"""
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("   ✅ 创建了新的主README文件")

if __name__ == "__main__":
    cleanup_project()
    create_clean_structure() 
    create_main_readme()
    print("\n🎉 项目整理完成！")
    print("\n📋 当前项目结构已优化，主要文件:")
    print("   - train_expert_correct_solution.py (主训练脚本)")
    print("   - generate_visualization_results.py (可视化脚本)")
    print("   - data/raw/new-2-1/ (数据集)")
    print("   - models/pretrained/ (预训练模型)")
    print("   - archive/ (归档的旧文件)")
