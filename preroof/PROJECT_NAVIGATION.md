# 🧭 Project Navigation Guide | 项目导航指南

## 📋 Overview | 概述

This project now has **dual structure** - original files are preserved for compatibility, while organized copies provide better navigation and development experience.

本项目现在具有**双重结构** - 原始文件保持兼容性，整理后的副本提供更好的导航和开发体验。

## 🗂️ Dual Structure Explanation | 双重结构说明

### 📂 Original Structure (Preserved) | 原始结构（保留）
All original files remain in their original locations to ensure:
- ✅ **Backward compatibility** | 向后兼容性
- ✅ **Existing scripts work** | 现有脚本正常工作
- ✅ **No broken imports** | 无导入错误
- ✅ **Git history intact** | Git历史完整

### 📁 Organized Structure (New) | 整理结构（新）
Organized copies provide:
- ✅ **Better navigation** | 更好的导航
- ✅ **Logical grouping** | 逻辑分组
- ✅ **Professional layout** | 专业布局
- ✅ **Easier development** | 更容易开发

## 🎯 Quick Access Guide | 快速访问指南

### 🚀 Getting Started | 开始使用

#### Original Way (Still Works) | 原始方式（仍然有效）
```bash
# Training | 训练
python train_improved_compatible.py

# Evaluation | 评估
python evaluate_improvements.py

# Visualization | 可视化
python visualize_results_demo.py
```

#### Organized Way (Recommended) | 整理方式（推荐）
```bash
# Training | 训练
python src/training/train_improved_compatible.py

# Evaluation | 评估
python src/evaluation/evaluate_improvements.py

# Visualization | 可视化
python src/visualization/visualize_results_demo.py
```

### 📚 Documentation Access | 文档访问

#### Technical Reports | 技术报告
- **Original**: `technical_report/`
- **Organized**: `docs/technical_reports/`

#### Visualization Results | 可视化结果
- **Original**: `visualization_results/`
- **Organized**: `docs/visualization/`

#### Key Documents | 关键文档
- **Main README**: `README.md` (original)
- **Organized README**: `README_ORGANIZED.md` (new)
- **Navigation Guide**: `PROJECT_NAVIGATION.md` (this file)

## 📁 Directory Mapping | 目录映射

### 📊 Source Code | 源代码
| Original Location | Organized Location | Description |
|-------------------|-------------------|-------------|
| `train_*.py` | `src/training/` | Training scripts |
| `analyze_*.py` | `src/evaluation/` | Analysis scripts |
| `generate_*.py` | `src/visualization/` | Visualization scripts |
| `monitor_*.py` | `src/utils/` | Utility scripts |

### 📚 Documentation | 文档
| Original Location | Organized Location | Description |
|-------------------|-------------------|-------------|
| `technical_report/` | `docs/technical_reports/` | Technical reports |
| `visualization_results/` | `docs/visualization/` | Visualization results |
| `*.md` (root) | `docs/legacy/` | Legacy documents |

### ⚙️ Configuration | 配置
| Original Location | Organized Location | Description |
|-------------------|-------------------|-------------|
| `config/` | `configs/` | Configuration files |
| `setup.py` | `scripts/setup/` | Setup scripts |

### 📓 Notebooks | 笔记本
| Original Location | Organized Location | Description |
|-------------------|-------------------|-------------|
| `*.ipynb` (root) | `notebooks/experiments/` | Jupyter notebooks |
| `notebooks/` | `notebooks/experiments/` | Experiment notebooks |

## 🎯 Recommended Usage | 推荐使用方式

### 👨‍💻 For Development | 开发使用
Use the **organized structure** for new development:
```bash
# Navigate to organized code
cd src/training/
python train_improved_compatible.py

# View organized documentation
open docs/technical_reports/BILINGUAL_TECHNICAL_REPORT.md
```

### 🔄 For Compatibility | 兼容性使用
Use the **original structure** for existing workflows:
```bash
# Existing scripts still work
python train_improved_compatible.py
python evaluate_improvements.py
```

### 📖 For Documentation | 文档使用
Access documentation from either location:
```bash
# Original location
open technical_report/BILINGUAL_TECHNICAL_REPORT.md

# Organized location (recommended)
open docs/technical_reports/BILINGUAL_TECHNICAL_REPORT.md
```

## 🔍 Finding Files | 查找文件

### 🎯 By Function | 按功能查找

#### Training Scripts | 训练脚本
- **Original**: Root directory (`train_*.py`)
- **Organized**: `src/training/`

#### Evaluation Scripts | 评估脚本
- **Original**: Root directory (`analyze_*.py`, `evaluate_*.py`)
- **Organized**: `src/evaluation/`

#### Visualization Scripts | 可视化脚本
- **Original**: Root directory (`generate_*.py`, `visualize_*.py`)
- **Organized**: `src/visualization/`

#### Documentation | 文档
- **Original**: `technical_report/`, `visualization_results/`
- **Organized**: `docs/technical_reports/`, `docs/visualization/`

### 📊 By Type | 按类型查找

#### Python Scripts | Python脚本
- **Training**: `src/training/` or root
- **Evaluation**: `src/evaluation/` or root
- **Visualization**: `src/visualization/` or root
- **Utilities**: `src/utils/` or root

#### Documentation Files | 文档文件
- **Technical Reports**: `docs/technical_reports/` or `technical_report/`
- **Visualization**: `docs/visualization/` or `visualization_results/`
- **Legacy Docs**: `docs/legacy/` or root

#### Configuration Files | 配置文件
- **Configs**: `configs/` or `config/`
- **Setup**: `scripts/setup/` or root

## 🎉 Benefits of Dual Structure | 双重结构的优势

### ✅ Advantages | 优势
1. **Zero Breaking Changes** | 零破坏性变更
   - All existing scripts continue to work
   - No import path changes needed
   - Git history preserved

2. **Improved Organization** | 改进的组织
   - Logical file grouping
   - Better navigation
   - Professional structure

3. **Flexible Usage** | 灵活使用
   - Choose your preferred structure
   - Gradual migration possible
   - Both structures maintained

4. **Enhanced Development** | 增强开发
   - Easier to find files
   - Better code organization
   - Cleaner project layout

### 🎯 Best Practices | 最佳实践
1. **New Development**: Use organized structure (`src/`, `docs/`)
2. **Existing Scripts**: Continue using original locations
3. **Documentation**: Prefer organized locations (`docs/`)
4. **Configuration**: Use organized configs (`configs/`)

## 📞 Support | 支持

If you have questions about the project structure:
1. Check this navigation guide
2. Look at `README_ORGANIZED.md`
3. Review `organization_summary.json`
4. Refer to original `README.md`

---

**Project Status**: ✅ Dual Structure Complete | 双重结构完成  
**Compatibility**: 🔄 100% Backward Compatible | 100%向后兼容  
**Organization**: 📁 Professional Structure Available | 专业结构可用  
**Usage**: 🎯 Choose Your Preferred Approach | 选择您偏好的方式  

---

*This dual structure approach ensures no functionality is lost while providing improved organization for future development.*
