# 🏠 Roof Detection Project | 屋顶检测项目

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
