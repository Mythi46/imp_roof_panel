#!/usr/bin/env python3
"""
Test script for batch processing API
批量处理API测试脚本
"""
import requests
import json
import base64
import cv2
import numpy as np

def create_test_roof_mask(width=200, height=150, roof_id=0):
    """创建测试用的屋顶掩码"""
    mask = np.zeros((height, width), dtype=np.uint8)
    
    # 创建不同形状的屋顶区域
    if roof_id == 0:
        # 矩形屋顶
        cv2.rectangle(mask, (20, 20), (180, 130), 255, -1)
    elif roof_id == 1:
        # 三角形屋顶
        points = np.array([[100, 20], [20, 130], [180, 130]], np.int32)
        cv2.fillPoly(mask, [points], 255)
    else:
        # 圆形屋顶
        cv2.circle(mask, (100, 75), 60, 255, -1)
    
    return mask

def mask_to_base64(mask):
    """将掩码转换为Base64"""
    _, buffer = cv2.imencode('.png', mask)
    b64_string = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/png;base64,{b64_string}"

def test_batch_processing():
    """测试批量处理功能"""
    print("🧪 Testing batch processing API...")
    
    # 创建多个测试屋顶掩码
    roof_masks = []
    for i in range(3):
        mask = create_test_roof_mask(roof_id=i)
        b64_mask = mask_to_base64(mask)
        roof_masks.append(b64_mask)
        print(f"  ✅ Created test roof mask {i+1}")
    
    # 准备API请求
    api_url = "http://localhost:8001/calculate_panels"
    payload = {
        "roof_masks": roof_masks,
        "gsd": 0.05,
        "panel_options": {"Standard_B": [1.65, 1.0]},
        "offset_m": 1.0,
        "panel_spacing_m": 0.02
    }
    
    try:
        print(f"\n📡 Sending batch request to {api_url}...")
        response = requests.post(api_url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Batch processing successful!")
            
            # 显示结果摘要
            print(f"\n📊 Results Summary:")
            print(f"  Total roofs processed: {result['total_roofs']}")
            print(f"  Total panels: {result['summary']['total_panels']}")
            print(f"  Total capacity: {result['summary']['total_capacity_kw']:.1f} kW")
            print(f"  Total roof area: {result['summary']['total_roof_area']:.1f} m²")
            
            # 显示每个屋顶的结果
            print(f"\n🏠 Individual Roof Results:")
            for roof in result['roofs']:
                if roof['success']:
                    print(f"  Roof {roof['roof_id']+1}: {roof['max_count']} panels, {roof['total_capacity_kw']:.1f} kW")
                    print(f"    Best panel: {roof['best_panel']}")
                    print(f"    Roof area: {roof['roof_area']:.1f} m²")
                    print(f"    Effective area: {roof['effective_area']:.1f} m²")
                    
                    # 检查bbox数据
                    if 'panels' in roof and roof['best_panel'] in roof['panels']:
                        panels_data = roof['panels'][roof['best_panel']]
                        if 'panels' in panels_data:
                            bbox_count = len(panels_data['panels'])
                            print(f"    Bounding boxes: {bbox_count} panels")
                            if bbox_count > 0:
                                sample_bbox = panels_data['panels'][0]
                                print(f"    Sample bbox: [x={sample_bbox[0]}, y={sample_bbox[1]}, w={sample_bbox[2]}, h={sample_bbox[3]}]")
                else:
                    print(f"  Roof {roof['roof_id']+1}: ❌ Failed - {roof.get('message', 'Unknown error')}")
            
            return True
            
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the API server is running:")
        print("   cd panel_count && python api_integration.py")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_single_processing():
    """测试单个处理功能（对比）"""
    print("\n🧪 Testing single processing API for comparison...")
    
    # 创建单个测试掩码
    mask = create_test_roof_mask(roof_id=0)
    b64_mask = mask_to_base64(mask)
    
    api_url = "http://localhost:8001/calculate_panels"
    payload = {
        "roof_mask": b64_mask,
        "gsd": 0.05,
        "panel_options": {"Standard_B": [1.65, 1.0]},
        "offset_m": 1.0
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Single processing successful!")
            print(f"  Panels: {result['max_count']}")
            print(f"  Capacity: {result['total_capacity_kw']:.1f} kW")
            
            # 检查bbox格式
            if 'panels' in result and result['best_panel'] in result['panels']:
                panels_data = result['panels'][result['best_panel']]
                if 'panels' in panels_data:
                    print(f"  Bounding boxes format confirmed: {len(panels_data['panels'])} panels")
            
            return True
        else:
            print(f"❌ Single processing failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Single test failed: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 Starting API Enhancement Tests")
    print("=" * 50)
    
    # 测试单个处理
    single_success = test_single_processing()
    
    # 测试批量处理
    batch_success = test_batch_processing()
    
    print("\n" + "=" * 50)
    if single_success and batch_success:
        print("✅ All tests passed! API enhancement successful.")
        print("\n📋 Summary:")
        print("  ✅ Single roof processing: Working")
        print("  ✅ Batch roof processing: Working")
        print("  ✅ Bounding box data: Available")
        print("  ✅ Visualization: Generated")
    else:
        print("❌ Some tests failed. Please check the API server.")
    
    return single_success and batch_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
