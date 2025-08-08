#!/usr/bin/env python3
"""
整理项目中暂时不需要的脚本文件
Organize temporarily unused script files in the project
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def create_organization_structure():
    """创建整理目录结构"""
    print("📁 Creating organization structure...")
    
    # 创建主要的整理目录
    base_dir = Path("scripts_archive")
    
    # 创建分类目录
    categories = {
        "utilities": "工具脚本 - 辅助功能和实用工具",
        "visualization": "可视化脚本 - 图表生成和展示相关",
        "analysis": "分析脚本 - 数据分析和状态检查",
        "setup": "设置脚本 - 环境配置和初始化",
        "experimental": "实验脚本 - 测试和实验性功能",
        "legacy": "遗留脚本 - 旧版本和备用脚本"
    }
    
    for category, description in categories.items():
        category_dir = base_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建说明文件
        readme_path = category_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"# {category.title()} Scripts\n\n")
            f.write(f"{description}\n\n")
            f.write(f"整理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## 文件列表\n\n")
    
    print(f"✅ Organization structure created: {base_dir}")
    return base_dir

def identify_scripts_to_organize():
    """识别需要整理的脚本文件"""
    print("🔍 Identifying scripts to organize...")
    
    # 根目录下的脚本文件分类
    scripts_to_organize = {
        "utilities": [
            "check_model_status.py",
            "organize_remaining_files.py", 
            "remove_duplicates.py"
        ],
        "visualization": [
            "fix_visualization_fonts.py",
            "generate_50_images_visualization.py",
            "generate_complete_html.py",
            "generate_english_charts.py",
            "generate_english_summary.py"
        ],
        "analysis": [
            # 分析相关的脚本会在这里
        ],
        "setup": [
            # 设置相关的脚本会在这里
        ],
        "experimental": [
            # 实验性脚本会在这里
        ],
        "legacy": [
            # 遗留脚本会在这里
        ]
    }
    
    # 检查文件是否存在
    existing_scripts = {}
    for category, files in scripts_to_organize.items():
        existing_scripts[category] = []
        for file in files:
            if os.path.exists(file):
                existing_scripts[category].append(file)
                print(f"  📄 Found: {file} -> {category}")
    
    return existing_scripts

def move_scripts(scripts_dict, base_dir):
    """移动脚本文件到对应目录"""
    print("📦 Moving scripts to organized directories...")
    
    moved_files = []
    
    for category, files in scripts_dict.items():
        if not files:
            continue
            
        category_dir = base_dir / category
        
        for file in files:
            try:
                source_path = Path(file)
                dest_path = category_dir / source_path.name
                
                # 移动文件
                shutil.move(str(source_path), str(dest_path))
                moved_files.append({
                    'file': file,
                    'category': category,
                    'new_path': str(dest_path)
                })
                
                print(f"  ✅ Moved: {file} -> {category}/")
                
                # 更新对应的README
                readme_path = category_dir / "README.md"
                with open(readme_path, 'a', encoding='utf-8') as f:
                    f.write(f"- `{source_path.name}` - 移动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                
            except Exception as e:
                print(f"  ❌ Error moving {file}: {e}")
    
    return moved_files

def organize_json_files():
    """整理JSON状态文件"""
    print("📋 Organizing JSON status files...")
    
    json_files = [
        "duplicate_removal_summary.json",
        "project_status_report.json", 
        "root_cleanup_summary.json"
    ]
    
    # 创建状态文件目录
    status_dir = Path("project_status")
    status_dir.mkdir(exist_ok=True)
    
    moved_json = []
    
    for json_file in json_files:
        if os.path.exists(json_file):
            try:
                source_path = Path(json_file)
                dest_path = status_dir / source_path.name
                
                shutil.move(str(source_path), str(dest_path))
                moved_json.append({
                    'file': json_file,
                    'new_path': str(dest_path)
                })
                
                print(f"  ✅ Moved: {json_file} -> project_status/")
                
            except Exception as e:
                print(f"  ❌ Error moving {json_file}: {e}")
    
    # 创建状态目录的README
    readme_path = status_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write("# Project Status Files\n\n")
        f.write("项目状态和报告文件\n\n")
        f.write(f"整理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## 文件说明\n\n")
        f.write("- `duplicate_removal_summary.json` - 重复文件清理报告\n")
        f.write("- `project_status_report.json` - 项目状态检查报告\n")
        f.write("- `root_cleanup_summary.json` - 根目录清理报告\n")
    
    return moved_json

def organize_misc_files():
    """整理其他杂项文件"""
    print("🗂️ Organizing miscellaneous files...")
    
    misc_files = [
        "font_test_result.png"
    ]
    
    # 创建临时文件目录
    temp_dir = Path("temp_files")
    temp_dir.mkdir(exist_ok=True)
    
    moved_misc = []
    
    for misc_file in misc_files:
        if os.path.exists(misc_file):
            try:
                source_path = Path(misc_file)
                dest_path = temp_dir / source_path.name
                
                shutil.move(str(source_path), str(dest_path))
                moved_misc.append({
                    'file': misc_file,
                    'new_path': str(dest_path)
                })
                
                print(f"  ✅ Moved: {misc_file} -> temp_files/")
                
            except Exception as e:
                print(f"  ❌ Error moving {misc_file}: {e}")
    
    # 创建临时文件目录的README
    readme_path = temp_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write("# Temporary Files\n\n")
        f.write("临时生成的文件和测试文件\n\n")
        f.write(f"整理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## 文件说明\n\n")
        f.write("- `font_test_result.png` - 字体测试结果图片\n")
    
    return moved_misc

def generate_organization_report(moved_scripts, moved_json, moved_misc):
    """生成整理报告"""
    print("📄 Generating organization report...")
    
    report = {
        "organization_time": datetime.now().isoformat(),
        "summary": {
            "total_files_moved": len(moved_scripts) + len(moved_json) + len(moved_misc),
            "scripts_moved": len(moved_scripts),
            "json_files_moved": len(moved_json),
            "misc_files_moved": len(moved_misc)
        },
        "moved_files": {
            "scripts": moved_scripts,
            "json_files": moved_json,
            "misc_files": moved_misc
        },
        "new_structure": {
            "scripts_archive/": "脚本归档目录",
            "scripts_archive/utilities/": "工具脚本",
            "scripts_archive/visualization/": "可视化脚本",
            "scripts_archive/analysis/": "分析脚本",
            "scripts_archive/setup/": "设置脚本",
            "scripts_archive/experimental/": "实验脚本",
            "scripts_archive/legacy/": "遗留脚本",
            "project_status/": "项目状态文件",
            "temp_files/": "临时文件"
        }
    }
    
    # 保存报告
    report_path = "organization_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        import json
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Organization report saved: {report_path}")
    return report

def main():
    """主函数"""
    print("🗂️ Project Scripts Organization")
    print("=" * 50)
    print(f"📅 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 1. 创建整理目录结构
    base_dir = create_organization_structure()
    
    # 2. 识别需要整理的脚本
    scripts_to_move = identify_scripts_to_organize()
    
    # 3. 移动脚本文件
    moved_scripts = move_scripts(scripts_to_move, base_dir)
    
    # 4. 整理JSON状态文件
    moved_json = organize_json_files()
    
    # 5. 整理其他杂项文件
    moved_misc = organize_misc_files()
    
    # 6. 生成整理报告
    report = generate_organization_report(moved_scripts, moved_json, moved_misc)
    
    # 7. 显示总结
    print("\n🎉 Organization completed!")
    print("=" * 50)
    print(f"📊 Total files moved: {report['summary']['total_files_moved']}")
    print(f"📄 Scripts moved: {report['summary']['scripts_moved']}")
    print(f"📋 JSON files moved: {report['summary']['json_files_moved']}")
    print(f"🗂️ Misc files moved: {report['summary']['misc_files_moved']}")
    print("\n📁 New directory structure:")
    for directory, description in report['new_structure'].items():
        print(f"   {directory} - {description}")
    
    print(f"\n📄 Detailed report: organization_report.json")
    print("✨ Project root directory is now cleaner and more organized!")

if __name__ == "__main__":
    main()
