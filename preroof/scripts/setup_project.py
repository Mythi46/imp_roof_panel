#!/usr/bin/env python3
"""
项目初始化脚本
Project setup script
"""

import os
import sys
import subprocess
from pathlib import Path

def create_directories():
    """创建项目目录结构"""
    directories = [
        "data/raw",
        "data/processed/train/images",
        "data/processed/train/labels", 
        "data/processed/val/images",
        "data/processed/val/labels",
        "data/processed/test/images",
        "data/processed/test/labels",
        "data/external",
        "models/pretrained",
        "models/trained",
        "results/training",
        "results/evaluation", 
        "results/predictions",
        "logs",
        "notebooks",
        "tests"
    ]
    
    print("📁 创建项目目录结构...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✅ {directory}")
    
    print("✅ 目录结构创建完成!")

def create_gitignore():
    """创建.gitignore文件"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Jupyter Notebook
.ipynb_checkpoints

# Data
data/raw/*
data/processed/*
!data/raw/.gitkeep
!data/processed/.gitkeep

# Models
models/pretrained/*
models/trained/*
!models/pretrained/.gitkeep
!models/trained/.gitkeep

# Results
results/training/*
results/evaluation/*
results/predictions/*
!results/training/.gitkeep
!results/evaluation/.gitkeep
!results/predictions/.gitkeep

# Logs
logs/*
!logs/.gitkeep

# OS
.DS_Store
Thumbs.db

# YOLO specific
runs/
wandb/
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    
    print("✅ .gitignore 文件创建完成!")

def create_gitkeep_files():
    """创建.gitkeep文件以保持空目录"""
    gitkeep_dirs = [
        "data/raw",
        "data/processed", 
        "models/pretrained",
        "models/trained",
        "results/training",
        "results/evaluation",
        "results/predictions",
        "logs"
    ]
    
    for directory in gitkeep_dirs:
        gitkeep_path = os.path.join(directory, ".gitkeep")
        with open(gitkeep_path, "w") as f:
            f.write("")

def install_dependencies():
    """安装项目依赖"""
    print("📦 安装项目依赖...")
    
    try:
        # 检查是否在虚拟环境中
        if sys.prefix == sys.base_prefix:
            print("⚠️  建议在虚拟环境中运行此项目")
            response = input("是否继续安装依赖? (y/n): ")
            if response.lower() != 'y':
                return False
        
        # 安装依赖
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖安装完成!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def check_gpu():
    """检查GPU可用性"""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            print(f"🚀 检测到GPU: {gpu_name} (共{gpu_count}个)")
            return True
        else:
            print("⚠️  未检测到GPU，将使用CPU训练（速度较慢）")
            return False
    except ImportError:
        print("⚠️  PyTorch未安装，无法检测GPU")
        return False

def create_example_notebook():
    """创建示例notebook"""
    notebook_content = '''{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# 🛰️ 卫星图像分割检测 - 快速开始\\n",
    "\\n",
    "这是一个快速开始的示例notebook。"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# 导入必要的库\\n",
    "import sys\\n",
    "sys.path.append('..')\\n",
    "\\n",
    "from src.data.download_dataset import download_and_setup\\n",
    "from src.models.train import RoofDetectionTrainer\\n",
    "\\n",
    "print('✅ 导入成功!')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# 1. 下载和设置数据集\\n",
    "dataset_path = download_and_setup()\\n",
    "if dataset_path:\\n",
    "    print(f'✅ 数据集准备完成: {dataset_path}')\\n",
    "else:\\n",
    "    print('❌ 数据集准备失败，请检查配置')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# 2. 训练模型\\n",
    "trainer = RoofDetectionTrainer()\\n",
    "\\n",
    "# 验证设置\\n",
    "if trainer.validate_training_setup():\\n",
    "    print('✅ 训练设置验证通过')\\n",
    "    \\n",
    "    # 开始训练\\n",
    "    results = trainer.train(name='quick_start')\\n",
    "    print('🎉 训练完成!')\\n",
    "else:\\n",
    "    print('❌ 训练设置验证失败')"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}'''
    
    with open("notebooks/00_快速开始.ipynb", "w", encoding="utf-8") as f:
        f.write(notebook_content)
    
    print("✅ 示例notebook创建完成!")

def main():
    """主函数"""
    print("🚀 开始初始化卫星图像分割检测项目...")
    print("=" * 50)
    
    # 1. 创建目录结构
    create_directories()
    
    # 2. 创建.gitignore
    create_gitignore()
    
    # 3. 创建.gitkeep文件
    create_gitkeep_files()
    
    # 4. 创建示例notebook
    create_example_notebook()
    
    # 5. 安装依赖
    if install_dependencies():
        # 6. 检查GPU
        check_gpu()
    
    print("=" * 50)
    print("🎉 项目初始化完成!")
    print()
    print("📋 下一步:")
    print("1. 编辑 config/data_config.yaml 中的API密钥")
    print("2. 运行 python src/data/download_dataset.py 下载数据")
    print("3. 运行 python src/models/train.py 开始训练")
    print("4. 或者使用 notebooks/00_快速开始.ipynb")
    print()
    print("📚 更多信息请查看 README.md")

if __name__ == "__main__":
    main()
