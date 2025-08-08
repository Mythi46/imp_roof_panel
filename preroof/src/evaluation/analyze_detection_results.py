#!/usr/bin/env python3
"""
分析检测结果统计
"""

import json
import numpy as np
from collections import Counter

def analyze_detection_results():
    """分析检测结果"""
    
    # 读取结果文件
    with open('visualization_results/detection_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("🎨 屋顶检测可视化结果分析")
    print("=" * 50)
    
    # 基本统计
    total_images = data['total_images']
    total_detections = data['total_detections']
    
    print(f"📊 基本统计:")
    print(f"   总图片数: {total_images}")
    print(f"   总检测数: {total_detections}")
    print(f"   平均每图: {total_detections/total_images:.1f}个目标")
    
    # 每张图片的检测数量
    detection_counts = [result['num_detections'] for result in data['results']]
    
    print(f"\n📈 检测数量分布:")
    print(f"   最多检测: {max(detection_counts)}个目标")
    print(f"   最少检测: {min(detection_counts)}个目标")
    print(f"   中位数: {np.median(detection_counts):.1f}个目标")
    print(f"   标准差: {np.std(detection_counts):.1f}")
    
    # 类别统计
    all_classes = []
    all_confidences = []
    
    for result in data['results']:
        for detection in result['detections']:
            all_classes.append(detection['class'])
            all_confidences.append(detection['confidence'])
    
    class_counts = Counter(all_classes)
    
    print(f"\n🏷️ 类别检测统计:")
    for class_name, count in class_counts.most_common():
        percentage = (count / total_detections) * 100
        print(f"   {class_name}: {count}个 ({percentage:.1f}%)")
    
    # 置信度统计
    if all_confidences:
        print(f"\n🎯 置信度统计:")
        print(f"   平均置信度: {np.mean(all_confidences):.3f}")
        print(f"   最高置信度: {np.max(all_confidences):.3f}")
        print(f"   最低置信度: {np.min(all_confidences):.3f}")
        print(f"   置信度标准差: {np.std(all_confidences):.3f}")
        
        # 置信度分布
        high_conf = sum(1 for c in all_confidences if c >= 0.8)
        medium_conf = sum(1 for c in all_confidences if 0.5 <= c < 0.8)
        low_conf = sum(1 for c in all_confidences if c < 0.5)
        
        print(f"\n📊 置信度分布:")
        print(f"   高置信度 (≥0.8): {high_conf}个 ({high_conf/len(all_confidences)*100:.1f}%)")
        print(f"   中置信度 (0.5-0.8): {medium_conf}个 ({medium_conf/len(all_confidences)*100:.1f}%)")
        print(f"   低置信度 (<0.5): {low_conf}个 ({low_conf/len(all_confidences)*100:.1f}%)")
    
    # 图片详细信息
    print(f"\n🖼️ 图片检测详情:")
    for i, result in enumerate(data['results'], 1):
        image_name = result['image_path'].split('\\')[-1]
        num_det = result['num_detections']
        
        # 统计该图片的类别
        image_classes = [det['class'] for det in result['detections']]
        image_class_counts = Counter(image_classes)
        class_summary = ', '.join([f"{cls}({cnt})" for cls, cnt in image_class_counts.items()])
        
        print(f"   图片{i:2d}: {image_name[:30]:<30} | {num_det:2d}个目标 | {class_summary}")
    
    print(f"\n✅ 分析完成!")
    print(f"📁 可视化结果保存在: visualization_results/")
    print(f"🌐 查看HTML画廊: visualization_results/results_gallery.html")

if __name__ == "__main__":
    analyze_detection_results()
