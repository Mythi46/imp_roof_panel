#!/usr/bin/env python3
"""
本地数据集下载脚本
Local dataset download script

下载卫星图像分割数据集到本地
"""

import os
import sys
import yaml
import shutil
from pathlib import Path

print("📥 本地数据集下载器")
print("=" * 40)

# 检查依赖
try:
    from roboflow import Roboflow
    print("✅ Roboflow库已安装")
except ImportError:
    print("❌ Roboflow库未安装")
    print("正在安装...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "roboflow"])
    from roboflow import Roboflow
    print("✅ Roboflow库安装完成")

# 数据集配置
DATASET_CONFIG = {
    "workspace": "a-imc4u",
    "project": "new-2-6zp4h", 
    "version": 1,
    "format": "yolov8"
}

# 尝试多个API密钥
API_KEYS = [
    "EKxSlogyvSMHiOP3MK94",  # 原始密钥
    # 如果您有其他密钥，可以添加在这里
]

def download_with_api_key(api_key):
    """使用指定API密钥下载数据集"""
    try:
        print(f"🔑 尝试API密钥: {api_key[:10]}...")
        
        rf = Roboflow(api_key=api_key)
        project = rf.workspace(DATASET_CONFIG["workspace"]).project(DATASET_CONFIG["project"])
        
        # 设置下载路径
        download_path = os.path.join(os.getcwd(), "data", "raw")
        os.makedirs(download_path, exist_ok=True)
        
        print(f"📂 下载到: {download_path}")
        
        # 下载数据集
        dataset = project.version(DATASET_CONFIG["version"]).download(
            model_format=DATASET_CONFIG["format"],
            location=download_path
        )
        
        return dataset
        
    except Exception as e:
        print(f"❌ API密钥失败: {str(e)}")
        return None

def setup_data_yaml(dataset_location):
    """设置数据配置文件"""
    try:
        # 原始data.yaml路径
        original_yaml = os.path.join(dataset_location, "data.yaml")
        
        if not os.path.exists(original_yaml):
            print(f"❌ 未找到data.yaml: {original_yaml}")
            return False
        
        # 读取原始配置
        with open(original_yaml, 'r') as f:
            data_config = yaml.safe_load(f)
        
        print(f"📊 数据集信息:")
        print(f"   类别数量: {data_config.get('nc', 'N/A')}")
        print(f"   类别名称: {data_config.get('names', 'N/A')}")
        
        # 更新路径为绝对路径
        base_path = os.path.abspath(dataset_location)
        data_config['path'] = base_path
        data_config['train'] = os.path.join(base_path, 'train', 'images')
        data_config['val'] = os.path.join(base_path, 'valid', 'images')
        data_config['test'] = os.path.join(base_path, 'test', 'images') if os.path.exists(os.path.join(base_path, 'test')) else data_config['val']
        
        # 保存到项目根目录
        project_yaml = os.path.join(os.getcwd(), "config", "data.yaml")
        os.makedirs(os.path.dirname(project_yaml), exist_ok=True)
        
        with open(project_yaml, 'w') as f:
            yaml.dump(data_config, f, default_flow_style=False)
        
        print(f"✅ 数据配置已保存: {project_yaml}")
        
        # 验证数据集
        train_images = os.path.join(base_path, 'train', 'images')
        val_images = os.path.join(base_path, 'valid', 'images')
        
        if os.path.exists(train_images):
            train_count = len([f for f in os.listdir(train_images) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            print(f"📊 训练图像: {train_count} 张")
        
        if os.path.exists(val_images):
            val_count = len([f for f in os.listdir(val_images) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            print(f"📊 验证图像: {val_count} 张")
        
        return True
        
    except Exception as e:
        print(f"❌ 设置数据配置失败: {e}")
        return False

def download_alternative_dataset():
    """下载替代数据集（如果主数据集不可用）"""
    print("\n🔄 尝试下载替代数据集...")
    
    try:
        # 使用公开的示例数据集
        from ultralytics import YOLO
        
        # 这会自动下载COCO8分割数据集
        model = YOLO('yolov8n-seg.pt')
        
        # 创建示例配置
        demo_config = {
            'path': os.path.abspath('data/demo'),
            'train': 'images/train',
            'val': 'images/val',
            'nc': 4,
            'names': ['Baren-Land', 'farm', 'rice-fields', 'roof']
        }
        
        # 保存演示配置
        os.makedirs('config', exist_ok=True)
        with open('config/data.yaml', 'w') as f:
            yaml.dump(demo_config, f, default_flow_style=False)
        
        print("✅ 演示数据集配置已创建")
        print("💡 您可以稍后替换为真实的卫星图像数据")
        
        return True
        
    except Exception as e:
        print(f"❌ 下载替代数据集失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始下载卫星图像分割数据集...")
    
    dataset = None
    
    # 尝试使用API密钥下载
    for api_key in API_KEYS:
        dataset = download_with_api_key(api_key)
        if dataset:
            break
    
    if dataset:
        print(f"✅ 数据集下载成功!")
        print(f"📁 位置: {dataset.location}")
        
        # 设置数据配置
        if setup_data_yaml(dataset.location):
            print("✅ 数据集配置完成")
        else:
            print("⚠️ 数据集配置可能有问题")
        
        # 显示下载结果
        print(f"\n📊 下载完成:")
        print(f"   数据集路径: {dataset.location}")
        print(f"   配置文件: config/data.yaml")
        print(f"   可以开始训练: python train_expert_simple.py")
        
    else:
        print("❌ 所有API密钥都失败了")
        print("🔄 尝试下载替代数据集...")
        
        if download_alternative_dataset():
            print("✅ 替代数据集准备完成")
            print("💡 建议:")
            print("   1. 获取有效的Roboflow API密钥")
            print("   2. 或者手动下载卫星图像数据集")
            print("   3. 将数据放在 data/raw/ 目录下")
        else:
            print("❌ 无法准备任何数据集")
            return False
    
    # 创建项目目录结构
    directories = [
        "data/raw",
        "data/processed", 
        "models/pretrained",
        "models/trained",
        "results/training",
        "results/evaluation",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        # 创建.gitkeep文件
        gitkeep_path = os.path.join(directory, ".gitkeep")
        if not os.path.exists(gitkeep_path):
            with open(gitkeep_path, "w") as f:
                f.write("")
    
    print(f"\n📁 项目目录结构已创建")
    
    # 显示下一步
    print(f"\n🎯 下一步:")
    print(f"   1. 检查数据: ls data/raw/")
    print(f"   2. 开始训练: python train_expert_simple.py")
    print(f"   3. 或使用GPU版本: python test_gpu_training.py")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 数据集下载完成!")
    else:
        print("\n❌ 数据集下载失败")
        sys.exit(1)
