# 🏠 本地专家改进版设置指南
# Local Expert Improved Version Setup Guide

## 🎯 概述

本指南专为本地conda环境`roof` (Python 3.10.18)设计，集成了所有专家改进功能。

## 📋 系统要求

### 最低要求
- Python 3.10.18
- 8GB RAM
- 10GB 磁盘空间
- Anaconda/Miniconda

### 推荐配置
- Python 3.10.18 (conda环境)
- 16GB+ RAM
- CUDA兼容GPU
- 20GB+ 磁盘空间

## 🚀 一键设置

### Windows
```cmd
# 运行一键设置脚本
setup_conda_environment.bat
```

### Linux/Mac
```bash
# 给脚本执行权限并运行
chmod +x setup_conda_environment.sh
./setup_conda_environment.sh
```

## 🔧 手动设置步骤

### 1. 创建Conda环境
```bash
# 使用environment.yml创建环境
conda env create -f environment.yml

# 激活环境
conda activate roof

# 验证Python版本
python --version  # 应该显示 Python 3.10.18
```

### 2. 安装专家改进版依赖
```bash
# 安装核心依赖
pip install ultralytics==8.3.3
pip install roboflow>=1.1.0
pip install rich>=13.0.0
pip install tensorboard>=2.13.0

# 验证安装
python -c "from ultralytics import YOLO; print('✅ Ultralytics安装成功')"
```

### 3. 项目结构设置
```bash
# 运行项目设置脚本
python setup_local_environment.py

# 检查项目结构
ls -la data/ models/ results/
```

### 4. 配置API密钥
```bash
# 编辑数据配置文件
nano config/data_config.yaml  # 或使用其他编辑器

# 替换API密钥
roboflow:
  api_key: "YOUR_API_KEY_HERE"  # 替换为您的密钥
```

## 🎯 专家改进功能

### 核心改进
1. **自动类别权重计算** - 基于有效样本数方法
2. **统一解像度768** - 训练验证推理一致
3. **余弦退火+AdamW** - 现代学习率策略
4. **分割友好数据增强** - 低Mosaic+Copy-Paste
5. **TTA+瓦片推理** - 高解像度支持

### 本地优化
- conda环境专用配置
- GPU/CPU自动检测
- 内存使用优化
- 本地路径管理

## 🚀 使用方法

### 方式1: 命令行训练
```bash
# 激活环境
conda activate roof

# 专家改进版训练（推荐）
python scripts/train_expert_local.py --download

# 自定义参数训练
python scripts/train_expert_local.py --epochs 100 --batch 8
```

### 方式2: Jupyter Notebook
```bash
# 激活环境
conda activate roof

# 启动notebook
jupyter notebook notebooks/01_专家改进版本地训练.ipynb
```

### 方式3: 传统方式（兼容）
```bash
# 传统训练脚本
python scripts/train_model.py --download
```

## 📊 预期效果

### 性能提升
- **mAP50**: 3-6个百分点提升
- **类别平衡**: F1标准偏差显著降低
- **训练稳定性**: 更平滑的收敛曲线
- **边缘质量**: 更精确的分割掩码

### 训练时间
- **GPU训练**: 1-3小时（取决于GPU性能）
- **CPU训练**: 8-24小时（不推荐）

## 🔍 验证安装

### 环境检查脚本
```bash
# 运行环境检查
python setup_local_environment.py

# 检查GPU可用性
python -c "import torch; print('GPU可用:', torch.cuda.is_available())"
```

### 快速测试
```bash
# 快速训练测试（5轮）
python scripts/train_expert_local.py --epochs 5 --batch 4
```

## 🔧 故障排除

### 常见问题

#### 1. Conda环境创建失败
```bash
# 清理conda缓存
conda clean --all

# 手动创建环境
conda create -n roof python=3.10.18
conda activate roof
pip install -r requirements.txt
```

#### 2. GPU不可用
```bash
# 检查CUDA版本
nvidia-smi

# 重新安装PyTorch
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
```

#### 3. 内存不足
```bash
# 减小batch size
python scripts/train_expert_local.py --batch 8 --imgsz 640
```

#### 4. 依赖冲突
```bash
# 重新创建环境
conda env remove -n roof
conda env create -f environment.yml
```

## 📁 文件结构

### 专家改进版文件
```
satellite-roof-detection/
├── environment.yml                    # Conda环境配置
├── setup_conda_environment.bat       # Windows设置脚本
├── setup_conda_environment.sh        # Linux/Mac设置脚本
├── setup_local_environment.py        # 本地环境设置
├── scripts/
│   └── train_expert_local.py         # 专家改进版训练脚本
├── notebooks/
│   └── 01_专家改进版本地训练.ipynb    # 专家改进版notebook
└── config/
    ├── local_config.yaml             # 本地配置
    └── model_config.yaml             # 模型配置
```

## 💡 最佳实践

### 训练建议
1. **首次训练**: 使用默认参数，观察收敛情况
2. **GPU内存不足**: 减小batch_size到8或4
3. **训练时间长**: 先用30epochs测试效果
4. **特定类别差**: 手动调整该类别权重

### 监控建议
1. **使用TensorBoard**: `tensorboard --logdir runs/segment`
2. **观察训练曲线**: 确保平滑收敛
3. **检查混淆矩阵**: 分析各类别性能
4. **验证推理效果**: 测试高分辨率图像

## 📞 技术支持

### 问题报告
1. 收集错误信息和日志
2. 记录系统环境信息
3. 提供复现步骤
4. 附上相关配置文件

### 联系方式
- GitHub Issues: 项目仓库
- 技术文档: 查看docs/目录
- 社区讨论: 项目讨论区

## 🎉 成功指标

安装成功后，您应该能够：
- ✅ 激活conda环境roof
- ✅ 运行专家改进版训练
- ✅ 看到自动计算的类别权重
- ✅ 观察到更稳定的训练曲线
- ✅ 获得更好的分割效果

恭喜您完成本地专家改进版的设置！🎊
