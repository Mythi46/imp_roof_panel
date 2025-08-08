#!/usr/bin/env python3
"""
整理剩余根目录文件脚本
Organize Remaining Root Directory Files Script

继续整理根目录中的剩余文件，只复制不删除
"""

import os
import shutil
from pathlib import Path
import json

def create_additional_directories():
    """创建额外需要的目录"""
    
    print("🗂️ 创建额外目录结构...")
    
    # 额外目录
    additional_dirs = [
        # 归档目录
        "archive/legacy_docs",           # 历史文档
        "archive/legacy_scripts",        # 历史脚本
        "archive/japanese_content",      # 日文内容
        "archive/original_content",      # 原始内容
        "archive/versions",              # 版本历史
        
        # 结果目录
        "outputs/legacy_results",        # 历史结果
        "outputs/training_runs",         # 训练运行
        
        # 脚本目录
        "scripts/legacy",                # 历史脚本
        "scripts/utilities",             # 工具脚本
        
        # 文档目录
        "docs/project_management",       # 项目管理文档
        "docs/setup_guides",             # 设置指南
    ]
    
    for directory in additional_dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ 创建目录: {directory}")

def organize_remaining_files():
    """整理剩余的根目录文件"""
    
    print("\n📁 整理剩余根目录文件...")
    
    # 剩余文件的复制映射
    remaining_file_copies = {
        # 历史文档 - 移动到docs/legacy（已经存在一些，补充剩余的）
        "CONTINUE_TRAINING_ANALYSIS.md": "docs/legacy/",
        "CONTINUE_TRAINING_FINAL_RESULTS.md": "docs/legacy/",
        "DATASET_ANALYSIS_SUMMARY.md": "docs/legacy/",
        "EXECUTIVE_SUMMARY.md": "docs/legacy/",
        "GITHUB_PUSH_SUCCESS.md": "docs/legacy/",
        "LOCAL_EXPERT_SETUP.md": "docs/legacy/",
        "PROJECT_IMPROVEMENT_REPORT.md": "docs/legacy/",
        "PROJECT_STATUS.md": "docs/legacy/",
        "PROJECT_SUMMARY.md": "docs/legacy/",
        "TRAINING_RESULTS_7_EPOCHS.md": "docs/legacy/",
        "TRAINING_RESULTS_ANALYSIS_AND_IMPROVEMENTS.md": "docs/legacy/",
        
        # 项目管理文档
        "QUICKSTART.md": "docs/project_management/",
        "PROJECT_NAVIGATION.md": "docs/project_management/",
        "README_ORGANIZED.md": "docs/project_management/",
        "organization_summary.json": "docs/project_management/",
        "project_info.json": "docs/project_management/",
        
        # 环境和依赖文件
        "environment.yml": "configs/",
        "requirements.txt": "configs/",
        
        # 设置和清理脚本
        "organize_project.py": "scripts/utilities/",
        "organize_project_safe.py": "scripts/utilities/",
        "cleanup_project.py": "scripts/utilities/",
        
        # 剩余的训练脚本（根目录中的）
        "train_expert_demo.py": "archive/legacy_scripts/",
        "train_expert_fixed_weights.py": "archive/legacy_scripts/",
        "train_expert_simple.py": "archive/legacy_scripts/",
        "train_expert_with_local_data.py": "archive/legacy_scripts/",
        
        # 剩余的评估脚本
        "test_gpu_training.py": "archive/legacy_scripts/",
        "validate_class_weights_fix.py": "archive/legacy_scripts/",
        
        # 剩余的可视化脚本
        "visualize_results_demo.py": "archive/legacy_scripts/",
        
        # 剩余的监控脚本
        "monitor_training.py": "archive/legacy_scripts/",
        "monitor_continue_training.py": "archive/legacy_scripts/",
        
        # 剩余的分析脚本
        "analyze_dataset_and_improve.py": "archive/legacy_scripts/",
        "analyze_detection_results.py": "archive/legacy_scripts/",
        "evaluate_improvements.py": "archive/legacy_scripts/",
        "generate_english_visualization.py": "archive/legacy_scripts/",
        "generate_visualization_results.py": "archive/legacy_scripts/",
        
        # 剩余的训练脚本
        "continue_training_optimized.py": "archive/legacy_scripts/",
        "start_training.py": "archive/legacy_scripts/",
        "train_improved_compatible.py": "archive/legacy_scripts/",
        "train_improved_v2.py": "archive/legacy_scripts/",
        "train_expert_correct_solution.py": "archive/legacy_scripts/",
        
        # 其他脚本
        "quick_test_expert_improvements.py": "archive/legacy_scripts/",
        "setup.py": "archive/legacy_scripts/",
        
        # 笔记本文件
        "roof_detection_expert_improved.ipynb": "archive/legacy_scripts/",
        "satellite_detection_expert_final.ipynb": "archive/legacy_scripts/",
    }
    
    # 执行文件复制
    for source, destination in remaining_file_copies.items():
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

def organize_directories():
    """整理剩余的目录"""
    
    print("\n📂 整理剩余目录...")
    
    # 目录复制映射
    directory_copies = {
        # 日文版本内容
        "japanese_version/": "archive/japanese_content/",
        
        # 原始文件
        "original_files/": "archive/original_content/",
        
        # 版本历史
        "versions/": "archive/versions/",
        
        # 结果目录
        "results/": "outputs/legacy_results/",
    }
    
    # 执行目录复制
    for source, destination in directory_copies.items():
        source_path = Path(source)
        dest_path = Path(destination)
        
        if source_path.exists() and source_path.is_dir():
            try:
                # 确保目标父目录存在
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 复制整个目录树
                if dest_path.exists():
                    shutil.rmtree(dest_path)
                shutil.copytree(str(source_path), str(dest_path))
                
                print(f"   ✅ 复制目录: {source} → {destination}")
                
            except Exception as e:
                print(f"   ❌ 复制目录失败: {source} → {destination} ({e})")

def copy_scripts_to_organized_structure():
    """将scripts目录中的文件复制到整理后的结构"""
    
    print("\n🔧 整理scripts目录...")
    
    scripts_mapping = {
        # 设置脚本
        "scripts/setup_project.py": "scripts/setup/",
        "scripts/check_setup.py": "scripts/setup/",
        
        # 下载脚本
        "scripts/download_dataset_local.py": "scripts/setup/",
        "scripts/download_roboflow_dataset.py": "scripts/setup/",
        "scripts/download_satellite_dataset.py": "scripts/setup/",
        
        # 训练脚本
        "scripts/train_expert_local.py": "scripts/training/",
        "scripts/train_model.py": "scripts/training/",
    }
    
    for source, destination in scripts_mapping.items():
        source_path = Path(source)
        dest_path = Path(destination)
        
        if source_path.exists():
            try:
                dest_path.mkdir(parents=True, exist_ok=True)
                dest_file = dest_path / source_path.name
                shutil.copy2(str(source_path), str(dest_file))
                print(f"   ✅ 复制脚本: {source} → {destination}")
            except Exception as e:
                print(f"   ❌ 复制脚本失败: {source} → {destination} ({e})")

def create_clean_root_summary():
    """创建清理后的根目录总结"""
    
    print("\n📋 创建根目录清理总结...")
    
    # 统计根目录文件
    root_files = []
    for item in Path(".").iterdir():
        if item.is_file() and not item.name.startswith('.'):
            root_files.append(item.name)
    
    # 创建总结
    summary = {
        "organization_phase": "Root Directory Cleanup",
        "remaining_root_files": len(root_files),
        "root_files_list": sorted(root_files),
        "organized_structure": {
            "docs/": {
                "technical_reports/": "Technical documentation",
                "visualization/": "Visualization results",
                "legacy/": "Historical documents",
                "project_management/": "Project management files",
                "setup_guides/": "Setup and configuration guides"
            },
            "src/": {
                "training/": "Training scripts",
                "evaluation/": "Evaluation scripts",
                "visualization/": "Visualization scripts",
                "utils/": "Utility functions"
            },
            "scripts/": {
                "setup/": "Setup and installation scripts",
                "training/": "Training pipeline scripts",
                "evaluation/": "Evaluation scripts",
                "utilities/": "Utility scripts",
                "legacy/": "Legacy scripts"
            },
            "archive/": {
                "legacy_docs/": "Historical documents",
                "legacy_scripts/": "Historical scripts",
                "japanese_content/": "Japanese version content",
                "original_content/": "Original files",
                "versions/": "Version history"
            },
            "outputs/": {
                "training/": "Training outputs",
                "evaluation/": "Evaluation outputs",
                "visualization/": "Visualization outputs",
                "legacy_results/": "Historical results"
            },
            "configs/": "Configuration files",
            "notebooks/": "Jupyter notebooks"
        },
        "benefits": [
            "Clean root directory",
            "Logical file organization",
            "Easy navigation",
            "Professional structure",
            "Preserved compatibility"
        ]
    }
    
    with open("root_cleanup_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print("   ✅ 创建root_cleanup_summary.json")

def create_final_project_readme():
    """创建最终的项目README"""
    
    print("\n📝 创建最终项目README...")
    
    readme_content = """# 🏠 Roof Detection Project | 屋顶检测项目

## 📋 Project Overview | 项目概述

This project implements a high-performance roof detection system using YOLOv8l-seg, achieving **90.77% mAP@0.5** performance through systematic optimization and innovative training strategies.

本项目实现了基于YOLOv8l-seg的高性能屋顶检测系统，通过系统性优化和创新训练策略达到了**90.77% mAP@0.5**的性能。

## 🎯 Key Achievements | 主要成果

- **Performance**: 90.77% mAP@0.5, 80.85% mAP@0.5:0.95
- **Improvement**: +42.7% mAP@0.5 from baseline
- **Innovation**: Solved YOLOv8 class_weights limitation
- **Production Ready**: Immediately deployable model

## 📁 Clean Project Structure | 清洁的项目结构

### 🗂️ Organized Layout | 整理后的布局

```
roof_pre/
├── 📚 docs/                          # Documentation | 文档
│   ├── technical_reports/             # Technical reports | 技术报告
│   ├── visualization/                 # Visualization results | 可视化结果
│   ├── legacy/                        # Legacy documents | 历史文档
│   ├── project_management/            # Project management | 项目管理
│   └── setup_guides/                  # Setup guides | 设置指南
├── 💻 src/                           # Source code | 源代码
│   ├── training/                      # Training scripts | 训练脚本
│   ├── evaluation/                    # Evaluation scripts | 评估脚本
│   ├── visualization/                 # Visualization scripts | 可视化脚本
│   └── utils/                         # Utility functions | 工具函数
├── 🔧 scripts/                       # Scripts | 脚本
│   ├── setup/                         # Setup scripts | 设置脚本
│   ├── training/                      # Training scripts | 训练脚本
│   ├── evaluation/                    # Evaluation scripts | 评估脚本
│   └── utilities/                     # Utility scripts | 工具脚本
├── 📦 archive/                       # Archive | 归档
│   ├── legacy_scripts/                # Legacy scripts | 历史脚本
│   ├── legacy_docs/                   # Legacy documents | 历史文档
│   ├── japanese_content/              # Japanese content | 日文内容
│   ├── original_content/              # Original content | 原始内容
│   └── versions/                      # Version history | 版本历史
├── 📊 data/                          # Data | 数据
├── 🤖 models/                        # Models | 模型
├── 📈 outputs/                       # Outputs | 输出
├── ⚙️ configs/                       # Configuration | 配置
├── 📓 notebooks/                     # Jupyter notebooks | Jupyter笔记本
└── 🏃 runs/                          # Training runs | 训练运行
```

## 🚀 Quick Start | 快速开始

### 1. Setup | 设置
```bash
# Install dependencies | 安装依赖
pip install -r configs/requirements.txt

# Setup environment | 设置环境
conda env create -f configs/environment.yml
```

### 2. Training | 训练
```bash
# Use organized structure | 使用整理后的结构
python src/training/train_improved_compatible.py

# Or use original files | 或使用原始文件
python train_improved_compatible.py
```

### 3. Evaluation | 评估
```bash
# Organized way | 整理方式
python src/evaluation/evaluate_improvements.py

# Original way | 原始方式
python evaluate_improvements.py
```

### 4. Visualization | 可视化
```bash
# View results | 查看结果
open docs/visualization/index.html

# Generate new visualizations | 生成新可视化
python src/visualization/visualize_results_demo.py
```

## 📚 Documentation | 文档

### 📖 Technical Reports | 技术报告
- **[Bilingual Technical Report](docs/technical_reports/BILINGUAL_TECHNICAL_REPORT.md)** - Complete analysis
- **[Performance Analysis](docs/technical_reports/BILINGUAL_PERFORMANCE_ANALYSIS.md)** - Detailed metrics
- **[Deployment Guide](docs/technical_reports/BILINGUAL_DEPLOYMENT_GUIDE.md)** - Production deployment

### 🎨 Visualization | 可视化
- **[Multi-language Gallery](docs/visualization/index.html)** - Interactive results
- **[Chinese Gallery](docs/visualization/results_gallery.html)** - 中文版
- **[English Gallery](docs/visualization/results_gallery_en.html)** - English version
- **[Japanese Gallery](docs/visualization/results_gallery_ja.html)** - 日本語版

### 📋 Project Management | 项目管理
- **[Project Navigation](docs/project_management/PROJECT_NAVIGATION.md)** - Navigation guide
- **[Organization Summary](docs/project_management/organization_summary.json)** - Structure summary

## 🔬 Technical Highlights | 技术亮点

### 🎯 Innovations | 创新点
1. **YOLOv8 Class Weights Solution** - Solved parameter limitation
2. **Data-Driven Weight Calculation** - Inverse frequency algorithm
3. **Two-Stage Training Strategy** - Aggressive + fine-tuning
4. **Advanced Data Augmentation** - Copy-paste + mosaic

### 📊 Performance | 性能
- **mAP@0.5**: 63.62% → 90.77% (+42.7%)
- **mAP@0.5:0.95**: 49.86% → 80.85% (+62.1%)
- **Class Balance**: Improved minority class performance by 25-30%
- **Production Ready**: Immediately deployable

## 🗂️ File Organization | 文件组织

This project maintains a **dual structure**:
- **Original files**: Preserved for compatibility
- **Organized structure**: Professional layout for development

Both structures coexist to ensure no functionality is lost while providing improved organization.

## 📄 License | 许可证

This project is licensed under the MIT License.

## 🤝 Contributing | 贡献

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Status**: ✅ Production Ready | 生产就绪  
**Performance**: 🏆 90.77% mAP@0.5  
**Organization**: 📁 Clean & Professional | 清洁专业  
**Documentation**: 📚 Complete | 完整  
"""
    
    with open("README_FINAL.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("   ✅ 创建README_FINAL.md")

def main():
    """主函数"""
    
    print("🗂️ 开始整理剩余根目录文件...")
    print("=" * 60)
    print("⚠️  注意：此脚本只复制文件，不删除任何原文件")
    print("=" * 60)
    
    # 1. 创建额外目录
    create_additional_directories()
    
    # 2. 整理剩余文件
    organize_remaining_files()
    
    # 3. 整理剩余目录
    organize_directories()
    
    # 4. 整理scripts目录
    copy_scripts_to_organized_structure()
    
    # 5. 创建清理总结
    create_clean_root_summary()
    
    # 6. 创建最终README
    create_final_project_readme()
    
    print("\n" + "=" * 60)
    print("✅ 根目录文件整理完成!")
    
    print("\n📁 整理成果:")
    print("   📚 docs/ - 完整文档结构")
    print("   💻 src/ - 源代码组织")
    print("   🔧 scripts/ - 脚本分类")
    print("   📦 archive/ - 历史内容归档")
    print("   📈 outputs/ - 结果输出")
    print("   ⚙️ configs/ - 配置文件")
    
    print("\n🎯 根目录现在包含:")
    print("   - 核心项目文件 (README, runs/, etc.)")
    print("   - 整理后的目录结构")
    print("   - 原始文件保持不变")
    print("   - 专业的项目布局")
    
    print("\n✅ 优势:")
    print("   - 清洁的根目录")
    print("   - 逻辑文件组织")
    print("   - 保持向后兼容")
    print("   - 专业项目结构")

if __name__ == "__main__":
    main()
