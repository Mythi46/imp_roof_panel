#!/usr/bin/env python3
"""
项目设置检查脚本
Project setup check script
"""

import os
import sys
import importlib
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    print(f"🐍 Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python版本过低，需要Python 3.8+")
        return False
    else:
        print("✅ Python版本符合要求")
        return True

def check_virtual_environment():
    """检查是否在虚拟环境中"""
    in_venv = sys.prefix != sys.base_prefix
    if in_venv:
        print("✅ 运行在虚拟环境中")
        print(f"   环境路径: {sys.prefix}")
    else:
        print("⚠️  未在虚拟环境中运行")
        print("   建议使用虚拟环境以避免依赖冲突")
    return in_venv

def check_dependencies():
    """检查关键依赖包"""
    required_packages = [
        'ultralytics',
        'torch',
        'torchvision', 
        'opencv-python',
        'numpy',
        'pandas',
        'matplotlib',
        'yaml',
        'PIL'
    ]
    
    print("📦 检查依赖包...")
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'opencv-python':
                importlib.import_module('cv2')
            elif package == 'yaml':
                importlib.import_module('yaml')
            elif package == 'PIL':
                importlib.import_module('PIL')
            else:
                importlib.import_module(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("   运行: pip install -r requirements.txt")
        return False
    else:
        print("✅ 所有依赖包已安装")
        return True

def check_gpu():
    """检查GPU可用性"""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            print(f"🚀 GPU可用: {gpu_name} (共{gpu_count}个)")
            print(f"   CUDA版本: {torch.version.cuda}")
            return True
        else:
            print("⚠️  GPU不可用，将使用CPU训练")
            return False
    except ImportError:
        print("❌ PyTorch未安装，无法检测GPU")
        return False

def check_directories():
    """检查项目目录结构"""
    required_dirs = [
        "config",
        "src",
        "src/data", 
        "src/models",
        "src/utils",
        "scripts",
        "data",
        "data/raw",
        "data/processed",
        "models",
        "results",
        "notebooks"
    ]
    
    print("📁 检查目录结构...")
    missing_dirs = []
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"   ✅ {directory}")
        else:
            print(f"   ❌ {directory}")
            missing_dirs.append(directory)
    
    if missing_dirs:
        print(f"\n❌ 缺少目录: {', '.join(missing_dirs)}")
        print("   运行: python scripts/setup_project.py")
        return False
    else:
        print("✅ 目录结构完整")
        return True

def check_config_files():
    """检查配置文件"""
    config_files = [
        "config/data_config.yaml",
        "config/model_config.yaml",
        "requirements.txt",
        "README.md"
    ]
    
    print("⚙️  检查配置文件...")
    missing_files = []
    
    for file_path in config_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ 缺少配置文件: {', '.join(missing_files)}")
        return False
    else:
        print("✅ 配置文件完整")
        return True

def check_data_config():
    """检查数据配置"""
    try:
        import yaml
        config_path = "config/data_config.yaml"
        
        if not os.path.exists(config_path):
            print("❌ 数据配置文件不存在")
            return False
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # 检查API密钥
        api_key = config.get('roboflow', {}).get('api_key', '')
        if api_key == "YOUR_API_KEY_HERE" or not api_key:
            print("⚠️  Roboflow API密钥未配置")
            print("   请编辑 config/data_config.yaml 设置您的API密钥")
            return False
        else:
            print("✅ Roboflow API密钥已配置")
        
        # 检查类别权重
        class_weights = config.get('dataset', {}).get('class_weights', [])
        if class_weights:
            print(f"✅ 类别权重已配置: {class_weights}")
        else:
            print("⚠️  类别权重未配置")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据配置检查失败: {e}")
        return False

def check_ultralytics():
    """检查Ultralytics YOLO"""
    try:
        from ultralytics import YOLO
        print("✅ Ultralytics YOLO可用")
        
        # 尝试加载预训练模型
        try:
            model = YOLO('yolov8n.pt')  # 下载小模型测试
            print("✅ 预训练模型下载正常")
            return True
        except Exception as e:
            print(f"⚠️  预训练模型下载可能有问题: {e}")
            return False
            
    except ImportError:
        print("❌ Ultralytics YOLO不可用")
        return False

def main():
    """主函数"""
    print("🔍 卫星图像分割检测项目设置检查")
    print("=" * 50)
    
    checks = [
        ("Python版本", check_python_version),
        ("虚拟环境", check_virtual_environment),
        ("依赖包", check_dependencies),
        ("GPU支持", check_gpu),
        ("目录结构", check_directories),
        ("配置文件", check_config_files),
        ("数据配置", check_data_config),
        ("YOLO模型", check_ultralytics)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ 检查失败: {e}")
            results.append((name, False))
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 检查结果总结:")
    
    passed = 0
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"   {status} {name}")
        if result:
            passed += 1
    
    print(f"\n通过: {passed}/{len(results)}")
    
    if passed == len(results):
        print("\n🎉 所有检查通过！项目已准备就绪")
        print("\n📋 下一步:")
        print("   python scripts/train_model.py --download")
    else:
        print("\n⚠️  部分检查未通过，请根据上述提示进行修复")
        print("\n💡 常见解决方案:")
        print("   1. 运行: python scripts/setup_project.py")
        print("   2. 安装依赖: pip install -r requirements.txt")
        print("   3. 配置API密钥: 编辑 config/data_config.yaml")

if __name__ == "__main__":
    main()
