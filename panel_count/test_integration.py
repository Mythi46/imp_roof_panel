#!/usr/bin/env python3
"""
API集成测试脚本
Test script for API integration
"""

import requests
import json
import base64
import cv2
import numpy as np

def create_test_mask():
    """テスト用のマスク画像を作成"""
    # 400x500の画像を作成
    mask = np.zeros((400, 500), dtype=np.uint8)
    
    # 矩形の屋根を作成
    cv2.rectangle(mask, (50, 50), (450, 350), 255, -1)
    
    return mask

def mask_to_base64(mask_image):
    """マスク画像をBase64エンコード"""
    _, buffer = cv2.imencode('.png', mask_image)
    img_b64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/png;base64,{img_b64}"

def test_api_integration():
    """API統合をテスト"""
    print("=== API統合テスト ===\n")

    # テストデータを作成
    test_mask = create_test_mask()
    mask_b64 = mask_to_base64(test_mask)

    test_data = {
        "mask": mask_b64,
        "centers": [{"x": 250, "y": 200}],
        "center_latitude": 35.6895,
        "map_scale": 0.05,
        "spacing_interval": 0.3
    }

    # APIエンドポイントにPOSTリクエストを送信
    url = "http://localhost:8001/segment_click"  # ポート8001に変更

    try:
        print("APIリクエストを送信中...")
        response = requests.post(url, json=test_data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print("✅ APIリクエスト成功!")
            print(f"屋根面積: {result.get('roof_area', 0):.2f} m²")
            print(f"有効面積: {result.get('effective_area', 0):.2f} m²")
            print(f"最適パネル: {result.get('best_panel', 'N/A')}")
            print(f"最大配置数: {result.get('max_count', 0)} 枚")

            # パネル詳細を表示
            panels = result.get('panels', {})
            for panel_name, panel_info in panels.items():
                print(f"\n{panel_name}:")
                print(f"  配置数: {panel_info.get('count_sim', 0)} 枚")
                print(f"  配置方向: {panel_info.get('orientation', 'N/A')}")

            # 可視化画像があれば保存
            if 'visualization_b64' in result:
                save_visualization(result['visualization_b64'])

        else:
            print(f"❌ APIエラー: {response.status_code}")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("❌ 接続エラー: APIサーバーが起動していません")
        print("先に 'python api_integration.py' でサーバーを起動してください")
    except Exception as e:
        print(f"❌ エラー: {e}")

def test_roof_segments_processing():
    """屋根セグメント処理をテスト"""
    print("=== 屋根セグメント処理テスト ===\n")

    # 複数セグメントのテストデータを作成
    test_mask1 = create_test_mask()
    test_mask2 = create_test_mask()

    # 2つ目のマスクを少し変更
    test_mask2 = cv2.resize(test_mask2, (300, 200))

    segments_data = {
        "segments": [
            {
                "label": "roof",
                "mask_base64": mask_to_base64(test_mask1),
                "center": {"x": 250, "y": 200}
            },
            {
                "label": "roof",
                "mask_base64": mask_to_base64(test_mask2),
                "center": {"x": 150, "y": 100}
            }
        ],
        "center_latitude": 35.6895,
        "map_scale": 0.05,
        "spacing_interval": 0.3
    }

    # APIエンドポイントにPOSTリクエストを送信
    url = "http://localhost:8001/process_roof_segments"

    try:
        print("セグメント処理リクエストを送信中...")
        response = requests.post(url, json=segments_data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print("✅ セグメント処理成功!")
            print(f"総セグメント数: {result.get('total_segments', 0)}")
            print(f"総パネル数: {result.get('total_panels', 0)} 枚")

            best_segment = result.get('best_segment', {})
            print(f"最適セグメント: {best_segment.get('best_panel', 'N/A')}")
            print(f"最大配置数: {best_segment.get('max_count', 0)} 枚")

            # 可視化画像があれば保存
            if 'visualization_b64' in result:
                save_visualization(result['visualization_b64'], 'test_segments_result.png')

        else:
            print(f"❌ セグメント処理エラー: {response.status_code}")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("❌ 接続エラー: APIサーバーが起動していません")
    except Exception as e:
        print(f"❌ エラー: {e}")

def save_visualization(b64_data, filename='test_result_visualization.png'):
    """可視化画像を保存"""
    try:
        # Base64データから画像部分を抽出
        img_data = b64_data.split(',')[1]
        img_bytes = base64.b64decode(img_data)

        # ファイルに保存
        with open(filename, 'wb') as f:
            f.write(img_bytes)

        print(f"✅ 可視化画像を保存: {filename}")

    except Exception as e:
        print(f"❌ 可視化画像の保存エラー: {e}")

def test_health_check():
    """ヘルスチェックをテスト"""
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)  # ポート8001に変更
        if response.status_code == 200:
            print("✅ ヘルスチェック成功")
            print(response.json())
        else:
            print(f"❌ ヘルスチェック失敗: {response.status_code}")
    except Exception as e:
        print(f"❌ ヘルスチェックエラー: {e}")

def create_sample_request_file():
    """サンプルリクエストファイルを作成"""
    test_mask = create_test_mask()
    mask_b64 = mask_to_base64(test_mask)
    
    sample_request = {
        "mask": mask_b64,
        "centers": [
            {"x": 123, "y": 456},
            {"x": 789, "y": 101}
        ],
        "center_latitude": 35.6895,
        "map_scale": 0.05,
        "spacing_interval": 0.3
    }
    
    with open('sample_request.json', 'w', encoding='utf-8') as f:
        json.dump(sample_request, f, indent=2, ensure_ascii=False)
    
    print("✅ サンプルリクエストファイルを作成: sample_request.json")

def main():
    print("太陽光パネル計算API統合テスト")
    print("=" * 40)

    while True:
        print("\n選択してください:")
        print("1. ヘルスチェック")
        print("2. 基本API統合テスト")
        print("3. 屋根セグメント処理テスト")
        print("4. サンプルリクエストファイル作成")
        print("5. 統合クライアントテスト")
        print("6. 終了")

        choice = input("\n選択 (1-6): ").strip()

        if choice == "1":
            test_health_check()
        elif choice == "2":
            test_api_integration()
        elif choice == "3":
            test_roof_segments_processing()
        elif choice == "4":
            create_sample_request_file()
        elif choice == "5":
            print("統合クライアントを起動中...")
            try:
                import subprocess
                subprocess.run(["python", "roof_detection_client.py"])
            except FileNotFoundError:
                print("❌ roof_detection_client.py が見つかりません")
        elif choice == "6":
            print("テスト終了")
            break
        else:
            print("無効な選択です")

if __name__ == "__main__":
    main()
