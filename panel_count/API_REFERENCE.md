# 太陽光パネル計算システム API リファレンス / Solar Panel Calculation System API Reference

## 📋 概要 / Overview

### 日本語
太陽光パネル配置計算システムのRESTful API仕様書です。屋根検出分割システムとの統合および独立した使用の両方に対応しています。

**バージョン**: 2.0.0
**最終更新**: 2025年7月25日
**主要エンドポイント**: `/calculate_panels`

### English
RESTful API specification for the solar panel layout calculation system. Supports both integration with roof detection segmentation systems and standalone usage.

**Version**: 2.0.0
**Last Updated**: July 25, 2025
**Primary Endpoint**: `/calculate_panels`

## 🌐 ベースURL / Base URL

```
http://localhost:8001
```

## 🔐 認証 / Authentication

現在のバージョンでは認証は不要です。本番環境では適切な認証機構の実装を推奨します。

## 📊 共通レスポンス形式 / Common Response Format

### 成功レスポンス / Success Response
```json
{
  "success": true,
  "data": {...},
  "message": "処理が正常に完了しました"
}
```

### エラーレスポンス / Error Response
```json
{
  "success": false,
  "error": "error_code",
  "message": "エラーの詳細説明",
  "details": {...}
}
```

## 🔌 エンドポイント / Endpoints

### 1. ヘルスチェック / Health Check

#### `GET /health`

システムの稼働状況を確認します。

**リクエスト例 / Request Example:**
```bash
curl -X GET http://localhost:8001/health
```

**レスポンス / Response:**
```json
{
  "status": "healthy",
  "service": "solar_panel_calculator",
  "version": "2.0.0",
  "api_endpoints": {
    "primary": "/calculate_panels",
    "deprecated": ["/process_roof_segments", "/segment_click"],
    "health": "/health"
  },
  "supported_input_methods": [
    "roof_mask (base64 encoded binary image)",
    "roof_shape_name (predefined shapes for testing)"
  ]
}
```

**ステータスコード / Status Codes:**
- `200 OK`: サービス正常
- `503 Service Unavailable`: サービス異常

---

### 2. 太陽光パネル配置計算 / Calculate Solar Panel Layout

#### `POST /calculate_panels`

**推奨API / Recommended API**

単一の屋根に対して太陽光パネルの最適配置を計算します。2つの入力方式をサポートしています。

**入力方式1: 屋根マスク画像 / Input Method 1: Roof Mask Image**

**リクエストボディ / Request Body:**
```json
{
  "roof_mask": "iVBORw0KGgoAAAANSUhEUgAA...",
  "gsd": 0.05,
  "panel_options": {
    "Standard_B": [1.65, 1.0]
  },
  "offset_m": 1.0,
  "panel_spacing_m": 0.02
}
```

**入力方式2: 事前定義屋根形状 / Input Method 2: Predefined Roof Shape**

**リクエストボディ / Request Body:**
```json
{
  "roof_shape_name": "rikuyane",
  "gsd": 0.05,
  "panel_options": {
    "Standard_B": [1.65, 1.0]
  },
  "offset_m": 1.0,
  "dimensions": [400, 500]
}
```

**パラメータ説明 / Parameter Description:**
- `roof_mask`: Base64エンコードされた二値屋根マスク画像
- `roof_shape_name`: 事前定義屋根形状名 ("rikuyane", "katanagare", "kiritsuma", "yosemune")
- `gsd`: 地上解像度 (m/pixel)
- `panel_options`: パネルオプション辞書 {名前: [長さ, 幅]}
- `offset_m`: 安全マージン (メートル)
- `panel_spacing_m`: パネル間隔 (メートル)
- `dimensions`: 画像サイズ [高さ, 幅] (roof_shape_name使用時のみ)

**レスポンス / Response:**
```json
{
  "success": true,
  "roof_area": 500.0,
  "effective_area": 324.0,
  "gsd": 0.05,
  "offset_m": 1.0,
  "panel_spacing_m": 0.02,
  "panels": {
    "Standard_B": {
      "panel_name": "Standard_B",
      "panel_size": [1.65, 1.0],
      "count_area": 196,
      "count_sim": 156,
      "orientation": "vertical"
    }
  },
  "best_panel": "Standard_B",
  "max_count": 156,
  "total_capacity_kw": 62.4,
  "roof_type": "rikuyane",
  "visualization_b64": "data:image/png;base64,iVBORw0KGgo..."
}
```

**ステータスコード / Status Codes:**
- `200 OK`: 計算成功
- `400 Bad Request`: 入力データエラー
- `500 Internal Server Error`: サーバーエラー

---

### 3. 屋根セグメント処理 / Process Roof Segments (DEPRECATED)

#### `POST /process_roof_segments`

**⚠️ 非推奨 / DEPRECATED**: このエンドポイントは非推奨です。`/calculate_panels` を使用してください。

複数の屋根セグメントを処理して太陽光パネルの最適配置を計算します。

**リクエストボディ / Request Body:**
```json
{
  "segments": [
    {
      "label": "roof",
      "mask_base64": "data:image/png;base64,iVBORw0KGgo...",
      "center": {"x": 250, "y": 200},
      "confidence": 0.95
    }
  ],
  "center_latitude": 35.6895,
  "map_scale": 0.05,
  "spacing_interval": 0.3,
  "panel_options": {
    "Sharp_NQ-256AF": [1.318, 0.990],
    "Standard_A": [1.65, 0.99],
    "Standard_B": [1.50, 0.80]
  }
}
```

**パラメータ説明 / Parameter Description:**

| パラメータ | 型 | 必須 | 説明 |
|------------|----|----|------|
| `segments` | Array | ✅ | 屋根セグメントの配列 |
| `segments[].label` | String | ✅ | セグメントラベル ("roof") |
| `segments[].mask_base64` | String | ✅ | Base64エンコードされたマスク画像 |
| `segments[].center` | Object | ❌ | 中心座標 {x, y} |
| `segments[].confidence` | Number | ❌ | 信頼度 (0.0-1.0) |
| `center_latitude` | Number | ❌ | 中心緯度 (デフォルト: 35.6895) |
| `map_scale` | Number | ❌ | 地図スケール m/pixel (デフォルト: 0.05) |
| `spacing_interval` | Number | ❌ | 間隔 meters (デフォルト: 0.3) |
| `panel_options` | Object | ❌ | パネル仕様 (デフォルト値使用) |

**レスポンス / Response:**
```json
{
  "success": true,
  "total_segments": 3,
  "total_panels": 125,
  "map_scale": 0.05,
  "spacing_interval": 0.3,
  "best_segment": {
    "segment_id": 0,
    "roof_area": 85.5,
    "effective_area": 78.2,
    "best_panel": "Sharp_NQ-256AF",
    "max_count": 45,
    "center": {"x": 250, "y": 200},
    "panels": {
      "Sharp_NQ-256AF": {
        "panel_name": "Sharp_NQ-256AF",
        "panel_size": [1.318, 0.990],
        "count_area": 47,
        "count_sim": 45,
        "orientation": "vertical",
        "panels": [[10, 20, 26, 66], [36, 20, 26, 66]]
      }
    }
  },
  "all_segments": [...],
  "visualization_b64": "data:image/png;base64,iVBORw0KGgo..."
}
```

**リクエスト例 / Request Example:**
```bash
curl -X POST http://localhost:8001/process_roof_segments \
  -H "Content-Type: application/json" \
  -d '{
    "segments": [
      {
        "label": "roof",
        "mask_base64": "data:image/png;base64,iVBORw0KGgo...",
        "center": {"x": 250, "y": 200}
      }
    ],
    "center_latitude": 35.6895,
    "map_scale": 0.05,
    "spacing_interval": 0.3
  }'
```

**ステータスコード / Status Codes:**
- `200 OK`: 処理成功
- `400 Bad Request`: リクエストパラメータエラー
- `500 Internal Server Error`: サーバー内部エラー

---

### 3. 単一セグメント処理 / Single Segment Processing

#### `POST /segment_click`

単一の屋根セグメントを処理します（互換性エンドポイント）。

**リクエストボディ / Request Body:**
```json
{
  "mask": "data:image/png;base64,iVBORw0KGgo...",
  "centers": [{"x": 250, "y": 200}],
  "center_latitude": 35.6895,
  "map_scale": 0.05,
  "spacing_interval": 0.3
}
```

**パラメータ説明 / Parameter Description:**

| パラメータ | 型 | 必須 | 説明 |
|------------|----|----|------|
| `mask` | String | ✅ | Base64エンコードされたマスク画像 |
| `centers` | Array | ❌ | 中心座標の配列 |
| `center_latitude` | Number | ❌ | 中心緯度 |
| `map_scale` | Number | ❌ | 地図スケール |
| `spacing_interval` | Number | ❌ | 間隔 |

**レスポンス / Response:**
```json
{
  "success": true,
  "roof_area": 85.5,
  "effective_area": 78.2,
  "map_scale": 0.05,
  "spacing_interval": 0.3,
  "centers": [{"x": 250, "y": 200}],
  "best_panel": "Sharp_NQ-256AF",
  "max_count": 45,
  "panels": {
    "Sharp_NQ-256AF": {
      "panel_name": "Sharp_NQ-256AF",
      "panel_size": [1.318, 0.990],
      "count_area": 47,
      "count_sim": 45,
      "orientation": "vertical",
      "panels": [[10, 20, 26, 66], [36, 20, 26, 66]]
    },
    "Standard_A": {...},
    "Standard_B": {...}
  },
  "visualization_b64": "data:image/png;base64,iVBORw0KGgo..."
}
```

**リクエスト例 / Request Example:**
```bash
curl -X POST http://localhost:8001/segment_click \
  -H "Content-Type: application/json" \
  -d '{
    "mask": "data:image/png;base64,iVBORw0KGgo...",
    "centers": [{"x": 250, "y": 200}],
    "center_latitude": 35.6895,
    "map_scale": 0.05,
    "spacing_interval": 0.3
  }'
```

## 📝 データ形式 / Data Formats

### Base64画像形式 / Base64 Image Format

マスク画像は以下の形式でエンコードしてください：

```
data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...
```

- **形式**: PNG推奨
- **色深度**: グレースケール (0-255)
- **マスク値**: 255=屋根エリア, 0=非屋根エリア

### パネル配置データ / Panel Placement Data

パネル配置は以下の形式で返されます：

```json
"panels": [
  [x, y, width, height],  // ピクセル座標
  [36, 20, 26, 66],
  [62, 20, 26, 66]
]
```

- `x, y`: パネル左上角の座標
- `width, height`: パネルのサイズ（ピクセル）

## ⚠️ エラーコード / Error Codes

| エラーコード | 説明 | 対処法 |
|-------------|------|--------|
| `no_data` | リクエストデータなし | JSONデータを送信してください |
| `no_segments` | セグメントデータなし | segmentsパラメータを確認してください |
| `decode_error` | Base64デコードエラー | 画像データの形式を確認してください |
| `empty_or_invalid_mask` | 空または無効なマスク | マスク画像の内容を確認してください |
| `processing_error` | 処理エラー | サーバーログを確認してください |

## 🔧 設定パラメータ / Configuration Parameters

### デフォルト値 / Default Values

```json
{
  "center_latitude": 35.6895,
  "map_scale": 0.05,
  "spacing_interval": 0.3,
  "panel_options": {
    "Sharp_NQ-256AF": [1.318, 0.990],
    "Standard_A": [1.65, 0.99],
    "Standard_B": [1.50, 0.80]
  }
}
```

### 推奨値範囲 / Recommended Value Ranges

| パラメータ | 最小値 | 最大値 | 推奨値 |
|------------|--------|--------|--------|
| `map_scale` | 0.01 | 0.5 | 0.05 |
| `spacing_interval` | 0.1 | 2.0 | 0.3 |
| `center_latitude` | -90 | 90 | 35.6895 |

## 🧪 テスト例 / Test Examples

### Python テストコード / Python Test Code

```python
import requests
import base64
import cv2
import numpy as np

# テスト用マスク画像を作成
mask = np.zeros((400, 500), dtype=np.uint8)
cv2.rectangle(mask, (50, 50), (450, 350), 255, -1)

# Base64エンコード
_, buffer = cv2.imencode('.png', mask)
mask_b64 = base64.b64encode(buffer).decode('utf-8')
mask_data_uri = f"data:image/png;base64,{mask_b64}"

# APIリクエスト
data = {
    "mask": mask_data_uri,
    "centers": [{"x": 250, "y": 200}],
    "center_latitude": 35.6895,
    "map_scale": 0.05,
    "spacing_interval": 0.3
}

response = requests.post("http://localhost:8001/segment_click", json=data)
result = response.json()

print(f"成功: {result['success']}")
print(f"最適パネル: {result['best_panel']}")
print(f"配置数: {result['max_count']} 枚")
```

### JavaScript テストコード / JavaScript Test Code

```javascript
const testAPI = async () => {
  const data = {
    mask: "data:image/png;base64,iVBORw0KGgo...",
    centers: [{x: 250, y: 200}],
    center_latitude: 35.6895,
    map_scale: 0.05,
    spacing_interval: 0.3
  };

  try {
    const response = await fetch('http://localhost:8001/segment_click', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    });

    const result = await response.json();
    console.log('結果:', result);
  } catch (error) {
    console.error('エラー:', error);
  }
};
```

## 📈 パフォーマンス / Performance

### レスポンス時間 / Response Time

| 画像サイズ | 平均処理時間 | メモリ使用量 |
|------------|-------------|-------------|
| 400x500px | ~0.5秒 | ~50MB |
| 800x1000px | ~1.2秒 | ~120MB |
| 1600x2000px | ~3.5秒 | ~300MB |

### 制限事項 / Limitations

- **最大画像サイズ**: 2000x2000px
- **最大セグメント数**: 10個
- **リクエストタイムアウト**: 60秒
- **同時接続数**: 10接続

## 🔒 セキュリティ / Security

### 推奨事項 / Recommendations

1. **HTTPS使用**: 本番環境ではHTTPS必須
2. **認証実装**: API キーまたはJWT認証
3. **レート制限**: リクエスト頻度制限
4. **入力検証**: 画像サイズ・形式の検証
5. **ログ記録**: アクセスログの記録

## 📞 サポート / Support

- **技術サポート**: [GitHub Issues](https://github.com/your-repo/issues)
- **ドキュメント**: [README.md](README.md)
- **統合ガイド**: [INTEGRATION_README.md](INTEGRATION_README.md)

---

**最終更新 / Last Updated**: 2025-07-02  
**APIバージョン / API Version**: v1.2.0
