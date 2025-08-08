#!/usr/bin/env python3
import os
import glob

def check_weight_files():
    """检查项目中的权重文件"""
    print("=== 检查屋顶检测项目中的权重文件 ===\n")
    
    # 定义要检查的路径
    weight_paths = [
        "runs/segment/continue_training_optimized/weights/best.pt",
        "runs/segment/continue_training_optimized/weights/last.pt", 
        "runs/segment/improved_training_compatible/weights/best.pt",
        "runs/segment/improved_training_compatible/weights/last.pt",
        "models/trained/*.pt"
    ]
    
    found_files = []
    
    for path in weight_paths:
        if "*" in path:
            # 使用glob处理通配符
            files = glob.glob(path)
            for file in files:
                if os.path.exists(file):
                    size = os.path.getsize(file)
                    size_mb = size / (1024 * 1024)
                    found_files.append((file, size_mb))
                    print(f"✅ 找到: {file} ({size_mb:.2f} MB)")
        else:
            if os.path.exists(path):
                size = os.path.getsize(path)
                size_mb = size / (1024 * 1024)
                found_files.append((path, size_mb))
                print(f"✅ 找到: {path} ({size_mb:.2f} MB)")
            else:
                print(f"❌ 未找到: {path}")
    
    print(f"\n=== 总结 ===")
    print(f"总共找到 {len(found_files)} 个权重文件")
    
    if found_files:
        print("\n最重要的权重文件:")
        for file, size in found_files:
            if "best.pt" in file and "continue_training_optimized" in file:
                print(f"🎯 主要模型: {file} ({size:.2f} MB)")
                print(f"   - 这是达到90.77% mAP@0.5性能的最佳模型")
                break
    else:
        print("❌ 没有找到任何权重文件")
        print("可能的原因:")
        print("1. 权重文件被移动到其他位置")
        print("2. 权重文件被删除")
        print("3. 训练过程中没有保存权重")
    
    return found_files

if __name__ == "__main__":
    check_weight_files()
