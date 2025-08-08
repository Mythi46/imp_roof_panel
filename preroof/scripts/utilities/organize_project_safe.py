#!/usr/bin/env python3
"""
安全的项目文件整理脚本
Safe Project File Organization Script

只复制文件到新位置，不删除原文件，确保数据安全
"""

import os
import shutil
from pathlib import Path
import json

def create_organized_structure():
    """创建标准化的项目结构"""
    
    print("🗂️ 创建标准化项目结构...")
    
    # 定义新的目录结构
    directories = [
        # 核心目录
        "docs",                          # 文档
        "docs/technical_reports",        # 技术报告
        "docs/visualization",            # 可视化结果
        "docs/legacy",                   # 历史文档
        
        # 源代码
        "src",                           # 源代码
        "src/training",                  # 训练脚本
        "src/evaluation",                # 评估脚本
        "src/visualization",             # 可视化脚本
        "src/utils",                     # 工具函数
        
        # 配置和脚本
        "scripts",                       # 脚本
        "scripts/setup",                 # 设置脚本
        "scripts/training",              # 训练脚本
        "scripts/evaluation",            # 评估脚本
        
        # 结果和输出
        "outputs",                       # 输出
        "outputs/training",              # 训练输出
        "outputs/evaluation",            # 评估输出
        "outputs/visualization",         # 可视化输出
        
        # 配置
        "configs",                       # 配置文件
        
        # 笔记本
        "notebooks",                     # Jupyter笔记本
        "notebooks/experiments",         # 实验笔记本
        "notebooks/analysis",            # 分析笔记本
    ]
    
    # 创建目录
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ 创建目录: {directory}")

def copy_files_safely():
    """安全地复制文件到新结构中（不删除原文件）"""
    
    print("\n📁 安全复制文件...")
    
    # 文件复制映射（只复制，不删除原文件）
    file_copies = {
        # 技术报告 - 复制到docs/technical_reports
        "technical_report/BILINGUAL_TECHNICAL_REPORT.md": "docs/technical_reports/",
        "technical_report/BILINGUAL_PERFORMANCE_ANALYSIS.md": "docs/technical_reports/",
        "technical_report/BILINGUAL_DEPLOYMENT_GUIDE.md": "docs/technical_reports/",
        "technical_report/COMPREHENSIVE_TECHNICAL_REPORT.md": "docs/technical_reports/",
        "technical_report/README.md": "docs/technical_reports/",
        "technical_report/deployment_guide.md": "docs/technical_reports/",
        "technical_report/detailed_timeline_analysis.md": "docs/technical_reports/",
        "technical_report/performance_metrics_analysis.md": "docs/technical_reports/",
        "technical_report/training_configuration_details.md": "docs/technical_reports/",
        
        # 可视化结果 - 复制到docs/visualization
        "visualization_results/index.html": "docs/visualization/",
        "visualization_results/results_gallery.html": "docs/visualization/",
        "visualization_results/results_gallery_en.html": "docs/visualization/",
        "visualization_results/results_gallery_ja.html": "docs/visualization/",
        "visualization_results/README.md": "docs/visualization/",
        "visualization_results/detection_results.json": "docs/visualization/",
        "visualization_results/detection_summary.png": "docs/visualization/",
        
        # 训练脚本 - 复制到src/training
        "train_improved_compatible.py": "src/training/",
        "train_improved_v2.py": "src/training/",
        "train_expert_correct_solution.py": "src/training/",
        "continue_training_optimized.py": "src/training/",
        "start_training.py": "src/training/",
        "train_expert_demo.py": "src/training/",
        "train_expert_fixed_weights.py": "src/training/",
        "train_expert_simple.py": "src/training/",
        "train_expert_with_local_data.py": "src/training/",
        
        # 评估脚本 - 复制到src/evaluation
        "analyze_dataset_and_improve.py": "src/evaluation/",
        "evaluate_improvements.py": "src/evaluation/",
        "analyze_detection_results.py": "src/evaluation/",
        "validate_class_weights_fix.py": "src/evaluation/",
        "test_gpu_training.py": "src/evaluation/",
        
        # 可视化脚本 - 复制到src/visualization
        "generate_visualization_results.py": "src/visualization/",
        "generate_english_visualization.py": "src/visualization/",
        "visualize_results_demo.py": "src/visualization/",
        
        # 监控脚本 - 复制到src/utils
        "monitor_training.py": "src/utils/",
        "monitor_continue_training.py": "src/utils/",
        
        # 测试脚本 - 复制到scripts/evaluation
        "quick_test_expert_improvements.py": "scripts/evaluation/",
        
        # 配置文件 - 复制到configs
        "config/data_config.yaml": "configs/",
        "config/model_config.yaml": "configs/",
        
        # 设置脚本 - 复制到scripts/setup
        "setup.py": "scripts/setup/",
        "cleanup_project.py": "scripts/setup/",
        
        # 笔记本 - 复制到notebooks/experiments
        "roof_detection_expert_improved.ipynb": "notebooks/experiments/",
        "satellite_detection_expert_final.ipynb": "notebooks/experiments/",
        "notebooks/01_专家改进版本地训练.ipynb": "notebooks/experiments/",
    }
    
    # 执行文件复制
    for source, destination in file_copies.items():
        source_path = Path(source)
        dest_path = Path(destination)
        
        if source_path.exists():
            try:
                # 确保目标目录存在
                dest_path.mkdir(parents=True, exist_ok=True)
                
                # 复制文件
                dest_file = dest_path / source_path.name
                shutil.copy2(str(source_path), str(dest_file))
                
                print(f"   ✅ 复制: {source} → {destination}")
                
            except Exception as e:
                print(f"   ❌ 复制失败: {source} → {destination} ({e})")

def copy_visualization_images():
    """复制可视化图片文件"""
    
    print("\n🖼️ 复制可视化图片...")
    
    viz_source = Path("visualization_results")
    viz_dest = Path("docs/visualization")
    
    if viz_source.exists():
        # 复制所有图片文件
        for img_file in viz_source.glob("*.jpg"):
            try:
                shutil.copy2(str(img_file), str(viz_dest / img_file.name))
                print(f"   ✅ 复制图片: {img_file.name}")
            except Exception as e:
                print(f"   ❌ 复制图片失败: {img_file.name} ({e})")
        
        for img_file in viz_source.glob("*.png"):
            try:
                shutil.copy2(str(img_file), str(viz_dest / img_file.name))
                print(f"   ✅ 复制图片: {img_file.name}")
            except Exception as e:
                print(f"   ❌ 复制图片失败: {img_file.name} ({e})")

def create_organized_readme():
    """创建整理后的README文件"""
    
    print("\n📝 创建整理后的README文件...")
    
    readme_content = """# 🏠 Roof Detection Project | 屋顶检测项目

## 📋 Project Overview | 项目概述

This project implements a high-performance roof detection system using YOLOv8l-seg, achieving **90.77% mAP@0.5** performance through systematic optimization and innovative training strategies.

本项目实现了基于YOLOv8l-seg的高性能屋顶检测系统，通过系统性优化和创新训练策略达到了**90.77% mAP@0.5**的性能。

## 🎯 Key Achievements | 主要成果

- **Performance**: 90.77% mAP@0.5, 80.85% mAP@0.5:0.95
- **Improvement**: +42.7% mAP@0.5 from baseline
- **Innovation**: Solved YOLOv8 class_weights limitation
- **Production Ready**: Immediately deployable model

## 📁 Organized Project Structure | 整理后的项目结构

### 📚 Documentation | 文档
- **docs/technical_reports/**: Complete technical documentation
- **docs/visualization/**: Interactive visualization galleries
- **docs/legacy/**: Historical documents

### 💻 Source Code | 源代码
- **src/training/**: Training scripts and implementations
- **src/evaluation/**: Model evaluation and analysis tools
- **src/visualization/**: Result visualization tools
- **src/utils/**: Utility functions and monitoring

### 🔧 Scripts | 脚本
- **scripts/setup/**: Project setup scripts
- **scripts/evaluation/**: Quick testing scripts
- **scripts/training/**: Training pipeline scripts

## 🚀 Quick Start | 快速开始

### Original Files | 原始文件
All original files are preserved in their original locations for compatibility.

### Organized Files | 整理后的文件
New organized structure is available in the respective directories:

```bash
# Training | 训练
python src/training/train_improved_compatible.py

# Evaluation | 评估
python src/evaluation/evaluate_improvements.py

# Visualization | 可视化
python src/visualization/visualize_results_demo.py
```

### Documentation | 文档
- **Technical Reports**: `docs/technical_reports/`
- **Visualization Gallery**: `docs/visualization/index.html`
- **Performance Analysis**: `docs/technical_reports/BILINGUAL_PERFORMANCE_ANALYSIS.md`

## 📊 Performance Highlights | 性能亮点

- **mAP@0.5**: 63.62% → 90.77% (+42.7%)
- **mAP@0.5:0.95**: 49.86% → 80.85% (+62.1%)
- **Class Balance**: Improved minority class performance by 25-30%
- **Production Ready**: Immediately deployable

## 🔬 Technical Innovations | 技术创新

1. **YOLOv8 Class Weights Solution** - Solved parameter limitation
2. **Data-Driven Weight Calculation** - Inverse frequency algorithm
3. **Two-Stage Training Strategy** - Aggressive + fine-tuning
4. **Advanced Data Augmentation** - Copy-paste + mosaic

## 📄 File Organization | 文件组织

This project maintains both:
- **Original structure** for backward compatibility
- **Organized structure** for better navigation and development

Both structures coexist to ensure no functionality is lost while providing improved organization.

---

**Status**: ✅ Production Ready | 生产就绪  
**Performance**: 🏆 90.77% mAP@0.5  
**Organization**: 📁 Dual Structure (Original + Organized)  
"""
    
    with open("README_ORGANIZED.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("   ✅ 创建README_ORGANIZED.md")

def create_organization_summary():
    """创建整理总结文件"""
    
    print("\n📋 创建整理总结...")
    
    summary = {
        "organization_type": "Safe Copy (No Deletion)",
        "original_files": "Preserved in original locations",
        "organized_files": "Copied to new structure",
        "structure": {
            "docs/": "All documentation and reports",
            "src/": "Source code organized by function",
            "scripts/": "Utility and setup scripts",
            "outputs/": "Training and evaluation outputs",
            "configs/": "Configuration files",
            "notebooks/": "Jupyter notebooks"
        },
        "benefits": [
            "Improved navigation",
            "Better organization",
            "Maintained compatibility",
            "No data loss"
        ],
        "status": "Complete - Dual Structure Available"
    }
    
    with open("organization_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print("   ✅ 创建organization_summary.json")

def main():
    """主函数"""
    
    print("🗂️ 开始安全项目文件整理...")
    print("=" * 50)
    print("⚠️  注意：此脚本只复制文件，不删除原文件")
    print("=" * 50)
    
    # 1. 创建标准化目录结构
    create_organized_structure()
    
    # 2. 安全复制文件
    copy_files_safely()
    
    # 3. 复制可视化图片
    copy_visualization_images()
    
    # 4. 创建整理后的README
    create_organized_readme()
    
    # 5. 创建整理总结
    create_organization_summary()
    
    print("\n" + "=" * 50)
    print("✅ 安全项目文件整理完成!")
    print("\n📁 项目现在有两套结构:")
    print("   📂 原始结构 - 保持不变，确保兼容性")
    print("   📂 整理结构 - 新的组织方式，便于开发")
    
    print("\n🎯 整理后的结构:")
    print("   📚 docs/ - 所有文档和报告")
    print("   💻 src/ - 按功能组织的源代码")
    print("   🔧 scripts/ - 工具和设置脚本")
    print("   📊 outputs/ - 训练和评估输出")
    print("   ⚙️ configs/ - 配置文件")
    print("   📓 notebooks/ - Jupyter笔记本")
    
    print("\n✅ 优势:")
    print("   - 原文件完全保留")
    print("   - 新结构便于导航")
    print("   - 双重兼容性")
    print("   - 零数据丢失")

if __name__ == "__main__":
    main()
