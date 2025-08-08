#!/usr/bin/env python3
"""
統合システム起動スクリプト
Integration system startup script
"""

import subprocess
import sys
import os
import time

def install_dependencies():
    """必要な依存関係をインストール"""
    print("依存関係をインストール中...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "requests"])
        print("✅ 依存関係のインストール完了")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依存関係のインストール失敗: {e}")
        return False

def check_dependencies():
    """依存関係をチェック"""
    required_packages = ['flask', 'requests', 'cv2', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def start_api_server():
    """APIサーバーを起動"""
    print("太陽光パネル計算APIサーバーを起動中...")
    print("太陽光パネル計算API: http://localhost:8001")
    print("屋根検出システム: http://localhost:8000 (別途起動が必要)")
    print("終了するには Ctrl+C を押してください")
    print("-" * 50)

    try:
        # 環境変数でポートを設定
        os.environ['FLASK_RUN_PORT'] = '8001'
        # api_integration.pyを実行
        subprocess.run([sys.executable, "api_integration.py"])
    except KeyboardInterrupt:
        print("\n✅ サーバーを停止しました")
    except FileNotFoundError:
        print("❌ api_integration.py が見つかりません")
    except Exception as e:
        print(f"❌ サーバー起動エラー: {e}")

def main():
    print("=" * 60)
    print("太陽光パネル計算システム統合 / Solar Panel Calculation Integration")
    print("=" * 60)
    
    # 依存関係をチェック
    missing = check_dependencies()
    if missing:
        print(f"不足している依存関係: {missing}")
        if input("インストールしますか? (y/n): ").lower() == 'y':
            if not install_dependencies():
                print("依存関係のインストールに失敗しました。手動でインストールしてください:")
                print("pip install flask requests")
                return
        else:
            print("依存関係をインストールしてから再実行してください。")
            return
    
    print("\n選択してください:")
    print("1. APIサーバーを起動")
    print("2. テストを実行")
    print("3. 統合ガイドを表示")
    print("4. 終了")
    
    choice = input("\n選択 (1-4): ").strip()
    
    if choice == "1":
        start_api_server()
    elif choice == "2":
        print("テストスクリプトを実行中...")
        try:
            subprocess.run([sys.executable, "test_integration.py"])
        except FileNotFoundError:
            print("❌ test_integration.py が見つかりません")
    elif choice == "3":
        if os.path.exists("integration_guide.md"):
            print("統合ガイド: integration_guide.md を参照してください")
        else:
            print("❌ integration_guide.md が見つかりません")
    elif choice == "4":
        print("終了します")
    else:
        print("無効な選択です")

if __name__ == "__main__":
    main()
