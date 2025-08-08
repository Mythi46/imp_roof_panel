#!/usr/bin/env python3
"""
屋根検出分割システムクライアント
Client for roof detection segmentation system
"""

import requests
import json
import base64
import cv2
import numpy as np
import os
from typing import Dict, List, Optional

class RoofDetectionClient:
    """屋根検出分割システムのクライアント"""
    
    def __init__(self, roof_api_url: str = "http://localhost:8000", 
                 panel_api_url: str = "http://localhost:8001"):
        """
        Args:
            roof_api_url: 屋根検出システムのURL
            panel_api_url: 太陽光パネル計算システムのURL
        """
        self.roof_api_url = roof_api_url.rstrip('/')
        self.panel_api_url = panel_api_url.rstrip('/')
    
    def detect_roof_segments(self, image_path: str, x: int, y: int) -> Optional[Dict]:
        """
        屋根検出システムを呼び出し (新API使用)
        
        Args:
            image_path: 衛星画像のパス
            x, y: クリック座標
            
        Returns:
            検出結果の辞書
        """
        try:
            # 画像ファイルを読み込み
            with open(image_path, 'rb') as f:
                files = {'image': (os.path.basename(image_path), f, 'image/jpeg')}
                data = {'x': x, 'y': y}
                
                # 屋根検出システムにPOSTリクエスト
                response = requests.post(
                    f"{self.roof_api_url}/segment",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 屋根検出成功: {len(result.get('segments', []))} セグメント")
                return result
            else:
                print(f"❌ 屋根検出エラー: {response.status_code}")
                print(response.text)
                return None
                
        except Exception as e:
            print(f"❌ 屋根検出システム呼び出しエラー: {e}")
            return None
    
    def calculate_solar_panels(self, roof_segments: Dict, 
                             center_latitude: float = 35.6895,
                             map_scale: float = 0.05,
                             spacing_interval: float = 0.3) -> Optional[Dict]:
        """
        太陽光パネル配置を計算
        
        Args:
            roof_segments: 屋根検出結果
            center_latitude: 中心緯度
            map_scale: 地図スケール (m/pixel)
            spacing_interval: 間隔 (meters)
            
        Returns:
            計算結果の辞書
        """
        try:
            # リクエストデータを準備
            request_data = {
                "segments": roof_segments.get('segments', []),
                "center_latitude": center_latitude,
                "map_scale": map_scale,
                "spacing_interval": spacing_interval
            }
            
            # 太陽光パネル計算システムにPOSTリクエスト
            response = requests.post(
                f"{self.panel_api_url}/calculate_panels",
                json=request_data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ パネル計算成功: 合計 {result.get('total_panels', 0)} 枚")
                return result
            else:
                print(f"❌ パネル計算エラー: {response.status_code}")
                print(response.text)
                return None
                
        except Exception as e:
            print(f"❌ パネル計算システム呼び出しエラー: {e}")
            return None
    
    def process_complete_workflow(self, image_path: str, x: int, y: int,
                                center_latitude: float = 35.6895,
                                map_scale: float = 0.05,
                                spacing_interval: float = 0.3) -> Optional[Dict]:
        """
        完全なワークフローを実行
        
        Args:
            image_path: 衛星画像のパス
            x, y: クリック座標
            center_latitude: 中心緯度
            map_scale: 地図スケール (m/pixel)
            spacing_interval: 間隔 (meters)
            
        Returns:
            最終結果の辞書
        """
        print("=" * 60)
        print("完全ワークフロー実行開始")
        print("=" * 60)
        
        # Step 1: 屋根検出
        print("\n🔍 Step 1: 屋根検出分割")
        roof_result = self.detect_roof_segments(image_path, x, y)
        
        if not roof_result:
            print("❌ 屋根検出に失敗しました")
            return None
        
        # Step 2: 太陽光パネル計算
        print("\n☀️ Step 2: 太陽光パネル配置計算")
        panel_result = self.calculate_solar_panels(
            roof_result, center_latitude, map_scale, spacing_interval
        )
        
        if not panel_result:
            print("❌ パネル計算に失敗しました")
            return None
        
        # Step 3: 結果統合
        print("\n📊 Step 3: 結果統合")
        final_result = {
            "workflow_success": True,
            "roof_detection": roof_result,
            "panel_calculation": panel_result,
            "summary": {
                "total_segments": len(roof_result.get('segments', [])),
                "total_panels": panel_result.get('total_panels', 0),
                "best_panel_type": panel_result.get('best_segment', {}).get('best_panel'),
                "max_panels_per_segment": panel_result.get('best_segment', {}).get('max_count', 0)
            }
        }
        
        print("✅ 完全ワークフロー完了!")
        return final_result
    
    def save_results(self, results: Dict, output_dir: str = "results"):
        """結果を保存"""
        os.makedirs(output_dir, exist_ok=True)
        
        # JSON結果を保存
        with open(f"{output_dir}/workflow_results.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # 可視化画像を保存
        panel_calc = results.get('panel_calculation', {})
        if 'visualization_b64' in panel_calc:
            try:
                img_data = panel_calc['visualization_b64'].split(',')[1]
                img_bytes = base64.b64decode(img_data)
                
                with open(f"{output_dir}/panel_layout_visualization.png", 'wb') as f:
                    f.write(img_bytes)
                
                print(f"✅ 可視化画像を保存: {output_dir}/panel_layout_visualization.png")
                
            except Exception as e:
                print(f"❌ 可視化画像の保存エラー: {e}")
        
        print(f"✅ 結果を保存: {output_dir}/workflow_results.json")

def main():
    """メイン関数"""
    print("屋根検出 → 太陽光パネル配置 統合クライアント")
    print("=" * 50)
    
    client = RoofDetectionClient()
    
    while True:
        print("\n選択してください:")
        print("1. 完全ワークフローを実行")
        print("2. 屋根検出のみ実行")
        print("3. パネル計算のみ実行 (JSONファイルから)")
        print("4. 終了")
        
        choice = input("\n選択 (1-4): ").strip()
        
        if choice == "1":
            image_path = input("画像ファイルパス: ").strip()
            if not os.path.exists(image_path):
                print("❌ ファイルが見つかりません")
                continue
            
            try:
                x = int(input("X座標: "))
                y = int(input("Y座標: "))
                center_lat = float(input("中心緯度 (デフォルト: 35.6895): ") or "35.6895")
                map_scale = float(input("地図スケール (デフォルト: 0.05): ") or "0.05")
                spacing = float(input("間隔 (デフォルト: 0.3): ") or "0.3")
                
                results = client.process_complete_workflow(
                    image_path, x, y, center_lat, map_scale, spacing
                )
                
                if results:
                    client.save_results(results)
                    
            except ValueError:
                print("❌ 無効な数値です")
        
        elif choice == "2":
            image_path = input("画像ファイルパス: ").strip()
            if not os.path.exists(image_path):
                print("❌ ファイルが見つかりません")
                continue
            
            try:
                x = int(input("X座標: "))
                y = int(input("Y座標: "))
                
                result = client.detect_roof_segments(image_path, x, y)
                if result:
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                    
            except ValueError:
                print("❌ 無効な数値です")
        
        elif choice == "3":
            json_path = input("屋根検出結果JSONファイルパス: ").strip()
            if not os.path.exists(json_path):
                print("❌ ファイルが見つかりません")
                continue
            
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    roof_data = json.load(f)
                
                center_lat = float(input("中心緯度 (デフォルト: 35.6895): ") or "35.6895")
                map_scale = float(input("地図スケール (デフォルト: 0.05): ") or "0.05")
                spacing = float(input("間隔 (デフォルト: 0.3): ") or "0.3")
                
                result = client.calculate_solar_panels(
                    roof_data, center_lat, map_scale, spacing
                )
                
                if result:
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                    
            except (ValueError, json.JSONDecodeError) as e:
                print(f"❌ エラー: {e}")
        
        elif choice == "4":
            print("終了します")
            break
        else:
            print("無効な選択です")

if __name__ == "__main__":
    main()
