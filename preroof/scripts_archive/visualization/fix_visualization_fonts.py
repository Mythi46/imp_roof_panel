#!/usr/bin/env python3
"""
修复可视化图表中文乱码问题
Fix Chinese character encoding issues in visualization charts
"""

import os
import sys
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from pathlib import Path

def check_chinese_fonts():
    """检查系统中可用的中文字体"""
    print("🔍 检查系统中文字体...")
    
    # 常见的中文字体名称
    chinese_font_names = [
        'SimHei',           # 黑体
        'Microsoft YaHei',  # 微软雅黑
        'SimSun',          # 宋体
        'KaiTi',           # 楷体
        'FangSong',        # 仿宋
        'Arial Unicode MS', # Arial Unicode MS
        'DejaVu Sans',     # DejaVu Sans (Linux)
        'WenQuanYi Micro Hei', # 文泉驿微米黑 (Linux)
    ]
    
    available_fonts = []
    
    # 获取所有字体
    all_fonts = fm.fontManager.ttflist
    
    for font in all_fonts:
        for chinese_name in chinese_font_names:
            if chinese_name.lower() in font.name.lower():
                available_fonts.append({
                    'name': font.name,
                    'fname': font.fname,
                    'path': font.fname
                })
                break
    
    # 去重
    unique_fonts = []
    seen_names = set()
    for font in available_fonts:
        if font['name'] not in seen_names:
            unique_fonts.append(font)
            seen_names.add(font['name'])
    
    print(f"✅ 找到 {len(unique_fonts)} 个中文字体:")
    for i, font in enumerate(unique_fonts, 1):
        print(f"  {i}. {font['name']}")
        print(f"     路径: {font['path']}")
    
    return unique_fonts

def test_chinese_display(font_name=None):
    """测试中文显示效果"""
    print(f"\n🧪 测试中文显示效果...")
    
    if font_name:
        plt.rcParams['font.sans-serif'] = [font_name]
        print(f"📝 使用字体: {font_name}")
    else:
        # 设置字体优先级
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans', 'Arial Unicode MS']
        print("📝 使用默认字体优先级")
    
    plt.rcParams['axes.unicode_minus'] = False
    
    # 创建测试图表
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 测试数据
    categories = ['裸地', '农田', '水田', '屋顶']
    values = [25, 30, 20, 25]
    colors = ['#8B4513', '#228B22', '#4169E1', '#DC143C']
    
    # 创建饼图
    wedges, texts, autotexts = ax.pie(values, labels=categories, colors=colors, 
                                     autopct='%1.1f%%', startangle=90)
    
    # 设置标题
    ax.set_title('屋根检出結果統計 - 中文字体测试', fontsize=16, fontweight='bold')
    
    # 添加图例
    ax.legend(wedges, categories, title="检测类别", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    plt.tight_layout()
    
    # 保存测试图片
    test_output = "font_test_result.png"
    plt.savefig(test_output, dpi=150, bbox_inches='tight')
    plt.show()
    
    print(f"✅ 测试图片已保存: {test_output}")
    print("📝 请检查图片中的中文是否正常显示")
    
    return test_output

def fix_matplotlib_config():
    """修复matplotlib配置"""
    print("\n🔧 修复matplotlib配置...")
    
    # 获取matplotlib配置目录
    config_dir = plt.get_configdir()
    print(f"📁 配置目录: {config_dir}")
    
    # 创建配置文件内容
    config_content = """
# Matplotlib configuration for Chinese font support
font.sans-serif: SimHei, Microsoft YaHei, DejaVu Sans, Arial Unicode MS
axes.unicode_minus: False
font.family: sans-serif
"""
    
    # 写入配置文件
    config_file = os.path.join(config_dir, 'matplotlibrc')
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content.strip())
        print(f"✅ 配置文件已更新: {config_file}")
        print("📝 重启Python后生效")
    except Exception as e:
        print(f"❌ 配置文件写入失败: {e}")

def regenerate_visualization_with_fonts():
    """重新生成带有正确字体的可视化结果"""
    print("\n🎨 重新生成可视化结果...")
    
    # 设置字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 检查可视化脚本是否存在
    viz_scripts = [
        'src/visualization/generate_visualization_results.py',
        'generate_visualization_results.py',
        'visualize_results_demo.py'
    ]
    
    script_found = None
    for script in viz_scripts:
        if os.path.exists(script):
            script_found = script
            break
    
    if script_found:
        print(f"✅ 找到可视化脚本: {script_found}")
        print("📝 请运行以下命令重新生成可视化结果:")
        print(f"   python {script_found}")
    else:
        print("⚠️ 未找到可视化脚本")
        print("📝 请手动运行可视化脚本")

def main():
    """主函数"""
    print("🔧 修复可视化图表中文乱码问题")
    print("=" * 50)
    
    # 1. 检查中文字体
    available_fonts = check_chinese_fonts()
    
    if not available_fonts:
        print("\n❌ 未找到中文字体!")
        print("💡 解决方案:")
        print("   1. Windows: 确保安装了SimHei或Microsoft YaHei字体")
        print("   2. Linux: 安装中文字体包 (sudo apt-get install fonts-wqy-microhei)")
        print("   3. macOS: 使用系统自带的中文字体")
        return
    
    # 2. 测试中文显示
    best_font = available_fonts[0]['name']
    test_chinese_display(best_font)
    
    # 3. 修复matplotlib配置
    fix_matplotlib_config()
    
    # 4. 提供重新生成指导
    regenerate_visualization_with_fonts()
    
    print("\n🎉 字体修复完成!")
    print("📝 建议:")
    print("   1. 重启Python环境")
    print("   2. 重新运行可视化脚本")
    print("   3. 检查生成的图片是否正常显示中文")

if __name__ == "__main__":
    main()
