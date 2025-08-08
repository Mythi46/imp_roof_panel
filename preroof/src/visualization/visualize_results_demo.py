#!/usr/bin/env python3
"""
可视化结果演示脚本
Visualization Results Demo Script

选取20组图片进行推理并生成可视化结果
"""

import os
import random
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import json
from datetime import datetime

# 设置matplotlib使用英文显示，避免乱码问题
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

def find_test_images(data_yaml_path, num_images=50):
    """Select test images from dataset"""

    print("🔍 Finding test images...")

    # 读取数据集配置
    import yaml
    with open(data_yaml_path) as f:
        config = yaml.safe_load(f)

    # 获取数据集根目录
    dataset_root = Path(data_yaml_path).parent

    # 查找验证集图片
    val_images_dir = dataset_root / "val" / "images"
    train_images_dir = dataset_root / "train" / "images"

    # 收集所有图片
    image_files = []

    # 优先使用验证集
    if val_images_dir.exists():
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
            image_files.extend(list(val_images_dir.glob(ext)))
            image_files.extend(list(val_images_dir.glob(ext.upper())))

    # 如果验证集图片不够，从训练集补充
    if len(image_files) < num_images and train_images_dir.exists():
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
            train_files = list(train_images_dir.glob(ext))
            train_files.extend(list(train_images_dir.glob(ext.upper())))
            image_files.extend(train_files)

    if len(image_files) == 0:
        print("❌ 未找到图片文件")
        return []

    # 随机选择指定数量的图片
    selected_images = random.sample(image_files, min(num_images, len(image_files)))

    print(f"✅ Found {len(image_files)} images, selected {len(selected_images)}")

    return selected_images

def load_best_model():
    """Load best trained model"""

    print("🔧 Loading best model...")

    # 尝试加载继续训练的最佳模型
    model_paths = [
        "runs/segment/continue_training_optimized/weights/best.pt",
        "runs/segment/improved_training_compatible/weights/best.pt",
        "models/pretrained/yolov8l-seg.pt"
    ]

    for model_path in model_paths:
        if os.path.exists(model_path):
            print(f"✅ Loading model: {model_path}")
            model = YOLO(model_path)
            return model, model_path

    print("❌ No trained model found")
    return None, None

def predict_and_visualize(model, image_path, output_dir, image_index):
    """对单张图片进行推理并可视化"""

    # 执行推理
    results = model.predict(
        source=str(image_path),
        conf=0.35,
        iou=0.6,
        imgsz=896,
        save=False,
        verbose=False
    )[0]

    # 读取原图
    image = cv2.imread(str(image_path))
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # 生成可视化结果
    annotated_image = results.plot()
    annotated_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)

    # 创建对比图
    fig, axes = plt.subplots(1, 2, figsize=(20, 10))

    # Original Image
    axes[0].imshow(image_rgb)
    axes[0].set_title(f'Original {image_index+1}: {image_path.name}', fontsize=14, fontweight='bold')
    axes[0].axis('off')

    # Detection Results
    axes[1].imshow(annotated_rgb)

    # 统计检测结果
    num_detections = len(results.boxes) if results.boxes else 0
    detection_info = []

    if results.boxes:
        class_counts = {}
        for box in results.boxes:
            class_id = int(box.cls[0])
            class_name = results.names[class_id]
            confidence = float(box.conf[0])

            if class_name not in class_counts:
                class_counts[class_name] = 0
            class_counts[class_name] += 1

            detection_info.append({
                'class': class_name,
                'confidence': confidence,
                'bbox': box.xyxy[0].tolist()
            })

        # Generate title
        title_parts = [f'Detection Results ({num_detections} objects)']
        for class_name, count in class_counts.items():
            title_parts.append(f'{class_name}: {count}')

        title = '\n'.join(title_parts)
    else:
        title = 'Detection Results (No objects detected)'

    axes[1].set_title(title, fontsize=14, fontweight='bold')
    axes[1].axis('off')

    plt.tight_layout()

    # 保存对比图
    output_path = output_dir / f"result_{image_index+1:02d}_{image_path.stem}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    # 保存单独的检测结果
    result_only_path = output_dir / f"detection_{image_index+1:02d}_{image_path.stem}.jpg"
    cv2.imwrite(str(result_only_path), annotated_image)

    return {
        'image_path': str(image_path),
        'output_path': str(output_path),
        'result_only_path': str(result_only_path),
        'num_detections': num_detections,
        'detections': detection_info,
        'image_size': image.shape[:2]
    }

def create_summary_visualization(results_data, output_dir):
    """Create summary visualization"""

    print("📊 Creating results summary...")

    # 统计总体结果
    total_images = len(results_data)
    total_detections = sum(r['num_detections'] for r in results_data)

    # 统计各类别检测数量
    class_counts = {}
    confidence_scores = []

    for result in results_data:
        for detection in result['detections']:
            class_name = detection['class']
            confidence = detection['confidence']

            if class_name not in class_counts:
                class_counts[class_name] = 0
            class_counts[class_name] += 1
            confidence_scores.append(confidence)

    # 创建统计图表
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # 1. 每张图片的检测数量
    image_indices = range(1, total_images + 1)
    detection_counts = [r['num_detections'] for r in results_data]

    axes[0, 0].bar(image_indices, detection_counts, color='skyblue', alpha=0.7)
    axes[0, 0].set_title('每张图片的检测数量', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel('图片编号')
    axes[0, 0].set_ylabel('检测数量')
    axes[0, 0].grid(True, alpha=0.3)

    # 2. 类别分布
    if class_counts:
        classes = list(class_counts.keys())
        counts = list(class_counts.values())
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']

        axes[0, 1].pie(counts, labels=classes, autopct='%1.1f%%',
                       colors=colors[:len(classes)], startangle=90)
        axes[0, 1].set_title('类别分布', fontsize=14, fontweight='bold')

    # 3. 置信度分布
    if confidence_scores:
        axes[1, 0].hist(confidence_scores, bins=20, color='lightgreen', alpha=0.7, edgecolor='black')
        axes[1, 0].set_title('置信度分布', fontsize=14, fontweight='bold')
        axes[1, 0].set_xlabel('置信度')
        axes[1, 0].set_ylabel('频次')
        axes[1, 0].grid(True, alpha=0.3)

        # 添加统计信息
        mean_conf = np.mean(confidence_scores)
        axes[1, 0].axvline(mean_conf, color='red', linestyle='--',
                          label=f'平均置信度: {mean_conf:.3f}')
        axes[1, 0].legend()

    # 4. 总体统计
    axes[1, 1].axis('off')
    stats_text = f"""
Detection Results Summary

Total Images: {total_images}
Total Detections: {total_detections}
Average per Image: {total_detections/total_images:.1f} objects

Class Statistics:
"""

    for class_name, count in class_counts.items():
        percentage = (count / total_detections) * 100 if total_detections > 0 else 0
        stats_text += f"   {class_name}: {count} ({percentage:.1f}%)\n"

    if confidence_scores:
        stats_text += f"\nConfidence Statistics:\n"
        stats_text += f"   Average: {np.mean(confidence_scores):.3f}\n"
        stats_text += f"   Maximum: {np.max(confidence_scores):.3f}\n"
        stats_text += f"   Minimum: {np.min(confidence_scores):.3f}\n"

    axes[1, 1].text(0.1, 0.9, stats_text, transform=axes[1, 1].transAxes,
                    fontsize=12, verticalalignment='top',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.5))

    plt.suptitle('🏠 Roof Detection Results Overview - 20 Images Visualization Analysis', fontsize=16, fontweight='bold')
    plt.tight_layout()

    # 保存总览图
    summary_path = output_dir / "detection_summary.png"
    plt.savefig(summary_path, dpi=300, bbox_inches='tight')
    plt.close()

    return str(summary_path)

def main():
    """主函数"""

    print("🎨 Roof Detection Visualization Demo")
    print("=" * 50)

    # 创建输出目录
    output_dir = Path("visualization_results")
    output_dir.mkdir(exist_ok=True)

    # 数据集配置
    data_yaml = "data/raw/new-2-1/data.yaml"

    if not os.path.exists(data_yaml):
        print(f"❌ Dataset config file not found: {data_yaml}")
        return

    # Load model
    model, model_path = load_best_model()
    if model is None:
        return

    # Select test images
    test_images = find_test_images(data_yaml, num_images=50)
    if not test_images:
        return

    print(f"\n🚀 Processing {len(test_images)} images...")

    # Process each image
    results_data = []

    for i, image_path in enumerate(test_images):
        print(f"🔍 Processing image {i+1}/50: {image_path.name}")

        try:
            result = predict_and_visualize(model, image_path, output_dir, i)
            results_data.append(result)
            print(f"   ✅ Detected {result['num_detections']} objects")

        except Exception as e:
            print(f"   ❌ Processing failed: {e}")
            continue

    # Create summary
    if results_data:
        summary_path = create_summary_visualization(results_data, output_dir)

        # Save detailed results
        results_json = {
            'model_path': model_path,
            'timestamp': datetime.now().isoformat(),
            'total_images': len(results_data),
            'total_detections': sum(r['num_detections'] for r in results_data),
            'results': results_data
        }

        json_path = output_dir / "detection_results.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results_json, f, indent=2, ensure_ascii=False)

        print(f"\n🎉 Visualization completed!")
        print(f"📁 Results saved in: {output_dir}")
        print(f"📊 Summary chart: {summary_path}")
        print(f"📋 Detailed results: {json_path}")
        print(f"🖼️ Processed images: {len(results_data)}/50")
        print(f"🎯 Total detections: {sum(r['num_detections'] for r in results_data)}")

        # Show class statistics
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