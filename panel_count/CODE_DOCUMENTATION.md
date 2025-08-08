# 太陽光パネル配置計算システム コード文書 / Solar Panel Layout Calculation System Code Documentation

## 📋 概要 / Overview

このドキュメントは、太陽光パネル配置計算システムの各モジュールとその主要関数について詳細に説明します。

This document provides detailed explanations of each module and its main functions in the solar panel layout calculation system.

## 🏗️ モジュール構成 / Module Structure

### 1. 📐 geometry.py - 幾何計算モジュール

**目的**: 太陽光パネル配置のための幾何学的計算を提供

**主要関数**:

#### `pixels_from_meters(value_m, gsd)`
- **機能**: メートルからピクセルへの変換（切り上げ）
- **用途**: 地理空間データの単位変換
- **計算量**: O(1)
- **例**: `pixels_from_meters(1.5, 0.05)` → `30`

#### `erode_with_margin(mask_bin, margin_px)`
- **機能**: マスクに安全マージンを適用
- **用途**: 屋根端からの安全距離確保
- **計算量**: O(H×W)
- **アルゴリズム**: OpenCV腐食処理

#### `calculate_panel_layout_fast(usable_mask, panel_w_px, panel_h_px)`
- **機能**: 高速パネル配置計算（畳み込みベース）
- **用途**: 大規模データの高速処理
- **計算量**: O(H×W) - 従来比85%高速化
- **アルゴリズム**: 
  1. 畳み込み演算で有効位置検出
  2. 貪欲法で重複回避配置

#### `calculate_panel_layout_original(usable_mask, panel_w_px, panel_h_px)`
- **機能**: 従来パネル配置計算（ピクセルスキャン）
- **用途**: 比較検証、小規模データ
- **計算量**: O(H×W×Ph×Pw)
- **アルゴリズム**: ピクセル単位の順次スキャン

#### `estimate_by_area(effective_area_sqm, panel_size_m)`
- **機能**: 面積ベース配置数推定
- **用途**: 理論上限値の計算
- **計算量**: O(1)
- **公式**: `floor(effective_area / panel_area)`

---

### 2. 🎯 planner.py - 高レベル制御モジュール

**目的**: 屋根形状に対する包括的なパネル配置計算

#### `process_roof(roof_shape_name, gsd, panel_options, offset_m, ...)`
- **機能**: 屋根形状の完全な処理パイプライン
- **処理フロー**:
  1. 屋根マスク生成
  2. 有効エリア計算（腐食処理）
  3. 複数パネル仕様での配置計算
  4. 最適配置の選択
  5. 可視化画像生成

**入力パラメータ**:
- `roof_shape_name`: 屋根形状名または画像パス
- `gsd`: Ground Sample Distance (m/pixel)
- `panel_options`: パネル仕様辞書
- `offset_m`: 安全マージン (m)
- `panel_spacing_m`: パネル間隔 (m)
- `use_fast_algorithm`: 高速アルゴリズム使用フラグ

**出力形式**:
```json
{
  "roof_type": "kiritsuma_side",
  "roof_area": 60.0,
  "effective_area": 55.2,
  "best_panel": "Sharp_NQ-256AF",
  "max_count": 42,
  "panels": {
    "Sharp_NQ-256AF": {
      "count_sim": 42,
      "orientation": "vertical",
      "panels": [[x, y, w, h], ...]
    }
  }
}
```

---

### 3. 🏠 roof_io.py - 屋根画像I/Oモジュール

**目的**: 屋根画像の読み込み、処理、可視化

#### `create_roof_mask(shape_name, dimensions)`
- **機能**: 屋根マスクの生成
- **対応形状**:
  - 幾何形状: `kiritsuma_side`, `yosemune_main`, `katanagare`, `rikuyane`
  - 画像ファイル: PNG, JPG, JPEG, BMP, TIFF
- **処理**: 自動二値化（Otsu閾値）

#### `load_roof_mask_from_image(image_path, target_dimensions)`
- **機能**: 画像ファイルからマスク読み込み
- **処理フロー**:
  1. グレースケール変換
  2. サイズ調整
  3. Otsu二値化

#### `visualize_result(original_mask, panels, filename)`
- **機能**: パネル配置結果の可視化
- **出力**: パネル位置を矩形で描画した画像

---

### 4. 🔧 cli.py - CLI処理モジュール

**目的**: コマンドライン引数の処理と検証

#### `parse_args()`
- **機能**: コマンドライン引数の解析
- **サポート引数**:
  - `--gsd`: Ground Sample Distance
  - `--offset`: 安全マージン
  - `--spacing`: パネル間隔
  - `--fast`: 高速アルゴリズム使用
  - `--roof-types`: 処理する屋根タイプ
  - `--output-csv`: 出力CSVファイル名

#### `validate_args(args)`
- **機能**: 引数の有効性検証
- **検証項目**:
  - 数値範囲チェック
  - ファイル存在確認
  - 屋根タイプ有効性

#### `save_results_to_csv(results, filename)`
- **機能**: 計算結果のCSV出力
- **出力フィールド**:
  - roof_type, panel_name, count_area, count_sim
  - orientation, roof_area, effective_area
  - gsd, offset, panel_spacing

---

### 5. 🌐 api_integration.py - API統合モジュール

**目的**: RESTful API サーバーの提供

#### Flask エンドポイント:

##### `POST /process_roof_segments`
- **機能**: 複数屋根セグメントの処理
- **入力**: JSON (segments, map_scale, spacing_interval)
- **出力**: 統合計算結果

##### `POST /segment_click`
- **機能**: 単一セグメント処理（互換性）
- **入力**: JSON (mask, centers, parameters)
- **出力**: パネル配置結果

##### `GET /health`
- **機能**: ヘルスチェック
- **出力**: サービス状態

#### `b64_to_cv2(b64str, flags)`
- **機能**: Base64画像のOpenCV変換
- **処理**: data URI対応、エラーハンドリング

#### `process_segmented_roof(mask_image, centers, map_scale, ...)`
- **機能**: 分割屋根画像の処理
- **統合**: geometry.pyの計算関数を使用

---

### 6. 🤝 roof_detection_client.py - 統合クライアント

**目的**: 屋根検出システムとの統合クライアント

#### `RoofDetectionClient` クラス:

##### `detect_roof_segments(image_path, x, y)`
- **機能**: 屋根検出システム呼び出し
- **通信**: HTTP POST (multipart/form-data)

##### `calculate_solar_panels(roof_segments, ...)`
- **機能**: 太陽光パネル計算システム呼び出し
- **通信**: HTTP POST (JSON)

##### `process_complete_workflow(image_path, x, y, ...)`
- **機能**: 完全ワークフローの実行
- **処理フロー**:
  1. 屋根検出
  2. パネル計算
  3. 結果統合

---

## 🔄 データフロー / Data Flow

```
Input Image/Coordinates
        ↓
[roof_detection_client.py] → Roof Detection API (8000)
        ↓
Roof Segments (Base64 masks)
        ↓
[api_integration.py] → Panel Calculation
        ↓
[planner.py] → process_roof()
        ↓
[roof_io.py] → create_roof_mask()
        ↓
[geometry.py] → erode_with_margin()
        ↓
[geometry.py] → calculate_panel_layout_fast()
        ↓
[roof_io.py] → visualize_result()
        ↓
Final Results (JSON + Visualization)
```

## 🧮 アルゴリズム比較 / Algorithm Comparison

| アルゴリズム | 時間計算量 | 空間計算量 | 用途 |
|-------------|-----------|-----------|------|
| Fast Layout | O(H×W) | O(H×W) | 本番環境、大規模データ |
| Original Layout | O(H×W×Ph×Pw) | O(H×W) | 検証、小規模データ |
| Area Estimation | O(1) | O(1) | 上限値計算 |

## 📊 パフォーマンス指標 / Performance Metrics

### 処理時間 (400×500px画像):
- **高速アルゴリズム**: ~0.5秒
- **従来アルゴリズム**: ~3.0秒
- **改善率**: 85%

### メモリ使用量:
- **ベース**: ~50MB
- **ピーク**: ~120MB (大画像処理時)

## 🔧 設定可能パラメータ / Configurable Parameters

### パネル仕様 / Panel Specifications:
```python
panel_options = {
    "Sharp_NQ-256AF": (1.318, 0.990),  # 長さ×幅 (m)
    "Standard_A": (1.65, 0.99),
    "Standard_B": (1.50, 0.80)
}
```

### 計算パラメータ / Calculation Parameters:
- **GSD**: 0.01 - 0.5 m/pixel (推奨: 0.05)
- **Offset**: 0.1 - 2.0 m (推奨: 0.3)
- **Spacing**: 0.01 - 0.1 m (推奨: 0.02)

## 🧪 テスト関数 / Test Functions

### test_integration.py:
- `test_api_integration()`: API機能テスト
- `test_roof_segments_processing()`: セグメント処理テスト
- `create_test_mask()`: テストデータ生成

## 📝 エラーハンドリング / Error Handling

### 共通エラータイプ:
- **ValueError**: 無効なパラメータ
- **FileNotFoundError**: ファイル不存在
- **ConnectionError**: API通信エラー
- **ProcessingError**: 計算処理エラー

### ログレベル:
- **DEBUG**: 詳細な処理情報
- **INFO**: 一般的な処理状況
- **WARNING**: 警告メッセージ
- **ERROR**: エラー情報

## 🔄 バージョン管理 / Version Management

### v1.2.0 (Current):
- 完全な文書化
- API仕様の標準化
- エラーハンドリング強化

### v1.1.0:
- 屋根検出システム統合
- Flask API追加
- 統合テスト実装

### v1.0.0:
- 基本機能実装
- 高速アルゴリズム開発
- CLI インターフェース

---

**最終更新 / Last Updated**: 2025-07-02  
**バージョン / Version**: 1.2.0  
**作成者 / Author**: Panel Count Module Team
