#!/usr/bin/env python3
"""
整理太阳能板计算结果文件到专门的文件夹中
"""

import os
import shutil
import glob
from pathlib import Path

def create_result_folders():
    """创建结果文件夹结构"""
    folders = [
        "results",
        "results/csv_data",
        "results/visualizations", 
        "results/reports",
        "results/logs",
        "results/scripts"
    ]
    
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
        print(f"Created folder: {folder}")

def move_files():
    """移动文件到相应文件夹"""
    
    # CSV数据文件
    csv_files = [
        "all_samples_results.csv",
        "sample_results.csv", 
        "segment_results.csv",
        "test_results.csv",
        "result_summary.csv"
    ]
    
    for file in csv_files:
        if os.path.exists(file):
            shutil.move(file, f"results/csv_data/{file}")
            print(f"Moved {file} to results/csv_data/")
    
    # 可视化图片文件
    png_files = glob.glob("result_*.png")
    for file in png_files:
        if os.path.exists(file):
            shutil.move(file, f"results/visualizations/{os.path.basename(file)}")
            print(f"Moved {file} to results/visualizations/")
    
    # 报告文件
    report_files = [
        "sample_analysis_report.md",
        "report.md",
        "report_ja_en.md"
    ]
    
    for file in report_files:
        if os.path.exists(file):
            shutil.move(file, f"results/reports/{file}")
            print(f"Moved {file} to results/reports/")
    
    # 日志文件
    log_files = [
        "panel_calculator.log"
    ]
    
    for file in log_files:
        if os.path.exists(file):
            shutil.move(file, f"results/logs/{file}")
            print(f"Moved {file} to results/logs/")
    
    # 脚本文件
    script_files = [
        "calculate_all_samples.py"
    ]
    
    for file in script_files:
        if os.path.exists(file):
            shutil.copy2(file, f"results/scripts/{file}")
            print(f"Copied {file} to results/scripts/")

def create_readme():
    """创建README文件说明结果文件夹结构"""
    readme_content = """# 太阳能板计算结果文件

## 文件夹结构

### csv_data/
包含所有CSV格式的计算数据：
- `all_samples_results.csv` - 所有sample图片的完整计算结果
- `sample_results.csv` - 完整屋顶图片的计算结果
- `segment_results.csv` - 分段屋顶图片的计算结果
- `result_summary.csv` - 几何形状屋顶的计算结果

### visualizations/
包含所有可视化图片：
- `result_*.png` - 太阳能板布局可视化图片
- 文件名格式：`result_[屋顶类型]_[面板型号].png`

### reports/
包含分析报告：
- `sample_analysis_report.md` - Sample图片分析报告
- `report.md` - 系统技术报告（中文）
- `report_ja_en.md` - 系统技术报告（日英双语）

### logs/
包含运行日志：
- `panel_calculator.log` - 系统运行日志

### scripts/
包含相关脚本：
- `calculate_all_samples.py` - 批量计算脚本

## 使用说明

1. 查看 `reports/sample_analysis_report.md` 了解详细分析结果
2. 查看 `csv_data/` 中的CSV文件获取具体数据
3. 查看 `visualizations/` 中的图片了解面板布局
4. 查看 `logs/` 中的日志文件排查问题

生成时间: 2025-06-25
"""
    
    with open("results/README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("Created results/README.md")

def main():
    print("=== 整理太阳能板计算结果文件 ===\n")
    
    # 创建文件夹结构
    create_result_folders()
    print()
    
    # 移动文件
    print("Moving files...")
    move_files()
    print()
    
    # 创建README
    create_readme()
    print()
    
    print("=== 文件整理完成 ===")
    print("所有结果文件已整理到 'results' 文件夹中")
    print("请查看 'results/README.md' 了解文件夹结构")

if __name__ == "__main__":
    main()
