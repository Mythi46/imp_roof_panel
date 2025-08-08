#!/usr/bin/env python3
"""
项目文件整理脚本
Project File Organization Script

重新组织项目文件结构，使其更加清晰和专业
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
        
        # 数据和模型
        "data",                          # 数据
        "data/raw",                      # 原始数据
        "data/processed",                # 处理后数据
        "models",                        # 模型
        "models/pretrained",             # 预训练模型
        "models/trained",                # 训练后模型
        
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
        
        # 归档
        "archive",                       # 归档文件
        "archive/old_scripts",           # 旧脚本
        "archive/old_docs",              # 旧文档
    ]
    
    # 创建目录
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ 创建目录: {directory}")

def organize_files():
    """整理现有文件到新结构中"""
    
    print("\n📁 整理现有文件...")
    
    # 文件移动映射
    file_moves = {
        # 技术报告
        "technical_report/": "docs/technical_reports/",
        
        # 可视化结果
        "visualization_results/": "docs/visualization/",
        
        # 历史文档 - 移动到legacy
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
        
        # 训练脚本
        "train_improved_compatible.py": "src/training/",
        "train_improved_v2.py": "src/training/",
        "train_expert_correct_solution.py": "src/training/",
        "continue_training_optimized.py": "src/training/",
        "start_training.py": "src/training/",
        
        # 评估脚本
        "analyze_dataset_and_improve.py": "src/evaluation/",
        "evaluate_improvements.py": "src/evaluation/",
        "analyze_detection_results.py": "src/evaluation/",
        
        # 可视化脚本
        "generate_visualization_results.py": "src/visualization/",
        "generate_english_visualization.py": "src/visualization/",
        "visualize_results_demo.py": "src/visualization/",
        
        # 监控脚本
        "monitor_training.py": "src/utils/",
        "monitor_continue_training.py": "src/utils/",
        
        # 测试脚本
        "quick_test_expert_improvements.py": "scripts/evaluation/",
        
        # 配置文件
        "config/": "configs/",
        
        # 设置脚本
        "setup.py": "scripts/setup/",
        "cleanup_project.py": "scripts/setup/",
        
        # 笔记本
        "roof_detection_expert_improved.ipynb": "notebooks/experiments/",
        "satellite_detection_expert_final.ipynb": "notebooks/experiments/",
        
        # 结果文件
        "results/": "outputs/",
        
        # 归档
        "original_files/": "archive/old_docs/",
        "japanese_version/": "archive/",
        "versions/": "archive/",
    }
    
    # 执行文件移动
    for source, destination in file_moves.items():
        source_path = Path(source)
        dest_path = Path(destination)
        
        if source_path.exists():
            try:
                if source_path.is_dir():
                    # 移动目录
                    if source.endswith('/'):
                        # 移动目录内容
                        dest_dir = dest_path / source_path.name
                        dest_dir.mkdir(parents=True, exist_ok=True)
                        shutil.copytree(source_path, dest_dir, dirs_exist_ok=True)
                        shutil.rmtree(source_path)
                    else:
                        # 移动整个目录
                        shutil.move(str(source_path), str(dest_path))
                else:
                    # 移动文件
                    dest_path.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(source_path), str(dest_path / source_path.name))
                
                print(f"   ✅ 移动: {source} → {destination}")
                
            except Exception as e:
                print(f"   ❌ 移动失败: {source} → {destination} ({e})")

def create_new_readme():
    """创建新的README文件"""
    
    print("\n📝 创建新的README文件...")
    
    readme_content = """# 🏠 Roof Detection Project | 屋顶检测项目

## 📋 Project Overview | 项目概述

This project implements a high-performance roof detection system using YOLOv8l-seg, achieving **90.77% mAP@0.5** performance through systematic optimization and innovative training strategies.

本项目实现了基于YOLOv8l-seg的高性能屋顶检测系统，通过系统性优化和创新训练策略达到了**90.77% mAP@0.5**的性能。

## 🎯 Key Achievements | 主要成果

- **Performance**: 90.77% mAP@0.5, 80.85% mAP@0.5:0.95
- **Improvement**: +42.7% mAP@0.5 from baseline
- **Innovation**: Solved YOLOv8 class_weights limitation
- **Production Ready**: Immediately deployable model

## 📁 Project Structure | 项目结构

```
roof_pre/
├── 📚 docs/                          # Documentation | 文档
│   ├── technical_reports/             # Technical reports | 技术报告
│   ├── visualization/                 # Visualization results | 可视化结果
│   └── legacy/                        # Legacy documents | 历史文档
├── 💻 src/                           # Source code | 源代码
│   ├── training/                      # Training scripts | 训练脚本
│   ├── evaluation/                    # Evaluation scripts | 评估脚本
│   ├── visualization/                 # Visualization scripts | 可视化脚本
│   └── utils/                         # Utility functions | 工具函数
├── 🔧 scripts/                       # Scripts | 脚本
│   ├── setup/                         # Setup scripts | 设置脚本
│   ├── training/                      # Training scripts | 训练脚本
│   └── evaluation/                    # Evaluation scripts | 评估脚本
├── 📊 data/                          # Data | 数据
│   ├── raw/                           # Raw data | 原始数据
│   └── processed/                     # Processed data | 处理后数据
├── 🤖 models/                        # Models | 模型
│   ├── pretrained/                    # Pretrained models | 预训练模型
│   └── trained/                       # Trained models | 训练后模型
├── 📈 outputs/                       # Outputs | 输出
│   ├── training/                      # Training outputs | 训练输出
│   ├── evaluation/                    # Evaluation outputs | 评估输出
│   └── visualization/                 # Visualization outputs | 可视化输出
├── ⚙️ configs/                       # Configuration files | 配置文件
├── 📓 notebooks/                     # Jupyter notebooks | Jupyter笔记本
│   ├── experiments/                   # Experiment notebooks | 实验笔记本
│   └── analysis/                      # Analysis notebooks | 分析笔记本
└── 📦 archive/                       # Archive | 归档
```

## 🚀 Quick Start | 快速开始

### 1. Environment Setup | 环境设置

```bash
# Install dependencies | 安装依赖
pip install -r requirements.txt

# Setup project | 设置项目
python scripts/setup/setup.py
```

### 2. Training | 训练

```bash
# Run optimized training | 运行优化训练
python src/training/train_improved_compatible.py

# Continue training | 继续训练
python src/training/continue_training_optimized.py
```

### 3. Evaluation | 评估

```bash
# Evaluate model | 评估模型
python src/evaluation/evaluate_improvements.py

# Analyze results | 分析结果
python src/evaluation/analyze_detection_results.py
```

### 4. Visualization | 可视化

```bash
# Generate visualization | 生成可视化
python src/visualization/visualize_results_demo.py

# View results | 查看结果
open docs/visualization/index.html
```

## 📚 Documentation | 文档

### Technical Reports | 技术报告

- **[Bilingual Technical Report](docs/technical_reports/BILINGUAL_TECHNICAL_REPORT.md)** - Complete technical analysis | 完整技术分析
- **[Performance Analysis](docs/technical_reports/BILINGUAL_PERFORMANCE_ANALYSIS.md)** - Detailed performance metrics | 详细性能指标
- **[Deployment Guide](docs/technical_reports/BILINGUAL_DEPLOYMENT_GUIDE.md)** - Production deployment | 生产部署

### Visualization | 可视化

- **[Multi-language Gallery](docs/visualization/index.html)** - Interactive results viewer | 交互式结果查看器
- **[Chinese Gallery](docs/visualization/results_gallery.html)** - 中文版结果展示
- **[English Gallery](docs/visualization/results_gallery_en.html)** - English results display
- **[Japanese Gallery](docs/visualization/results_gallery_ja.html)** - 日本語結果表示

## 🔬 Technical Highlights | 技术亮点

### Innovations | 创新点

1. **YOLOv8 Class Weights Solution** - Solved parameter limitation issue
2. **Data-Driven Weight Calculation** - Inverse frequency weighting algorithm
3. **Two-Stage Training Strategy** - Aggressive + fine-tuning optimization
4. **Advanced Data Augmentation** - Copy-paste + mosaic strategies

### Performance | 性能

- **mAP@0.5**: 63.62% → 90.77% (+42.7%)
- **mAP@0.5:0.95**: 49.86% → 80.85% (+62.1%)
- **Class Balance**: Improved minority class performance by 25-30%
- **Production Ready**: Immediately deployable with excellent stability

## 🛠️ Development | 开发

### Requirements | 要求

- Python 3.8+
- PyTorch 2.0+
- Ultralytics 8.3+
- CUDA 11.8+ (recommended)

### Model | 模型

- **Architecture**: YOLOv8l-seg
- **Parameters**: 45.9M
- **Input Size**: 896×896
- **Classes**: 4 (roof, farm, rice-fields, Baren-Land)

## 📄 License | 许可证

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing | 贡献

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Contact | 联系

For questions and support, please open an issue on GitHub.

---

**Status**: ✅ Production Ready | 生产就绪  
**Performance**: 🏆 90.77% mAP@0.5  
**Documentation**: 📚 Complete | 完整  
**Deployment**: 🚀 Ready | 就绪  
"""
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("   ✅ 创建新的README.md")

def create_project_info():
    """创建项目信息文件"""
    
    print("\n📋 创建项目信息文件...")
    
    project_info = {
        "name": "Roof Detection Project",
        "version": "1.0.0",
        "description": "High-performance roof detection system using YOLOv8l-seg",
        "performance": {
            "mAP@0.5": "90.77%",
            "mAP@0.5:0.95": "80.85%",
            "improvement": "+42.7%"
        },
        "structure": {
            "docs": "Documentation and reports",
            "src": "Source code",
            "scripts": "Utility scripts",
            "data": "Dataset files",
            "models": "Model files",
            "outputs": "Training and evaluation outputs",
            "configs": "Configuration files",
            "notebooks": "Jupyter notebooks",
            "archive": "Archived files"
        },
        "status": "Production Ready",
        "last_updated": "2025-01-28"
    }
    
    with open("project_info.json", "w", encoding="utf-8") as f:
        json.dump(project_info, f, indent=2, ensure_ascii=False)
    
    print("   ✅ 创建project_info.json")

def cleanup_root_directory():
    """清理根目录中的临时文件"""
    
    print("\n🧹 清理根目录...")
    
    # 要删除的文件和目录
    cleanup_items = [
        "yolo11n.pt",  # 临时模型文件
    ]
    
    for item in cleanup_items:
        item_path = Path(item)
        if item_path.exists():
            try:
                if item_path.is_dir():
                    shutil.rmtree(item_path)
                else:
                    item_path.unlink()
                print(f"   ✅ 删除: {item}")
            except Exception as e:
                print(f"   ❌ 删除失败: {item} ({e})")

def main():
    """主函数"""
    
    print("🗂️ 开始项目文件整理...")
    print("=" * 50)
    
    # 1. 创建标准化目录结构
    create_organized_structure()
    
    # 2. 整理现有文件
    organize_files()
    
    # 3. 创建新的README
    create_new_readme()
    
    # 4. 创建项目信息文件
    create_project_info()
    
    # 5. 清理根目录
    cleanup_root_directory()
    
    print("\n" + "=" * 50)
    print("✅ 项目文件整理完成!")
    print("\n📁 新的项目结构:")
    print("   📚 docs/ - 所有文档和报告")
    print("   💻 src/ - 源代码")
    print("   🔧 scripts/ - 脚本文件")
    print("   📊 data/ - 数据文件")
    print("   🤖 models/ - 模型文件")
    print("   📈 outputs/ - 输出结果")
    print("   ⚙️ configs/ - 配置文件")
    print("   📓 notebooks/ - Jupyter笔记本")
    print("   📦 archive/ - 归档文件")
    
    print("\n🎯 下一步:")
    print("   1. 检查新的项目结构")
    print("   2. 测试脚本是否正常工作")
    print("   3. 更新导入路径（如果需要）")
    print("   4. 提交到Git")

if __name__ == "__main__":
    main()
