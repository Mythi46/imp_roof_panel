#!/usr/bin/env python3
"""
GSD (Ground Sample Distance) 估算工具
帮助用户根据已知信息估算合适的GSD值
"""

import cv2
import numpy as np

def estimate_gsd_from_known_dimension():
    """基于已知尺寸估算GSD"""
    print("=== GSD估算工具 ===\n")
    print("如果您知道图片中某个物体的实际尺寸，可以用来估算GSD")
    
    # 获取用户输入
    image_path = input("请输入图片路径: ").strip()
    
    try:
        # 加载图片
        img = cv2.imread(image_path)
        if img is None:
            print(f"无法加载图片: {image_path}")
            return None
            
        height, width = img.shape[:2]
        print(f"图片尺寸: {width} × {height} 像素")
        
        # 获取已知尺寸信息
        print("\n请提供一个已知的实际尺寸:")
        real_length = float(input("实际长度 (米): "))
        pixel_length = float(input("对应的像素长度: "))
        
        # 计算GSD
        gsd = real_length / pixel_length
        
        print(f"\n估算结果:")
        print(f"GSD = {gsd:.4f} m/pixel")
        print(f"图片覆盖的实际尺寸: {width * gsd:.2f}m × {height * gsd:.2f}m")
        print(f"总面积: {width * height * gsd * gsd:.2f} m²")
        
        return gsd
        
    except Exception as e:
        print(f"处理过程中出错: {e}")
        return None

def estimate_gsd_from_typical_roof():
    """基于典型屋顶尺寸估算GSD"""
    print("=== 基于典型屋顶尺寸估算GSD ===\n")
    
    image_path = input("请输入图片路径: ").strip()
    
    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f"无法加载图片: {image_path}")
            return None
            
        height, width = img.shape[:2]
        print(f"图片尺寸: {width} × {height} 像素")
        
        print("\n典型住宅屋顶尺寸参考:")
        print("1. 小型住宅: 8m × 12m (96 m²)")
        print("2. 中型住宅: 10m × 15m (150 m²)")
        print("3. 大型住宅: 12m × 20m (240 m²)")
        
        roof_area = float(input("\n请输入您估计的屋顶面积 (m²): "))
        
        # 假设屋顶占图片的比例
        print("\n屋顶在图片中的占比:")
        print("1. 屋顶占满整个图片 (100%)")
        print("2. 屋顶占图片大部分 (80%)")
        print("3. 屋顶占图片一半 (50%)")
        print("4. 屋顶占图片小部分 (30%)")
        
        ratio_choice = input("请选择 (1-4): ").strip()
        ratio_map = {"1": 1.0, "2": 0.8, "3": 0.5, "4": 0.3}
        roof_ratio = ratio_map.get(ratio_choice, 0.8)
        
        # 计算GSD
        image_area_pixels = width * height
        roof_area_pixels = image_area_pixels * roof_ratio
        gsd = (roof_area / roof_area_pixels) ** 0.5
        
        print(f"\n估算结果:")
        print(f"GSD = {gsd:.4f} m/pixel")
        print(f"图片覆盖的实际尺寸: {width * gsd:.2f}m × {height * gsd:.2f}m")
        print(f"屋顶实际尺寸: {(roof_area_pixels * gsd * gsd)**0.5:.2f}m × {(roof_area_pixels * gsd * gsd)**0.5:.2f}m (假设正方形)")
        
        return gsd
        
    except Exception as e:
        print(f"处理过程中出错: {e}")
        return None

def main():
    print("GSD (Ground Sample Distance) 估算工具")
    print("=====================================\n")
    
    print("选择估算方法:")
    print("1. 基于已知物体尺寸估算")
    print("2. 基于典型屋顶尺寸估算")
    print("3. 查看当前使用的默认值")
    
    choice = input("\n请选择 (1-3): ").strip()
    
    if choice == "1":
        gsd = estimate_gsd_from_known_dimension()
    elif choice == "2":
        gsd = estimate_gsd_from_typical_roof()
    elif choice == "3":
        print("\n当前系统默认GSD值:")
        print("GSD = 0.05 m/pixel (每像素5厘米)")
        print("这意味着:")
        print("- 400×500像素的图片覆盖 20m × 25m = 500 m²")
        print("- 适用于高分辨率航拍图像")
        print("\n如果您的图片不是高分辨率航拍，这个值可能不准确。")
        return
    else:
        print("无效选择")
        return
    
    if gsd:
        print(f"\n建议使用以下命令重新计算:")
        print(f"python main.py --roof-types \"sample/a full.png\" --gsd {gsd:.4f} --fast")

if __name__ == "__main__":
    main()
