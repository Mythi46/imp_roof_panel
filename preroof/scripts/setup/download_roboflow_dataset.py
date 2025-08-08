#!/usr/bin/env python3
"""
使用Roboflow API下载卫星图像分割数据集
Download satellite image segmentation dataset using Roboflow API
"""

import os
import sys
import shutil
from pathlib import Path

print("🛰️ Roboflow数据集下载")
print("Roboflow Dataset Download")
print("=" * 40)

def install_roboflow():
    """安装roboflow库"""
    print("📦 检查并安装roboflow库...")
    
    try:
        import roboflow
        print("✅ roboflow库已安装")
        return True
    except ImportError:
        print("📥 安装roboflow库...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "roboflow"])
            print("✅ roboflow库安装成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ roboflow库安装失败: {e}")
            return False

def download_dataset():
    """下载数据集"""
    print("📥 下载数据集...")
    
    try:
        from roboflow import Roboflow
        
        # 使用您提供的API密钥和项目信息
        api_key = "EkXslogyvSMHiOP3MK94"
        workspace = "a-imc4u"
        project_name = "new-2-6zp4h"
        version_number = 1
        
        print(f"🔑 API密钥: {api_key[:10]}...")
        print(f"📁 工作空间: {workspace}")
        print(f"📊 项目: {project_name}")
        print(f"🔢 版本: {version_number}")
        
        # 初始化Roboflow
        rf = Roboflow(api_key=api_key)
        project = rf.workspace(workspace).project(project_name)
        version = project.version(version_number)
        
        # 下载YOLOv8格式数据集
        print("⬇️ 开始下载...")
        dataset = version.download("yolov8")
        
        print(f"✅ 数据集下载完成!")
        print(f"📁 下载位置: {dataset.location}")
        
        return dataset.location
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def organize_dataset(download_path):
    """整理数据集到标准位置"""
    if not download_path or not os.path.exists(download_path):
        print("❌ 下载路径无效")
        return False
    
    print("📁 整理数据集...")
    
    # 目标位置
    target_path = "data/raw/new-2-1"
    
    # 创建目标目录
    os.makedirs(target_path, exist_ok=True)
    
    try:
        # 如果下载路径不是目标路径，则移动文件
        if os.path.abspath(download_path) != os.path.abspath(target_path):
            print(f"📦 移动数据集: {download_path} → {target_path}")
            
            # 复制所有文件
            for item in os.listdir(download_path):
                source = os.path.join(download_path, item)
                dest = os.path.join(target_path, item)
                
                if os.path.isdir(source):
                    if os.path.exists(dest):
                        shutil.rmtree(dest)
                    shutil.copytree(source, dest)
                    print(f"📁 复制目录: {item}")
                else:
                    shutil.copy2(source, dest)
                    print(f"📄 复制文件: {item}")
        
        print(f"✅ 数据集已整理到: {target_path}")
        return target_path
        
    except Exception as e:
        print(f"❌ 整理失败: {e}")
        return False

def verify_dataset(dataset_path):
    """验证数据集完整性"""
    print("🔍 验证数据集...")
    
    if not os.path.exists(dataset_path):
        print(f"❌ 数据集路径不存在: {dataset_path}")
        return False
    
    # 检查必要的文件和目录
    required_items = [
        "data.yaml",
        "train",
        "val"
    ]
    
    missing_items = []
    for item in required_items:
        item_path = os.path.join(dataset_path, item)
        if not os.path.exists(item_path):
            missing_items.append(item)
        else:
            print(f"✅ 找到: {item}")
    
    if missing_items:
        print(f"❌ 缺失项目: {missing_items}")
        return False
    
    # 检查data.yaml内容
    try:
        import yaml
        yaml_path = os.path.join(dataset_path, "data.yaml")
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print(f"📊 数据集配置:")
        print(f"   类别数: {config.get('nc', 'N/A')}")
        print(f"   类别名: {config.get('names', 'N/A')}")
        print(f"   训练集: {config.get('train', 'N/A')}")
        print(f"   验证集: {config.get('val', 'N/A')}")
        
        # 检查图像和标签数量
        train_images_path = os.path.join(dataset_path, "train", "images")
        train_labels_path = os.path.join(dataset_path, "train", "labels")
        
        if os.path.exists(train_images_path) and os.path.exists(train_labels_path):
            train_images = len([f for f in os.listdir(train_images_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            train_labels = len([f for f in os.listdir(train_labels_path) if f.endswith('.txt')])
            
            print(f"📊 训练集统计:")
            print(f"   图像数量: {train_images}")
            print(f"   标签数量: {train_labels}")
            
            if train_images == train_labels and train_images > 0:
                print("✅ 训练集图像和标签数量匹配")
            else:
                print("⚠️ 训练集图像和标签数量不匹配")
        
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def update_training_script(dataset_path):
    """更新训练脚本中的数据集路径"""
    print("🔧 更新训练脚本...")
    
    training_script = "train_expert_correct_solution.py"
    if not os.path.exists(training_script):
        print(f"⚠️ 训练脚本不存在: {training_script}")
        return
    
    try:
        # 读取训练脚本
        with open(training_script, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新数据集路径
        yaml_path = os.path.join(dataset_path, "data.yaml").replace("\\", "/")
        
        # 查找并替换data参数
        import re
        pattern = r"data\s*=\s*['\"][^'\"]*['\"]"
        replacement = f"data='{yaml_path}'"
        
        if re.search(pattern, content):
            new_content = re.sub(pattern, replacement, content)
            
            with open(training_script, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ 已更新训练脚本数据集路径: {yaml_path}")
        else:
            print("⚠️ 未找到data参数，请手动更新")
            
    except Exception as e:
        print(f"❌ 更新训练脚本失败: {e}")

def main():
    """主函数"""
    print("🚀 开始下载数据集...")
    
    # 1. 安装roboflow库
    if not install_roboflow():
        print("❌ 无法安装roboflow库，请手动安装: pip install roboflow")
        return False
    
    # 2. 下载数据集
    download_path = download_dataset()
    if not download_path:
        print("❌ 数据集下载失败")
        return False
    
    # 3. 整理数据集
    organized_path = organize_dataset(download_path)
    if not organized_path:
        print("❌ 数据集整理失败")
        return False
    
    # 4. 验证数据集
    if not verify_dataset(organized_path):
        print("❌ 数据集验证失败")
        return False
    
    # 5. 更新训练脚本
    update_training_script(organized_path)
    
    print(f"\n🎉 数据集下载和配置完成!")
    print(f"📁 数据集位置: {organized_path}")
    print(f"📋 下一步:")
    print(f"   1. 检查数据集: ls {organized_path}")
    print(f"   2. 运行训练: python train_expert_correct_solution.py")
    print(f"   3. 查看结果: 训练完成后检查results目录")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n✅ 所有步骤完成!")
    else:
        print(f"\n❌ 部分步骤失败，请检查错误信息")
        
    print(f"\n📞 如需帮助:")
    print(f"   - 检查网络连接")
    print(f"   - 验证API密钥有效性")
    print(f"   - 确认项目访问权限")
    print(f"   - 查看Roboflow项目页面")
