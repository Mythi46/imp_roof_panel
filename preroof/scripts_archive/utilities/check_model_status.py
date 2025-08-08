#!/usr/bin/env python3
"""
全面检查模型状态和可用资源
Comprehensive model status and resource check
"""

import os
import sys
import yaml
from pathlib import Path
import json
from datetime import datetime

def check_project_structure():
    """检查项目结构"""
    print("🔍 Checking Project Structure")
    print("=" * 50)
    
    # 关键目录检查
    key_dirs = [
        "data/raw/new-2-1",
        "runs/segment",
        "models",
        "visualization_results",
        "src"
    ]
    
    for dir_path in key_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path} - EXISTS")
            # 显示子目录
            try:
                subdirs = [d for d in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, d))]
                if subdirs:
                    print(f"   📁 Subdirectories: {', '.join(subdirs[:5])}")
            except:
                pass
        else:
            print(f"❌ {dir_path} - MISSING")
    
    print()

def check_trained_models():
    """检查训练好的模型"""
    print("🤖 Checking Trained Models")
    print("=" * 50)
    
    # 可能的模型位置
    model_locations = [
        "runs/segment/improved_training_compatible/weights/best.pt",
        "runs/segment/continue_training_optimized/weights/best.pt",
        "runs/segment/*/weights/best.pt",
        "models/trained/best.pt",
        "best.pt"
    ]
    
    found_models = []
    
    for location in model_locations:
        if '*' in location:
            # 处理通配符路径
            base_path = location.split('*')[0]
            if os.path.exists(base_path):
                try:
                    for subdir in os.listdir(base_path):
                        full_path = os.path.join(base_path, subdir, "weights", "best.pt")
                        if os.path.exists(full_path):
                            found_models.append(full_path)
                except:
                    pass
        else:
            if os.path.exists(location):
                found_models.append(location)
    
    if found_models:
        print(f"✅ Found {len(found_models)} trained models:")
        for i, model in enumerate(found_models, 1):
            file_size = os.path.getsize(model) / (1024*1024)  # MB
            mod_time = datetime.fromtimestamp(os.path.getmtime(model))
            print(f"   {i}. {model}")
            print(f"      Size: {file_size:.1f} MB")
            print(f"      Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("❌ No trained models found")
    
    print()
    return found_models

def check_dataset():
    """检查数据集"""
    print("📊 Checking Dataset")
    print("=" * 50)
    
    data_yaml_path = "data/raw/new-2-1/data.yaml"
    
    if not os.path.exists(data_yaml_path):
        print(f"❌ Dataset config not found: {data_yaml_path}")
        return None
    
    print(f"✅ Dataset config found: {data_yaml_path}")
    
    try:
        with open(data_yaml_path, 'r') as f:
            data_config = yaml.safe_load(f)
        
        print(f"📋 Classes: {data_config.get('nc', 'Unknown')} classes")
        print(f"   Names: {data_config.get('names', [])}")
        
        # 检查图片目录
        dataset_root = Path(data_yaml_path).parent
        
        for split in ['train', 'val', 'test']:
            if split in data_config:
                rel_path = data_config[split]
                if rel_path.startswith('../'):
                    abs_path = dataset_root / rel_path
                else:
                    abs_path = Path(rel_path)
                
                if abs_path.exists():
                    try:
                        image_files = [f for f in abs_path.iterdir() 
                                     if f.suffix.lower() in ['.jpg', '.jpeg', '.png']]
                        print(f"   ✅ {split}: {len(image_files)} images in {abs_path}")
                    except Exception as e:
                        print(f"   ❌ {split}: Error reading {abs_path} - {e}")
                else:
                    print(f"   ❌ {split}: Directory not found - {abs_path}")
        
        return data_config
        
    except Exception as e:
        print(f"❌ Error reading dataset config: {e}")
        return None
    
    print()

def check_visualization_results():
    """检查可视化结果"""
    print("🎨 Checking Visualization Results")
    print("=" * 50)
    
    viz_dirs = [
        "visualization_results",
        "visualization_results_50"
    ]
    
    for viz_dir in viz_dirs:
        if os.path.exists(viz_dir):
            try:
                files = os.listdir(viz_dir)
                png_files = [f for f in files if f.endswith('.png')]
                jpg_files = [f for f in files if f.endswith('.jpg')]
                html_files = [f for f in files if f.endswith('.html')]
                json_files = [f for f in files if f.endswith('.json')]
                
                print(f"✅ {viz_dir}:")
                print(f"   📊 PNG charts: {len(png_files)}")
                print(f"   🖼️ JPG images: {len(jpg_files)}")
                print(f"   🌐 HTML files: {len(html_files)}")
                print(f"   📋 JSON files: {len(json_files)}")
                
                # 显示一些关键文件
                key_files = ['index.html', 'detection_summary.png', 'detection_results.json']
                for key_file in key_files:
                    if key_file in files:
                        print(f"   ✅ {key_file}")
                    else:
                        print(f"   ❌ {key_file} missing")
                        
            except Exception as e:
                print(f"❌ Error reading {viz_dir}: {e}")
        else:
            print(f"❌ {viz_dir} not found")
    
    print()

def check_dependencies():
    """检查依赖库"""
    print("📦 Checking Dependencies")
    print("=" * 50)
    
    required_packages = [
        'ultralytics',
        'opencv-python',
        'matplotlib',
        'numpy',
        'pillow',
        'yaml',
        'torch'
    ]
    
    for package in required_packages:
        try:
            if package == 'opencv-python':
                import cv2
                version = cv2.__version__
            elif package == 'yaml':
                import yaml
                version = getattr(yaml, '__version__', 'Unknown')
            else:
                module = __import__(package)
                version = getattr(module, '__version__', 'Unknown')
            
            print(f"✅ {package}: {version}")
            
        except ImportError:
            print(f"❌ {package}: NOT INSTALLED")
        except Exception as e:
            print(f"⚠️ {package}: Error - {e}")
    
    print()

def check_training_results():
    """检查训练结果"""
    print("📈 Checking Training Results")
    print("=" * 50)
    
    training_dirs = []
    
    # 查找训练结果目录
    if os.path.exists("runs/segment"):
        for subdir in os.listdir("runs/segment"):
            full_path = os.path.join("runs/segment", subdir)
            if os.path.isdir(full_path):
                training_dirs.append(full_path)
    
    if training_dirs:
        print(f"✅ Found {len(training_dirs)} training runs:")
        
        for train_dir in training_dirs:
            print(f"\n📁 {train_dir}:")
            
            # 检查关键文件
            key_files = {
                'results.csv': '训练结果',
                'args.yaml': '训练参数',
                'weights/best.pt': '最佳模型',
                'weights/last.pt': '最后模型'
            }
            
            for file_path, description in key_files.items():
                full_file_path = os.path.join(train_dir, file_path)
                if os.path.exists(full_file_path):
                    if file_path.endswith('.pt'):
                        size_mb = os.path.getsize(full_file_path) / (1024*1024)
                        print(f"   ✅ {description}: {size_mb:.1f} MB")
                    else:
                        print(f"   ✅ {description}")
                else:
                    print(f"   ❌ {description} missing")
            
            # 读取训练结果
            results_csv = os.path.join(train_dir, 'results.csv')
            if os.path.exists(results_csv):
                try:
                    import pandas as pd
                    df = pd.read_csv(results_csv)
                    if len(df) > 0:
                        last_row = df.iloc[-1]
                        print(f"   📊 Final epoch: {len(df)}")
                        if 'metrics/mAP50(B)' in df.columns:
                            print(f"   🎯 Final mAP@0.5: {last_row['metrics/mAP50(B)']:.3f}")
                        if 'metrics/mAP50-95(B)' in df.columns:
                            print(f"   🎯 Final mAP@0.5:0.95: {last_row['metrics/mAP50-95(B)']:.3f}")
                except Exception as e:
                    print(f"   ⚠️ Error reading results: {e}")
    else:
        print("❌ No training results found")
    
    print()

def generate_status_report():
    """生成状态报告"""
    print("📋 Generating Status Report")
    print("=" * 50)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'project_status': 'checking...',
        'summary': {}
    }
    
    # 检查各个组件
    models = check_trained_models()
    dataset = check_dataset()
    
    # 生成总结
    report['summary'] = {
        'trained_models': len(models) if models else 0,
        'dataset_available': dataset is not None,
        'visualization_exists': os.path.exists('visualization_results'),
        'ready_for_50_images': len(models) > 0 and dataset is not None
    }
    
    if report['summary']['ready_for_50_images']:
        report['project_status'] = 'READY'
        print("🎉 Project Status: READY for 50 images visualization")
        print("💡 Recommended next steps:")
        print("   1. Run 50 images visualization")
        print("   2. Generate extended analysis")
        print("   3. Create comprehensive report")
    else:
        report['project_status'] = 'NOT_READY'
        print("⚠️ Project Status: NOT READY")
        print("🔧 Required actions:")
        if not models:
            print("   - Train or locate model files")
        if not dataset:
            print("   - Fix dataset configuration")
    
    # 保存报告
    with open('project_status_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Status report saved: project_status_report.json")

def main():
    """主函数"""
    print("🔍 Comprehensive Model and Project Status Check")
    print("=" * 60)
    print(f"📅 Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 执行各项检查
    check_project_structure()
    check_dependencies()
    models = check_trained_models()
    dataset = check_dataset()
    check_training_results()
    check_visualization_results()
    generate_status_report()
    
    print("🏁 Status check completed!")

if __name__ == "__main__":
    main()
