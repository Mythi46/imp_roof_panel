#!/usr/bin/env python3
"""
Generate 50 images visualization results
生成50组图像可视化结果
"""

import os
import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path
import random
from ultralytics import YOLO
import yaml
from PIL import Image
import json
from datetime import datetime

# 设置matplotlib使用英文显示，避免乱码问题
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False
print("✅ Set charts to use English display")

def find_test_images_extended(data_yaml_path, num_images=50):
    """从数据集中选取50张测试图片"""
    print("🔍 Finding 50 test images...")
    
    try:
        with open(data_yaml_path, 'r') as f:
            data_config = yaml.safe_load(f)

        # 获取数据集根目录
        dataset_root = Path(data_yaml_path).parent

        # 尝试多个可能的图片目录
        possible_dirs = []
        for key in ['test', 'val', 'train']:
            if key in data_config:
                rel_path = data_config[key]
                if rel_path.startswith('../'):
                    # 处理相对路径
                    abs_path = dataset_root / rel_path
                else:
                    abs_path = Path(rel_path)
                possible_dirs.append(abs_path)
        
        all_images = []

        for img_dir in possible_dirs:
            if img_dir and img_dir.exists():
                print(f"   📁 Checking directory: {img_dir}")
                image_files = [f for f in img_dir.iterdir()
                             if f.suffix.lower() in ['.jpg', '.jpeg', '.png']]
                all_images.extend(image_files)
                print(f"   ✅ Found {len(image_files)} images in {img_dir}")
        
        # 如果图片不够50张，重复使用
        if len(all_images) < num_images:
            print(f"⚠️ Only found {len(all_images)} images, will repeat some images")
            # 重复图片列表直到达到50张
            multiplier = (num_images // len(all_images)) + 1
            all_images = (all_images * multiplier)[:num_images]
        else:
            # 随机选择50张
            all_images = random.sample(all_images, num_images)
        
        print(f"✅ Selected {len(all_images)} images for processing")
        return all_images
        
    except Exception as e:
        print(f"❌ Error finding images: {e}")
        return []

def load_best_model():
    """加载最佳训练模型"""
    print("🔧 Loading best model...")
    
    # 可能的模型路径
    model_paths = [
        "runs/segment/improved_training_compatible/weights/best.pt",
        "runs/segment/continue_training_optimized/weights/best.pt",
        "results/roof_detection_training/weights/best.pt",
        "models/trained/best.pt",
        "best.pt",
        "yolov8l-seg.pt"  # 预训练模型作为后备
    ]
    
    for model_path in model_paths:
        if os.path.exists(model_path):
            print(f"✅ Loading model: {model_path}")
            model = YOLO(model_path)
            return model, model_path
    
    print("❌ No trained model found")
    return None, None

def predict_and_visualize_batch(model, image_paths, output_dir, batch_size=10):
    """批量处理图片以提高效率"""
    print(f"🚀 Processing {len(image_paths)} images in batches of {batch_size}...")
    
    results_data = []
    
    for i in range(0, len(image_paths), batch_size):
        batch_paths = image_paths[i:i+batch_size]
        batch_end = min(i+batch_size, len(image_paths))
        
        print(f"📦 Processing batch {i//batch_size + 1}: images {i+1}-{batch_end}")
        
        for j, image_path in enumerate(batch_paths):
            global_index = i + j
            print(f"   🔍 Processing image {global_index+1}/50: {image_path.name}")
            
            try:
                # 预测
                results = model.predict(
                    source=str(image_path),
                    save=False,
                    conf=0.25,
                    iou=0.7,
                    verbose=False
                )
                
                # 加载原图
                image = cv2.imread(str(image_path))
                if image is None:
                    print(f"   ❌ Failed to load image: {image_path}")
                    continue
                    
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                # 创建可视化
                fig, axes = plt.subplots(1, 2, figsize=(16, 8))
                
                # 原图
                axes[0].imshow(image_rgb)
                axes[0].set_title(f'Original Image {global_index+1}: {image_path.name}', 
                                fontsize=14, fontweight='bold')
                axes[0].axis('off')
                
                # 检测结果
                annotated_image = image_rgb.copy()
                
                # 处理检测结果
                detections = []
                if results and len(results) > 0:
                    result = results[0]
                    
                    if hasattr(result, 'boxes') and result.boxes is not None:
                        boxes = result.boxes.xyxy.cpu().numpy()
                        confidences = result.boxes.conf.cpu().numpy()
                        classes = result.boxes.cls.cpu().numpy()
                        
                        class_names = ['Baren-Land', 'farm', 'rice-fields', 'roof']
                        colors = [(139, 69, 19), (34, 139, 34), (65, 105, 225), (220, 20, 60)]
                        
                        for box, conf, cls in zip(boxes, confidences, classes):
                            x1, y1, x2, y2 = box.astype(int)
                            class_name = class_names[int(cls)] if int(cls) < len(class_names) else f"Class_{int(cls)}"
                            color = colors[int(cls)] if int(cls) < len(colors) else (255, 255, 255)
                            
                            # 绘制边界框
                            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), color, 2)
                            
                            # 绘制标签
                            label = f'{class_name}: {conf:.2f}'
                            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                            cv2.rectangle(annotated_image, (x1, y1-label_size[1]-10), 
                                        (x1+label_size[0], y1), color, -1)
                            cv2.putText(annotated_image, label, (x1, y1-5), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                            
                            # 记录检测结果
                            detections.append({
                                'class': class_name,
                                'confidence': float(conf),
                                'bbox': [int(x1), int(y1), int(x2), int(y2)]
                            })
                
                # 显示检测结果
                axes[1].imshow(annotated_image)
                
                # 生成标题
                num_detections = len(detections)
                if num_detections > 0:
                    class_counts = {}
                    for detection in detections:
                        class_name = detection['class']
                        if class_name not in class_counts:
                            class_counts[class_name] = 0
                        class_counts[class_name] += 1
                    
                    title_parts = [f'Detection Results ({num_detections} objects)']
                    for class_name, count in class_counts.items():
                        title_parts.append(f'{class_name}: {count}')
                    
                    title = '\n'.join(title_parts)
                else:
                    title = 'Detection Results (No objects detected)'
                
                axes[1].set_title(title, fontsize=14, fontweight='bold')
                axes[1].axis('off')
                
                # 保存结果
                result_filename = f"result_{global_index+1:02d}_{image_path.stem}.png"
                result_path = output_dir / result_filename
                plt.savefig(result_path, dpi=150, bbox_inches='tight')
                plt.close()
                
                # 保存纯检测结果图
                detection_filename = f"detection_{global_index+1:02d}_{image_path.stem}.jpg"
                detection_path = output_dir / detection_filename
                cv2.imwrite(str(detection_path), cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
                
                # 记录结果数据
                result_data = {
                    'image_index': global_index + 1,
                    'image_name': image_path.name,
                    'image_path': str(image_path),
                    'result_image': result_filename,
                    'detection_image': detection_filename,
                    'num_detections': num_detections,
                    'detections': detections
                }
                
                results_data.append(result_data)
                print(f"   ✅ Detected {num_detections} objects")
                
            except Exception as e:
                print(f"   ❌ Processing failed: {e}")
                continue
    
    return results_data

def create_extended_summary(results_data, output_dir):
    """创建50张图片的总览"""
    print("📊 Creating extended summary for 50 images...")
    
    # 统计数据
    total_images = len(results_data)
    total_detections = sum(r['num_detections'] for r in results_data)
    
    # 类别统计
    class_counts = {}
    confidence_scores = []
    
    for result in results_data:
        for detection in result['detections']:
            class_name = detection['class']
            if class_name not in class_counts:
                class_counts[class_name] = 0
            class_counts[class_name] += 1
            confidence_scores.append(detection['confidence'])
    
    # 创建总览图
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. 类别分布饼图
    if class_counts:
        colors = ['#DC143C', '#4169E1', '#8B4513', '#228B22']
        wedges, texts, autotexts = axes[0, 0].pie(
            class_counts.values(), 
            labels=class_counts.keys(), 
            colors=colors[:len(class_counts)],
            autopct='%1.1f%%', 
            startangle=90
        )
        axes[0, 0].set_title('Detection Distribution by Class', fontsize=14, fontweight='bold')
    
    # 2. 类别检测数量柱状图
    if class_counts:
        bars = axes[0, 1].bar(class_counts.keys(), class_counts.values(), 
                            color=colors[:len(class_counts)], alpha=0.8)
        axes[0, 1].set_title('Detection Count by Class', fontsize=14, fontweight='bold')
        axes[0, 1].set_xlabel('Object Classes', fontsize=12)
        axes[0, 1].set_ylabel('Number of Detections', fontsize=12)
        axes[0, 1].grid(True, alpha=0.3)
        
        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            axes[0, 1].text(bar.get_x() + bar.get_width()/2., height + 1,
                           f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    # 3. 每张图片检测数量分布
    detection_counts = [r['num_detections'] for r in results_data]
    axes[1, 0].hist(detection_counts, bins=20, color='skyblue', alpha=0.7, edgecolor='black')
    axes[1, 0].set_title('Objects per Image Distribution', fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel('Number of Objects per Image', fontsize=12)
    axes[1, 0].set_ylabel('Frequency', fontsize=12)
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. 统计信息文本
    axes[1, 1].axis('off')
    
    stats_text = f"""Detection Results Summary (50 Images)

Total Images: {total_images}
Total Detections: {total_detections}
Average per Image: {total_detections/total_images:.1f} objects

Class Statistics:
"""
    
    for class_name, count in class_counts.items():
        percentage = (count / total_detections) * 100 if total_detections > 0 else 0
        stats_text += f"   {class_name}: {count} ({percentage:.1f}%)\n"
    
    if confidence_scores:
        stats_text += f"""
Confidence Statistics:
   Average: {np.mean(confidence_scores):.3f}
   Maximum: {np.max(confidence_scores):.3f}
   Minimum: {np.min(confidence_scores):.3f}
"""
    
    axes[1, 1].text(0.1, 0.9, stats_text, transform=axes[1, 1].transAxes,
                    fontsize=12, verticalalignment='top',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.5))
    
    # 设置总标题
    plt.suptitle('🏠 Roof Detection Results Overview - 50 Images Analysis', 
                 fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # 保存图片
    summary_path = output_dir / "detection_summary_50_images.png"
    plt.savefig(summary_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Extended summary saved: {summary_path}")
    return summary_path

def main():
    """主函数"""
    print("🎨 Roof Detection Visualization - 50 Images Extended")
    print("=" * 60)
    
    # 设置路径
    # 直接使用训练图片目录
    train_images_dir = Path("data/raw/new-2-1/train/images")
    output_dir = Path("visualization_results_50")
    output_dir.mkdir(exist_ok=True)
    
    if not train_images_dir.exists():
        print(f"❌ Training images directory not found: {train_images_dir}")
        return

    # 加载模型
    model, model_path = load_best_model()
    if model is None:
        return

    # 直接从训练图片目录选择50张图片
    all_images = list(train_images_dir.glob("*.jpg"))
    if len(all_images) < 50:
        print(f"⚠️ Only found {len(all_images)} images, using all available")
        test_images = all_images
    else:
        import random
        random.seed(42)  # 确保可重复性
        test_images = random.sample(all_images, 50)

    if not test_images:
        print("❌ No images found")
        return
    
    print(f"\n🚀 Processing {len(test_images)} images...")
    
    # 批量处理图片
    results_data = predict_and_visualize_batch(model, test_images, output_dir)
    
    # 创建总览
    if results_data:
        summary_path = create_extended_summary(results_data, output_dir)
        
        # 保存详细结果
        results_json = {
            'model_path': model_path,
            'timestamp': datetime.now().isoformat(),
            'total_images': len(results_data),
            'total_detections': sum(r['num_detections'] for r in results_data),
            'results': results_data
        }
        
        json_path = output_dir / "detection_results_50.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results_json, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎉 50 Images Visualization completed!")
        print(f"📁 Results saved in: {output_dir}")
        print(f"📊 Summary chart: {summary_path}")
        print(f"📋 Detailed results: {json_path}")
        print(f"🖼️ Processed images: {len(results_data)}/50")
        print(f"🎯 Total detections: {sum(r['num_detections'] for r in results_data)}")
        
        # 显示类别统计
        class_counts = {}
        for result in results_data:
            for detection in result['detections']:
                class_name = detection['class']
                if class_name not in class_counts:
                    class_counts[class_name] = 0
                class_counts[class_name] += 1
        
        print(f"\n📋 Class Detection Statistics:")
        for class_name, count in class_counts.items():
            print(f"   {class_name}: {count}")
    
    else:
        print("❌ No images processed successfully")

if __name__ == "__main__":
    main()
