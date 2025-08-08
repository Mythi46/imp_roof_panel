#!/usr/bin/env python3
"""
Fix Dependencies Script
依赖修复脚本
"""
import os
from pathlib import Path

def create_unified_requirements():
    """创建统一的依赖版本"""
    print("🔧 Creating unified dependency versions...")
    
    # 定义统一的核心依赖版本
    core_deps = {
        'numpy': '1.24.3',  # 兼容性最好的版本
        'opencv-python-headless': '4.8.1.78',
        'Pillow': '10.0.0',
        'requests': '2.31.0',
        'pandas': '2.0.3',  # 稳定版本
        'scikit-learn': '1.3.0'
    }
    
    return core_deps

def update_panel_count_requirements():
    """更新panel_count依赖"""
    print("📦 Updating panel_count requirements...")
    
    requirements = """# Panel Count Service Dependencies
# 太阳能板计算服务依赖

# Core computation
opencv-python-headless==4.8.1.78
numpy==1.24.3
scipy==1.11.1
Pillow==10.0.0

# Web framework
flask==2.3.2
requests==2.31.0

# Optional: for enhanced functionality
matplotlib==3.7.2
"""
    
    with open('panel_count/requirements.txt', 'w') as f:
        f.write(requirements)
    
    print("  ✅ Updated panel_count/requirements.txt")

def update_roof_requirements():
    """更新roof服务依赖"""
    print("📦 Updating roof service requirements...")
    
    requirements = """# Roof Detection Service Dependencies
# 屋顶检测服务依赖

# Web framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# AI/ML
ultralytics==8.0.196
torch==2.0.1
torchvision==0.15.2

# Image processing
opencv-python-headless==4.8.1.78
Pillow==10.0.0
numpy==1.24.3

# Geometry
shapely==2.0.1
"""
    
    with open('roof/requirements.txt', 'w') as f:
        f.write(requirements)
    
    print("  ✅ Updated roof/requirements.txt")

def create_dev_requirements():
    """创建开发环境依赖"""
    print("📦 Creating development requirements...")
    
    dev_requirements = """# Development Dependencies
# 开发环境依赖

# Testing
pytest==7.4.0
pytest-cov==4.1.0
pytest-asyncio==0.21.1

# Code quality
black==23.7.0
flake8==6.0.0
isort==5.12.0

# Documentation
sphinx==7.1.2
sphinx-rtd-theme==1.3.0

# Development tools
jupyter==1.0.0
ipython==8.14.0

# API testing
httpx==0.24.1
"""
    
    with open('requirements-dev.txt', 'w') as f:
        f.write(dev_requirements)
    
    print("  ✅ Created requirements-dev.txt")

def create_docker_requirements():
    """为Docker创建精简的依赖文件"""
    print("🐳 Creating Docker-optimized requirements...")
    
    # Panel Count Docker requirements
    panel_docker_req = """opencv-python-headless==4.8.1.78
numpy==1.24.3
scipy==1.11.1
flask==2.3.2
requests==2.31.0
Pillow==10.0.0
"""
    
    with open('panel_count/requirements-docker.txt', 'w') as f:
        f.write(panel_docker_req)
    
    # Roof Detection Docker requirements
    roof_docker_req = """fastapi==0.104.1
uvicorn[standard]==0.24.0
ultralytics==8.0.196
opencv-python-headless==4.8.1.78
Pillow==10.0.0
numpy==1.24.3
python-multipart==0.0.6
shapely==2.0.1
"""
    
    with open('roof/requirements-docker.txt', 'w') as f:
        f.write(roof_docker_req)
    
    print("  ✅ Created Docker-optimized requirements")

def update_dockerfiles():
    """更新Dockerfile以使用新的依赖文件"""
    print("🐳 Updating Dockerfiles...")
    
    # 更新panel_count Dockerfile
    panel_dockerfile = Path('panel_count/Dockerfile.panel')
    if panel_dockerfile.exists():
        content = panel_dockerfile.read_text()
        if 'requirements-docker.txt' not in content:
            content = content.replace(
                'COPY requirements.txt .',
                'COPY requirements-docker.txt requirements.txt'
            )
            panel_dockerfile.write_text(content)
            print("  ✅ Updated panel_count Dockerfile")
    
    # 更新roof Dockerfile
    roof_dockerfile = Path('roof/Dockerfile')
    if roof_dockerfile.exists():
        content = roof_dockerfile.read_text()
        if 'requirements-docker.txt' not in content:
            content = content.replace(
                'COPY requirements.txt .',
                'COPY requirements-docker.txt requirements.txt'
            )
            roof_dockerfile.write_text(content)
            print("  ✅ Updated roof Dockerfile")

def create_dependency_check_script():
    """创建依赖检查脚本"""
    print("🔍 Creating dependency check script...")
    
    check_script = """#!/usr/bin/env python3
\"\"\"
Dependency Compatibility Check
依赖兼容性检查
\"\"\"
import subprocess
import sys

def check_dependencies():
    \"\"\"检查依赖兼容性\"\"\"
    print("🔍 Checking dependency compatibility...")
    
    try:
        # 检查pip-tools是否安装
        subprocess.run(['pip-compile', '--version'], 
                      capture_output=True, check=True)
        print("  ✅ pip-tools is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  ⚠️  pip-tools not found. Install with: pip install pip-tools")
        return False
    
    # 检查各服务的依赖
    services = ['panel_count', 'roof']
    
    for service in services:
        req_file = f"{service}/requirements.txt"
        try:
            result = subprocess.run([
                'pip-compile', '--dry-run', req_file
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✅ {service} dependencies are compatible")
            else:
                print(f"  ❌ {service} has dependency conflicts:")
                print(f"     {result.stderr}")
                
        except Exception as e:
            print(f"  ⚠️  Could not check {service}: {e}")
    
    return True

if __name__ == "__main__":
    check_dependencies()
"""
    
    with open('check_dependencies.py', 'w') as f:
        f.write(check_script)
    
    print("  ✅ Created dependency check script")

def create_install_script():
    """创建安装脚本"""
    print("📥 Creating installation script...")
    
    install_script = """#!/bin/bash
# Installation Script for IoT-AI Project
# IoT-AIプロジェクトのインストールスクリプト

echo "🚀 Installing IoT-AI Project Dependencies"
echo "========================================"

# 检查Python版本
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# 升级pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# 安装开发工具
echo "🔧 Installing development tools..."
pip install pip-tools wheel

# 安装各服务依赖
echo "📦 Installing panel_count dependencies..."
cd panel_count
pip install -r requirements.txt
cd ..

echo "📦 Installing roof detection dependencies..."
cd roof  
pip install -r requirements.txt
cd ..

# 安装开发依赖（可选）
if [ "$1" = "--dev" ]; then
    echo "🛠️  Installing development dependencies..."
    pip install -r requirements-dev.txt
fi

echo "✅ Installation completed!"
echo ""
echo "🚀 Quick Start:"
echo "  1. Start roof detection: cd roof && uvicorn app.main:app --port 8000"
echo "  2. Start panel calculation: cd panel_count && python api_integration.py"
echo "  3. Test: curl http://localhost:8001/health"
"""
    
    with open('install.sh', 'w') as f:
        f.write(install_script)
    
    # Windows版本
    install_bat = """@echo off
REM Installation Script for IoT-AI Project (Windows)
REM IoT-AIプロジェクトのインストールスクリプト (Windows)

echo 🚀 Installing IoT-AI Project Dependencies
echo ========================================

REM 升级pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM 安装开发工具
echo 🔧 Installing development tools...
pip install pip-tools wheel

REM 安装各服务依赖
echo 📦 Installing panel_count dependencies...
cd panel_count
pip install -r requirements.txt
cd ..

echo 📦 Installing roof detection dependencies...
cd roof
pip install -r requirements.txt
cd ..

REM 安装开发依赖（可选）
if "%1"=="--dev" (
    echo 🛠️  Installing development dependencies...
    pip install -r requirements-dev.txt
)

echo ✅ Installation completed!
echo.
echo 🚀 Quick Start:
echo   1. Start roof detection: cd roof ^&^& uvicorn app.main:app --port 8000
echo   2. Start panel calculation: cd panel_count ^&^& python api_integration.py
echo   3. Test: curl http://localhost:8001/health
"""
    
    with open('install.bat', 'w') as f:
        f.write(install_bat)
    
    print("  ✅ Created installation scripts (install.sh, install.bat)")

def main():
    """执行依赖修复"""
    print("🔧 Starting dependency fixes...")
    print("=" * 50)
    
    try:
        update_panel_count_requirements()
        update_roof_requirements()
        create_dev_requirements()
        create_docker_requirements()
        update_dockerfiles()
        create_dependency_check_script()
        create_install_script()
        
        print("\n" + "=" * 50)
        print("✅ Dependency fixes completed!")
        print("\n📋 Next Steps:")
        print("1. Run: python check_dependencies.py")
        print("2. Install dependencies: ./install.sh (or install.bat on Windows)")
        print("3. Test services individually")
        print("4. Run integration tests")
        
    except Exception as e:
        print(f"❌ Error during dependency fixes: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
