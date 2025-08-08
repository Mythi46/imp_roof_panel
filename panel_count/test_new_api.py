#!/usr/bin/env python3
"""
新しいAPI端点のテストスクリプト
Test script for the new API endpoints
"""

import requests
import json
import base64
import cv2
import numpy as np

def test_health_endpoint():
    """ヘルスチェックエンドポイントのテスト"""
    print("🔍 Testing /health endpoint...")
    try:
        response = requests.get('http://localhost:8001/health')
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_calculate_panels_with_roof_shape():
    """事前定義屋根形状を使用したテスト"""
    print("\n🔍 Testing /calculate_panels with roof_shape_name...")
    
    test_data = {
        "roof_shape_name": "rikuyane",
        "gsd": 0.05,
        "panel_options": {
            "Standard_B": [1.65, 1.0]
        },
        "offset_m": 1.0,
        "dimensions": [400, 500]
    }
    
    try:
        response = requests.post(
            'http://localhost:8001/calculate_panels',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Success: {result.get('success')}")
        if result.get('success'):
            print(f"Max panels: {result.get('max_count')}")
            print(f"Roof area: {result.get('roof_area'):.1f} m²")
            print(f"Effective area: {result.get('effective_area'):.1f} m²")
            print(f"Total capacity: {result.get('total_capacity_kw', 0):.1f} kW")
        else:
            print(f"Error: {result.get('message')}")
        return response.status_code == 200 and result.get('success')
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def create_test_roof_mask():
    """テスト用の屋根マスクを作成"""
    # 400x500の画像に200x300の白い矩形を作成
    mask = np.zeros((400, 500), dtype=np.uint8)
    mask[100:300, 150:350] = 255  # 白い矩形 = 屋根エリア
    
    # Base64エンコード
    _, buffer = cv2.imencode('.png', mask)
    mask_b64 = base64.b64encode(buffer).decode('utf-8')
    
    return mask_b64

def test_calculate_panels_with_roof_mask():
    """Base64屋根マスクを使用したテスト"""
    print("\n🔍 Testing /calculate_panels with roof_mask...")
    
    roof_mask_b64 = create_test_roof_mask()
    
    test_data = {
        "roof_mask": roof_mask_b64,
        "gsd": 0.05,
        "panel_options": {
            "Standard_B": [1.65, 1.0],
            "Standard_A": [1.65, 0.99]
        },
        "offset_m": 1.0,
        "panel_spacing_m": 0.02
    }
    
    try:
        response = requests.post(
            'http://localhost:8001/calculate_panels',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Success: {result.get('success')}")
        if result.get('success'):
            print(f"Max panels: {result.get('max_count')}")
            print(f"Best panel: {result.get('best_panel')}")
            print(f"Roof area: {result.get('roof_area'):.1f} m²")
            print(f"Total capacity: {result.get('total_capacity_kw', 0):.1f} kW")
            if 'visualization_b64' in result:
                print("✅ Visualization image generated")
        else:
            print(f"Error: {result.get('message')}")
        return response.status_code == 200 and result.get('success')
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_deprecated_endpoints():
    """非推奨エンドポイントのテスト"""
    print("\n🔍 Testing deprecated endpoints...")
    
    # Test /process_roof_segments
    try:
        response = requests.post(
            'http://localhost:8001/process_roof_segments',
            json={"test": "data"},
            headers={'Content-Type': 'application/json'}
        )
        print(f"/process_roof_segments Status: {response.status_code}")
        result = response.json()
        print(f"Deprecated: {result.get('deprecated')}")
        print(f"New endpoint: {result.get('new_endpoint')}")
    except Exception as e:
        print(f"❌ Deprecated endpoint test failed: {e}")

def main():
    """メインテスト関数"""
    print("🚀 Starting API endpoint tests...")
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Calculate Panels (Roof Shape)", test_calculate_panels_with_roof_shape),
        ("Calculate Panels (Roof Mask)", test_calculate_panels_with_roof_mask),
        ("Deprecated Endpoints", test_deprecated_endpoints)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        try:
            success = test_func()
            results.append((test_name, success))
            print(f"✅ {test_name}: {'PASSED' if success else 'FAILED'}")
        except Exception as e:
            print(f"❌ {test_name}: FAILED - {e}")
            results.append((test_name, False))
    
    # 結果サマリー
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is ready for use.")
    else:
        print("⚠️  Some tests failed. Please check the API server.")

if __name__ == '__main__':
    main()
