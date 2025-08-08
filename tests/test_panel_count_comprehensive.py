#!/usr/bin/env python3
"""
Panel Count Module 综合测试
Comprehensive tests for Panel Count module

解决可能的冲突和问题
"""

import sys
import os
import numpy as np
from pathlib import Path

# 添加项目路径
sys.path.insert(0, 'src')

def test_imports():
    """测试所有导入"""
    print("🔍 测试模块导入...")
    
    try:
        from panel_count import geometry, planner, roof_io, PANEL_COUNT_AVAILABLE
        print("✅ 主模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 主模块导入失败: {e}")
        return False

def test_geometry_functions():
    """测试几何计算函数"""
    print("\n🔍 测试几何计算函数...")
    
    try:
        from panel_count.geometry import (
            pixels_from_meters, erode_with_margin, 
            calculate_panel_layout_fast, calculate_panel_layout_original,
            estimate_by_area, enhance_panels_with_shading_data
        )
        
        # 测试像素转换
        pixels = pixels_from_meters(5.0, 0.1)
        assert pixels == 50, f"像素转换错误: 期望50, 得到{pixels}"
        print("✅ 像素转换测试通过")
        
        # 测试腐蚀
        test_mask = np.ones((100, 100), dtype=np.uint8) * 255
        eroded = erode_with_margin(test_mask, 5)
        assert eroded.shape == (100, 100), "腐蚀后形状错误"
        print("✅ 腐蚀测试通过")
        
        # 测试快速布局计算
        roof_mask = np.ones((200, 300), dtype=np.uint8) * 255
        panels = calculate_panel_layout_fast(roof_mask, 10, 17)
        print(f"✅ 快速布局计算通过: 找到 {len(panels)} 个面板")
        
        return True
        
    except Exception as e:
        print(f"❌ 几何计算测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_roof_io_functions():
    """测试屋顶IO函数"""
    print("\n🔍 测试屋顶IO函数...")
    
    try:
        from panel_count.roof_io import create_roof_mask, visualize_result
        
        # 测试支持的屋顶形状
        supported_shapes = ['kiritsuma_side', 'yosemune_main', 'katanagare', 'rikuyane']
        
        for shape in supported_shapes:
            mask = create_roof_mask(shape, dimensions=(200, 300))
            non_zero = np.sum(mask > 0)
            print(f"✅ {shape}: {mask.shape}, 非零像素: {non_zero}")
            assert non_zero > 0, f"{shape} 生成了空掩码"
        
        return True
        
    except Exception as e:
        print(f"❌ 屋顶IO测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_planner_step_by_step():
    """逐步测试规划器"""
    print("\n🔍 逐步测试规划器...")
    
    try:
        from panel_count.roof_io import create_roof_mask
        from panel_count.geometry import (
            pixels_from_meters, erode_with_margin, calculate_panel_layout_fast
        )
        
        # 步骤1: 创建屋顶掩码
        roof_mask = create_roof_mask('kiritsuma_side', dimensions=(200, 300))
        print(f"步骤1 - 屋顶掩码: {roof_mask.shape}, 非零像素: {np.sum(roof_mask > 0)}")
        
        # 步骤2: 应用偏移
        gsd = 0.1
        offset_m = 0.1
        margin_px = pixels_from_meters(offset_m, gsd)
        usable_mask = erode_with_margin(roof_mask, margin_px)
        print(f"步骤2 - 可用掩码: 边距{margin_px}px, 非零像素: {np.sum(usable_mask > 0)}")
        
        # 步骤3: 计算面板尺寸
        panel_length_m = 1.65
        panel_width_m = 1.0
        panel_spacing_m = 0.02
        
        panel_w_px = pixels_from_meters(panel_width_m + panel_spacing_m, gsd)
        panel_h_px = pixels_from_meters(panel_length_m + panel_spacing_m, gsd)
        print(f"步骤3 - 面板尺寸: {panel_h_px}x{panel_w_px} pixels")
        
        # 步骤4: 执行布局计算
        if np.sum(usable_mask > 0) > 0:
            panels = calculate_panel_layout_fast(usable_mask, panel_w_px, panel_h_px)
            print(f"步骤4 - 布局计算: 找到 {len(panels)} 个面板")
            
            # 计算容量
            panel_capacity_kw = 0.4  # 400W per panel
            total_capacity = len(panels) * panel_capacity_kw
            print(f"步骤5 - 总容量: {total_capacity} kW")
            
            return len(panels) > 0
        else:
            print("❌ 可用掩码为空")
            return False
        
    except Exception as e:
        print(f"❌ 规划器逐步测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_planner():
    """测试完整规划器"""
    print("\n🔍 测试完整规划器...")
    
    try:
        from panel_count.planner import process_roof
        
        # 使用较大的屋顶尺寸和较小的偏移
        result = process_roof(
            roof_shape_name='rikuyane',  # 陆屋根 - 最简单的矩形
            gsd=0.1,
            panel_options={'standard': (1.65, 1.0)},
            offset_m=0.05,  # 很小的偏移
            panel_spacing_m=0.02,
            dimensions=(400, 600),  # 更大的屋顶
            use_fast_algorithm=True
        )
        
        print("✅ 完整规划器测试成功")
        print(f"   屋顶类型: {result.get('roof_type', 'unknown')}")
        print(f"   面板数量: {result.get('panel_count', 0)}")
        print(f"   总容量: {result.get('total_capacity_kw', 0)} kW")
        print(f"   可用面积: {result.get('usable_area_m2', 0)} m²")
        
        return result.get('panel_count', 0) > 0
        
    except Exception as e:
        print(f"❌ 完整规划器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """测试依赖关系"""
    print("\n🔍 测试依赖关系...")
    
    dependencies = {
        'numpy': 'numpy',
        'opencv-python': 'cv2',
        'scipy': 'scipy.signal'
    }
    
    all_available = True
    for dep_name, import_name in dependencies.items():
        try:
            __import__(import_name)
            print(f"✅ {dep_name} 可用")
        except ImportError:
            print(f"❌ {dep_name} 不可用")
            all_available = False
    
    return all_available

def main():
    """主测试函数"""
    print("🧪 Panel Count Module 综合测试")
    print("=" * 60)
    
    tests = [
        ("依赖关系", test_dependencies),
        ("模块导入", test_imports),
        ("几何计算函数", test_geometry_functions),
        ("屋顶IO函数", test_roof_io_functions),
        ("规划器逐步测试", test_planner_step_by_step),
        ("完整规划器", test_full_planner),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 总结
    print(f"\n{'='*60}")
    print("🎉 测试总结")
    print(f"{'='*60}")
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:20} : {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 测试通过")
    
    if passed == len(results):
        print("🎉 所有测试通过！Panel Count 模块准备就绪。")
        return True
    else:
        print("⚠️ 部分测试失败，需要修复。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
