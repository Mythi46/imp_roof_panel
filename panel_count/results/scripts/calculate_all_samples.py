#!/usr/bin/env python3
"""
批量计算sample文件夹中所有屋顶图片的太阳能板布局
"""

import os
import glob
import subprocess
import sys

def find_sample_images():
    """查找sample文件夹中的所有图片文件"""
    sample_dir = "sample"
    if not os.path.exists(sample_dir):
        print(f"Error: {sample_dir} directory not found")
        return []
    
    # 支持的图片格式
    extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.tiff']
    image_files = []
    
    for ext in extensions:
        pattern = os.path.join(sample_dir, ext)
        image_files.extend(glob.glob(pattern))
    
    return sorted(image_files)

def run_calculation(image_files, output_csv="all_samples_results.csv"):
    """运行太阳能板计算"""
    if not image_files:
        print("No image files found")
        return False
    
    print(f"Found {len(image_files)} image files:")
    for img in image_files:
        print(f"  - {img}")
    
    # 构建命令
    cmd = [
        sys.executable, "main.py",
        "--roof-types"] + image_files + [
        "--fast",
        "--output-csv", output_csv,
        "--log-level", "INFO"
    ]
    
    print(f"\nRunning calculation...")
    print(f"Output will be saved to: {output_csv}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Calculation completed successfully!")
        print("\nOutput:")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running calculation: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    print("=== 太阳能板计算 - Sample图片批量处理 ===\n")
    
    # 查找图片文件
    image_files = find_sample_images()
    
    if not image_files:
        print("No image files found in sample directory")
        return 1
    
    # 运行计算
    success = run_calculation(image_files)
    
    if success:
        print("\n=== 计算完成 ===")
        print("结果文件:")
        print("  - all_samples_results.csv (详细数据)")
        print("  - result_*.png (可视化图片)")
        print("  - panel_calculator.log (日志文件)")
        return 0
    else:
        print("\n=== 计算失败 ===")
        return 1

if __name__ == "__main__":
    sys.exit(main())
