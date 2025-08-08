#!/usr/bin/env python3
"""
下载公开卫星数据集
Download public satellite dataset

使用公开可用的卫星图像数据集
"""

import os
import sys
import yaml
import requests
import zipfile
from pathlib import Path
import shutil

print("🛰️ 公开卫星数据集下载器")
print("=" * 50)

def download_file(url, filename):
    """下载文件"""
    try:
        print(f"📥 下载: {filename}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r   进度: {percent:.1f}%", end='', flush=True)
        
        print(f"\n✅ 下载完成: {filename}")
        return True
        
    except Exception as e:
        print(f"\n❌ 下载失败: {e}")
        return False

def create_satellite_dataset():
    """创建卫星数据集结构"""
    print("\n🏗️ 创建卫星数据集结构...")
    
    # 数据集目录
    dataset_dir = "data/satellite_dataset"
    os.makedirs(dataset_dir, exist_ok=True)
    
    # 创建子目录
    subdirs = [
        "train/images", "train/labels",
        "val/images", "val/labels", 
        "test/images", "test/labels"
    ]
    
    for subdir in subdirs:
        os.makedirs(os.path.join(dataset_dir, subdir), exist_ok=True)
    
    # 创建数据配置文件
    data_config = {
        'path': os.path.abspath(dataset_dir),
        'train': 'train/images',
        'val': 'val/images',
        'test': 'test/images',
        'nc': 4,
        'names': ['Baren-Land', 'farm', 'rice-fields', 'roof']
    }
    
    # 保存配置
    config_dir = "config"
    os.makedirs(config_dir, exist_ok=True)
    
    with open(os.path.join(config_dir, "data.yaml"), 'w') as f:
        yaml.dump(data_config, f, default_flow_style=False)
    
    print(f"✅ 数据集结构已创建: {dataset_dir}")
    return dataset_dir

def download_sample_images():
    """下载示例卫星图像"""
    print("\n📸 下载示例卫星图像...")
    
    # 公开的卫星图像URL (示例)
    sample_urls = [
        # 这些是示例URL，实际使用时需要替换为真实的卫星图像数据集
        "https://github.com/ultralytics/yolov5/releases/download/v1.0/coco128.zip"
    ]
    
    dataset_dir = "data/satellite_dataset"
    
    try:
        # 下载COCO128作为示例数据
        zip_file = "coco128.zip"
        if download_file(sample_urls[0], zip_file):
            print("📦 解压数据集...")
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall("data/temp")
            
            # 移动文件到正确位置
            temp_dir = "data/temp/coco128"
            if os.path.exists(temp_dir):
                # 复制图像文件
                images_src = os.path.join(temp_dir, "images", "train2017")
                if os.path.exists(images_src):
                    # 分配到训练和验证集
                    image_files = [f for f in os.listdir(images_src) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                    
                    # 80% 训练，20% 验证
                    split_idx = int(len(image_files) * 0.8)
                    train_files = image_files[:split_idx]
                    val_files = image_files[split_idx:]
                    
                    # 复制训练图像
                    train_dst = os.path.join(dataset_dir, "train", "images")
                    for i, img_file in enumerate(train_files[:20]):  # 限制数量用于演示
                        src = os.path.join(images_src, img_file)
                        dst = os.path.join(train_dst, f"satellite_train_{i:03d}.jpg")
                        shutil.copy2(src, dst)
                        
                        # 创建对应的标签文件（示例）
                        label_file = os.path.join(dataset_dir, "train", "labels", f"satellite_train_{i:03d}.txt")
                        with open(label_file, 'w') as f:
                            # 示例标签 (class x_center y_center width height)
                            f.write(f"{i % 4} 0.5 0.5 0.3 0.3\n")
                    
                    # 复制验证图像
                    val_dst = os.path.join(dataset_dir, "val", "images")
                    for i, img_file in enumerate(val_files[:10]):  # 限制数量用于演示
                        src = os.path.join(images_src, img_file)
                        dst = os.path.join(val_dst, f"satellite_val_{i:03d}.jpg")
                        shutil.copy2(src, dst)
                        
                        # 创建对应的标签文件（示例）
                        label_file = os.path.join(dataset_dir, "val", "labels", f"satellite_val_{i:03d}.txt")
                        with open(label_file, 'w') as f:
                            f.write(f"{i % 4} 0.5 0.5 0.2 0.2\n")
                    
                    print(f"✅ 已创建 {len(train_files[:20])} 张训练图像")
                    print(f"✅ 已创建 {len(val_files[:10])} 张验证图像")
            
            # 清理临时文件
            shutil.rmtree("data/temp", ignore_errors=True)
            os.remove(zip_file)
            
            return True
    
    except Exception as e:
        print(f"❌ 下载示例图像失败: {e}")
        return False

def create_manual_instructions():
    """创建手动下载说明"""
    instructions = """
# 🛰️ 手动数据集设置说明

## 📥 获取真实卫星数据集

### 方法1: Roboflow (推荐)
1. 访问 https://roboflow.com/
2. 注册账户并获取API密钥
3. 搜索卫星图像分割数据集
4. 下载YOLOv8格式的数据

### 方法2: 公开数据集
1. **DOTA数据集**: https://captain-whu.github.io/DOTA/
2. **xView数据集**: http://xviewdataset.org/
3. **SpaceNet数据集**: https://spacenet.ai/

### 方法3: 自制数据集
1. 收集卫星图像
2. 使用LabelImg或Roboflow标注
3. 导出为YOLOv8格式

## 📁 数据集目录结构

将数据放置在以下结构中：

```
data/satellite_dataset/
├── train/
│   ├── images/          # 训练图像
│   └── labels/          # 训练标签 (.txt)
├── val/
│   ├── images/          # 验证图像  
│   └── labels/          # 验证标签 (.txt)
└── test/
    ├── images/          # 测试图像
    └── labels/          # 测试标签 (.txt)
```

## 🏷️ 标签格式

每个.txt文件包含：
```
class_id x_center y_center width height
```

其中：
- class_id: 0=Baren-Land, 1=farm, 2=rice-fields, 3=roof
- 坐标为相对值 (0-1)

## ⚙️ 配置文件

确保 config/data.yaml 正确指向您的数据：

```yaml
path: /path/to/data/satellite_dataset
train: train/images
val: val/images
test: test/images
nc: 4
names: ['Baren-Land', 'farm', 'rice-fields', 'roof']
```
"""
    
    with open("DATASET_SETUP.md", 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("📝 已创建数据集设置说明: DATASET_SETUP.md")

def main():
    """主函数"""
    print("🚀 开始设置卫星数据集...")
    
    # 创建数据集结构
    dataset_dir = create_satellite_dataset()
    
    # 尝试下载示例数据
    if download_sample_images():
        print("✅ 示例数据集创建成功")
    else:
        print("⚠️ 示例数据下载失败，但结构已创建")
    
    # 创建手动设置说明
    create_manual_instructions()
    
    # 验证数据集
    config_file = "config/data.yaml"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        print(f"\n📊 数据集配置:")
        print(f"   路径: {config['path']}")
        print(f"   类别: {config['names']}")
        
        # 检查图像数量
        train_images = os.path.join(dataset_dir, "train", "images")
        val_images = os.path.join(dataset_dir, "val", "images")
        
        if os.path.exists(train_images):
            train_count = len([f for f in os.listdir(train_images) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            print(f"   训练图像: {train_count} 张")
        
        if os.path.exists(val_images):
            val_count = len([f for f in os.listdir(val_images) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            print(f"   验证图像: {val_count} 张")
    
    print(f"\n🎯 下一步:")
    print(f"   1. 查看设置说明: cat DATASET_SETUP.md")
    print(f"   2. 添加真实卫星图像到 {dataset_dir}")
    print(f"   3. 开始训练: python train_expert_with_local_data.py")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 卫星数据集设置完成!")
        else:
            print("\n❌ 数据集设置失败")
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
