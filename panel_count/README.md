# 太陽光パネル配置計算システム / Solar Panel Layout Calculation System

## ⚠️ 架构更新通知 / Architecture Update Notice

**重要**: 本系统已进行架构重构，移除了重复的屋顶检测系统。
**Important**: This system has undergone architectural refactoring, removing duplicate roof detection systems.

- 屋顶检测服务: `roof/` (端口 8000)
- 太阳能板计算服务: `panel_count/` (端口 8001)

详细信息请参考 `ARCHITECTURE_REFACTOR_PLAN.md`

---

## 🎯 概要 / Overview

### 日本語
屋根画像から太陽光パネルの最適配置を計算するシステムです。幾何学的形状と実際の屋根画像の両方に対応し、高精度な配置シミュレーションを提供します。

### English
A system for calculating optimal solar panel layouts from roof images. It supports both geometric shapes and real roof images, providing high-precision placement simulations.

## ✨ 主要機能 / Key Features

- **🏠 多様な屋根形状対応**: 切妻、寄棟、片流れ、陸屋根等
- **📸 実画像処理**: 実際の屋根写真からの自動マスク生成
- **⚡ 高速計算**: 畳み込みベースの最適化アルゴリズム
- **📊 多規格対応**: 複数のパネルサイズでの比較分析
- **🎨 可視化出力**: 配置結果の画像生成とCSVデータ出力
- **🔌 API統合**: RESTful APIによる他システムとの連携

## 🚀 クイックスタート / Quick Start

### 基本使用 / Basic Usage

```bash
# 依存関係のインストール
pip install -r requirements.txt

# 基本計算の実行
python main.py --gsd 0.05 --offset 0.3

# API サーバーの起動
python api_integration.py
```

### Docker使用 / Docker Usage

```bash
# Dockerコンテナでの実行
docker-compose up -d

# 統合システムの起動
docker-compose -f docker-compose.integration.yml up -d
```

## 📁 プロジェクト構造 / Project Structure

```
panel_count/
├── 📄 main.py                    # メインエントリーポイント
├── 🔧 cli.py                     # CLI処理・引数検証
├── 🏠 roof_io.py                 # 屋根画像I/O・可視化
├── 📐 geometry.py                # 幾何計算・アルゴリズム
├── 🎯 planner.py                 # 高レベル制御・計算統合
├── 🌐 api_integration.py         # Flask API サーバー
├── 🤝 roof_detection_client.py   # 統合クライアント
├── 🧪 test_integration.py        # 統合テスト
├── 📋 requirements.txt           # 依存関係
├── 📚 README.md                  # このファイル
├── 📖 INTEGRATION_README.md      # 統合ガイド
├── 🚀 DEPLOYMENT_GUIDE.md        # 部署ガイド
└── 📊 results/                   # 計算結果・レポート
    ├── csv_data/                 # CSV出力データ
    ├── visualizations/           # 可視化画像
    ├── reports/                  # 技術レポート
    └── logs/                     # ログファイル
```

## 🔧 システム要件 / System Requirements

### 最小要件 / Minimum Requirements
- Python 3.8+
- RAM: 4GB
- Storage: 1GB

### 推奨要件 / Recommended Requirements
- Python 3.9+
- RAM: 8GB
- Storage: 5GB
- GPU: CUDA対応 (オプション)

### 依存関係 / Dependencies
```
opencv-python>=4.5.0
numpy>=1.21.0
scipy>=1.7.0
flask>=2.0.0
requests>=2.25.0
```

## 📖 使用方法 / Usage

### 1. コマンドライン使用 / Command Line Usage

```bash
# 基本的な計算
python main.py

# カスタムパラメータでの計算
python main.py --gsd 0.03 --offset 0.5 --spacing 0.05

# 特定の屋根タイプのみ計算
python main.py --roof-types kiritsuma_side katanagare

# 画像ファイルからの計算
python main.py --roof-types sample_roof.png

# 高速アルゴリズムの使用
python main.py --fast

# 詳細ログの出力
python main.py --log-level DEBUG
```

### 2. API使用 / API Usage

#### サーバー起動 / Start Server
```bash
python api_integration.py
```

#### リクエスト例 / Request Example
```python
import requests

data = {
    "mask": "data:image/png;base64,iVBORw0KGgo...",
    "centers": [{"x": 250, "y": 200}],
    "center_latitude": 35.6895,
    "map_scale": 0.05,
    "spacing_interval": 0.3
}

response = requests.post("http://localhost:8001/segment_click", json=data)
result = response.json()
```

### 3. 統合クライアント使用 / Integrated Client Usage

```bash
# 統合クライアントの起動
python roof_detection_client.py

# 完全ワークフローの実行
# 1. 完全ワークフローを実行 を選択
# 2. 画像ファイルパスと座標を入力
# 3. 結果の確認
```

## 🏗️ アーキテクチャ / Architecture

### システム構成 / System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Panel Count System                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   CLI Tool  │    │  Flask API  │    │Integration  │     │
│  │   main.py   │    │api_integration│    │   Client    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                   │                   │          │
│         └───────────────────┼───────────────────┘          │
│                             │                              │
│              ┌─────────────────────────────┐               │
│              │        Core Modules         │               │
│              │                             │               │
│              │  ┌─────────┐ ┌─────────┐   │               │
│              │  │planner  │ │geometry │   │               │
│              │  │  .py    │ │  .py    │   │               │
│              │  └─────────┘ └─────────┘   │               │
│              │                             │               │
│              │  ┌─────────┐ ┌─────────┐   │               │
│              │  │roof_io  │ │  cli    │   │               │
│              │  │  .py    │ │  .py    │   │               │
│              │  └─────────┘ └─────────┘   │               │
│              └─────────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

### データフロー / Data Flow

```
Input Image/Shape → Roof Mask → Erosion → Panel Layout → Visualization
      ↓               ↓           ↓           ↓            ↓
   roof_io.py    roof_io.py   geometry.py  geometry.py  roof_io.py
```

## 🧮 アルゴリズム / Algorithms

### 高速配置アルゴリズム / Fast Placement Algorithm

```python
# 畳み込みによる有効位置検出
hit_map = convolve2d(mask_bin, window[::-1, ::-1], mode='valid')
valid = (hit_map == panel_h_px * panel_w_px)

# 貪欲法による重複回避配置
for y, x in zip(*np.where(valid)):
    if not np.any(taken_mask[y:y+panel_h_px, x:x+panel_w_px]):
        panels.append((x, y, panel_w_px, panel_h_px))
        taken_mask[y:y+panel_h_px, x:x+panel_w_px] = True
```

### パフォーマンス比較 / Performance Comparison

| 指標 | 従来手法 | 改良手法 | 改善率 |
|------|----------|----------|--------|
| 計算時間 | O(H×W×Ph×Pw) | O(H×W) | ~85% |
| メモリ使用量 | 高 | 中 | ~40% |
| 精度 | 100% | 100% | 維持 |

## 🎛️ 設定 / Configuration

### パネル仕様 / Panel Specifications

```python
panel_options = {
    "Sharp_NQ-256AF": (1.318, 0.990),  # 長さ×幅 (m)
    "Standard_A": (1.65, 0.99),
    "Standard_B": (1.50, 0.80)
}
```

### 計算パラメータ / Calculation Parameters

| パラメータ | デフォルト値 | 説明 |
|------------|-------------|------|
| `gsd` | 0.05 | Ground Sample Distance (m/pixel) |
| `offset` | 0.3 | 屋根端からのオフセット (m) |
| `spacing` | 0.02 | パネル間の間隔 (m) |

## 🧪 テスト / Testing

### テストの実行 / Running Tests

```bash
# 統合テストの実行
python test_integration.py

# 特定テストの実行
python -m pytest tests/ -v

# カバレッジレポートの生成
python -m pytest --cov=. tests/
```

### テストカバレッジ / Test Coverage

- ✅ 基本API機能テスト
- ✅ 屋根セグメント処理テスト
- ✅ 統合ワークフローテスト
- ✅ エラーハンドリングテスト
- ✅ パフォーマンステスト

## 📊 出力形式 / Output Formats

### CSV出力 / CSV Output

```csv
roof_type,panel_name,count_area,count_sim,orientation,roof_area,effective_area
kiritsuma_side,Sharp_NQ-256AF,45,42,vertical,60.0,55.2
```

### JSON出力 / JSON Output

```json
{
  "success": true,
  "roof_area": 60.0,
  "effective_area": 55.2,
  "best_panel": "Sharp_NQ-256AF",
  "max_count": 42,
  "panels": {
    "Sharp_NQ-256AF": {
      "count_sim": 42,
      "orientation": "vertical"
    }
  }
}
```

## 🔌 API リファレンス / API Reference

### エンドポイント / Endpoints

#### `POST /process_roof_segments`
屋根セグメント処理

**リクエスト:**
```json
{
  "segments": [...],
  "center_latitude": 35.6895,
  "map_scale": 0.05,
  "spacing_interval": 0.3
}
```

**レスポンス:**
```json
{
  "success": true,
  "total_segments": 3,
  "total_panels": 125,
  "best_segment": {...}
}
```

#### `POST /segment_click`
単一セグメント処理 (互換性)

#### `GET /health`
ヘルスチェック

## 📚 ドキュメント / Documentation

### 📋 完全文書一覧 / Complete Documentation
- 📚 [文書インデックス](DOCUMENTATION_INDEX.md) - 全文書の概要と案内
- 🔌 [API リファレンス](API_REFERENCE.md) - RESTful API 詳細仕様
- 💻 [コード文書](CODE_DOCUMENTATION.md) - モジュール・関数詳細
- 🚨 [トラブルシューティング](TROUBLESHOOTING.md) - 問題解決ガイド
- 🔧 [メンテナンスガイド](MAINTENANCE_GUIDE.md) - 運用・保守手順

### 🤝 統合・部署文書 / Integration & Deployment
- 📖 [統合ガイド](INTEGRATION_README.md) - 屋根検出システム統合
- 🚀 [部署ガイド](DEPLOYMENT_GUIDE.md) - Docker・本番環境部署
- 📋 [統合詳細](integration_guide.md) - API統合手順

### 📊 技術レポート / Technical Reports
- 📊 [技術レポート](results/reports/technical_report_ja_en.md) - アルゴリズム・性能分析
- 📈 [エグゼクティブサマリー](results/reports/executive_summary_ja_en.md) - プロジェクト概要
- 🧪 [テストガイド](test_integration.py) - 統合テスト手順

## 🆕 更新履歴 / Changelog

### v1.2.0 (2025-07-02)
- 📚 技術文档全面更新
- 🔧 API文档完善
- 📖 使用指南优化

### v1.1.0 (2025-06-27)
- 🤝 屋根検出システムとの統合完了
- 🌐 Flask API サーバー追加
- 🧪 統合テストスイート追加

### v1.0.0 (2025-06-20)
- 🎯 初期リリース
- ⚡ 高速配置アルゴリズム実装
- 📊 可視化機能追加

## 📞 サポート / Support

- 📧 Email: support@example.com
- 📱 Issues: GitHub Issues
- 📖 Documentation: このREADME

---

**開発チーム / Development Team**: Panel Count Module Team  
**最終更新 / Last Updated**: 2025-07-02  
**バージョン / Version**: v1.2.0
