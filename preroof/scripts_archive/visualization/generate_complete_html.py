#!/usr/bin/env python3
"""
生成包含所有正确文件名的HTML页面
Generate HTML page with all correct filenames
"""

import os
import json
from pathlib import Path
from collections import Counter

def load_detection_data():
    """加载检测结果数据"""
    json_path = Path("visualization_results_50/detection_results_50.json")

    if not json_path.exists():
        print(f"⚠️ Detection results JSON not found: {json_path}")
        return None

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data

def get_result_files_with_detections():
    """获取所有result文件的文件名和检测信息"""
    viz_dir = Path("visualization_results_50")
    detection_data = load_detection_data()

    result_info = []

    if detection_data:
        # 使用JSON数据中的信息
        for result in detection_data['results']:
            image_index = result['image_index']
            result_filename = result['result_image']

            # 统计检测类别
            detections = result['detections']
            class_counts = Counter([det['class'] for det in detections])

            # 生成类别标签
            class_labels = []
            for class_name, count in class_counts.items():
                class_labels.append(f"{class_name}: {count}")

            result_info.append({
                'filename': result_filename,
                'index': image_index,
                'num_detections': result['num_detections'],
                'class_labels': class_labels,
                'class_counts': class_counts
            })
    else:
        # 备用方案：只获取文件名
        for i in range(1, 51):
            pattern = f"result_{i:02d}_"
            for file in viz_dir.iterdir():
                if file.name.startswith(pattern) and file.name.endswith('.png'):
                    result_info.append({
                        'filename': file.name,
                        'index': i,
                        'num_detections': 0,
                        'class_labels': [],
                        'class_counts': {}
                    })
                    break

    return result_info

def generate_html():
    """生成完整的HTML页面"""
    result_info = get_result_files_with_detections()
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏠 Roof Detection Results - 50 Images Analysis</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
            padding: 30px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.95);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
        }

        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }

        .stat-label {
            font-size: 1.1em;
            color: #666;
            font-weight: 500;
        }

        .summary-section {
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }

        .summary-image {
            width: 100%;
            max-width: 800px;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            margin: 20px auto;
            display: block;
        }

        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }

        .image-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }

        .image-card:hover {
            transform: translateY(-5px);
        }

        .image-card img {
            width: 100%;
            height: 200px;
            object-fit: cover;
            cursor: pointer;
        }

        .image-info {
            padding: 15px;
        }

        .image-title {
            font-weight: bold;
            margin-bottom: 5px;
            color: #333;
        }

        .image-details {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
        }

        .detection-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-top: 8px;
        }

        .detection-tag {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.75em;
            font-weight: 500;
            color: white;
            text-shadow: 1px 1px 1px rgba(0,0,0,0.3);
        }

        .tag-roof { background-color: #DC143C; }
        .tag-rice-fields { background-color: #4169E1; }
        .tag-baren-land { background-color: #8B4513; }
        .tag-farm { background-color: #228B22; }

        .detection-count {
            font-size: 0.8em;
            color: #888;
            margin-top: 5px;
            font-style: italic;
        }

        .class-legend {
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 20px;
            margin: 20px 0;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 15px;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 20px;
            font-weight: 500;
        }

        .legend-color {
            width: 20px;
            height: 20px;
            border-radius: 50%;
        }

        .roof { background-color: #DC143C; }
        .rice-fields { background-color: #4169E1; }
        .baren-land { background-color: #8B4513; }
        .farm { background-color: #228B22; }

        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.9);
        }

        .modal-content {
            margin: auto;
            display: block;
            width: 90%;
            max-width: 1200px;
            max-height: 90%;
            object-fit: contain;
            margin-top: 2%;
        }

        .close {
            position: absolute;
            top: 15px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }

        .close:hover {
            color: #bbb;
        }

        .section-title {
            font-size: 2em;
            margin-bottom: 20px;
            color: #333;
            text-align: center;
            font-weight: 600;
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 2em;
            }
            
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .gallery {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🏠 Roof Detection Results</h1>
            <p>Comprehensive Analysis of 50 Images using Expert Improved YOLOv8 Model</p>
            <p><strong>Model Performance:</strong> mAP@0.5: 90.8% | Processing Date: 2025-07-29</p>
        </div>

        <!-- Statistics -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">50</div>
                <div class="stat-label">Images Processed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">850</div>
                <div class="stat-label">Total Detections</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">17.0</div>
                <div class="stat-label">Avg Objects/Image</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">100%</div>
                <div class="stat-label">Success Rate</div>
            </div>
        </div>

        <!-- Class Legend -->
        <div class="class-legend">
            <div class="legend-item">
                <div class="legend-color roof"></div>
                <span>Roof (561 - 66.0%)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color rice-fields"></div>
                <span>Rice Fields (110 - 12.9%)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color baren-land"></div>
                <span>Bare Land (101 - 11.9%)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color farm"></div>
                <span>Farm (78 - 9.2%)</span>
            </div>
        </div>

        <!-- Summary Section -->
        <div class="summary-section">
            <h2 class="section-title">📊 Detection Summary</h2>
            <img src="detection_summary_50_images.png" alt="Detection Summary" class="summary-image">
            <p style="text-align: center; margin-top: 15px; color: #666;">
                Comprehensive analysis showing class distribution, detection counts, and confidence statistics for all 50 processed images.
            </p>
        </div>

        <!-- Results Gallery -->
        <div class="summary-section">
            <h2 class="section-title">🖼️ Detection Results Gallery</h2>
            <p style="text-align: center; margin-bottom: 20px; color: #666;">
                Click on any image to view in full size. Each image shows original vs detection results side by side.
            </p>
            
            <div class="gallery" id="gallery">
'''
    
    # 添加所有图片
    for info in result_info:
        filename = info['filename']
        index = info['index']
        num_detections = info['num_detections']
        class_labels = info['class_labels']
        class_counts = info['class_counts']

        if filename:
            # 提取简化的图片名称用于显示
            display_name = filename.replace('result_', '').replace('.png', '').split('_')[1] if '_' in filename else f"Image {index}"

            # 生成检测标签
            detection_tags_html = ""
            for class_name, count in class_counts.items():
                tag_class = f"tag-{class_name.replace('-', '-')}"
                detection_tags_html += f'<span class="detection-tag {tag_class}">{class_name}: {count}</span>'

            html_content += f'''
                <div class="image-card">
                    <img src="{filename}" alt="Detection Result {index}" onclick="openModal(this.src)">
                    <div class="image-info">
                        <div class="image-title">Detection Result {index}</div>
                        <div class="image-details">{display_name}</div>
                        <div class="detection-count">Total: {num_detections} objects</div>
                        <div class="detection-tags">
                            {detection_tags_html}
                        </div>
                    </div>
                </div>'''
    
    html_content += '''
            </div>
        </div>
    </div>

    <!-- Modal for full-size images -->
    <div id="imageModal" class="modal">
        <span class="close">&times;</span>
        <img class="modal-content" id="modalImage">
    </div>

    <script>
        // Modal functionality
        const modal = document.getElementById('imageModal');
        const modalImg = document.getElementById('modalImage');
        const closeBtn = document.getElementsByClassName('close')[0];

        function openModal(src) {
            modal.style.display = 'block';
            modalImg.src = src;
        }

        closeBtn.onclick = function() {
            modal.style.display = 'none';
        }

        modal.onclick = function(event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        }

        // Keyboard navigation
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                modal.style.display = 'none';
            }
        });
    </script>
</body>
</html>'''
    
    return html_content

def main():
    """主函数"""
    print("🎨 Generating Complete HTML with All 50 Images")
    print("=" * 50)
    
    # 生成HTML内容
    html_content = generate_html()
    
    # 保存HTML文件
    output_path = "visualization_results_50/index_complete.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Complete HTML generated: {output_path}")
    print("📊 Features:")
    print("   - All 50 detection results with correct filenames")
    print("   - Click to view full-size images")
    print("   - Responsive design")
    print("   - Modal image viewer")
    print("   - Complete statistics")

if __name__ == "__main__":
    main()
