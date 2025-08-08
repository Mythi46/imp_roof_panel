# 屋顶检测分割系统集成指南 / Roof Detection Segmentation System Integration Guide

## 概要 / Overview

### 日本語
このガイドは、屋根検出分割システムと太陽光パネル配置計算システムの統合方法を説明します。

### English
This guide explains how to integrate the roof detection segmentation system with the solar panel layout calculation system.

## システム構成 / System Architecture

```
[屋根検出分割システム] → [POST Request] → [太陽光パネル計算API] → [計算結果]
[Roof Detection System] → [POST Request] → [Solar Panel Calc API] → [Results]
```

## API仕様 / API Specification

### エンドポイント / Endpoint
```
POST http://localhost:8000/segment_click
```

### 入力パラメータ / Input Parameters

| パラメータ名 | 型 | 説明 | 例 |
|-------------|----|----|---|
| `mask` | String | Base64エンコードされた分割マスク画像 (0/255) | `data:image/png;base64,iVBORw0KGgo...` |
| `centers` | Array | 中心点座標のリスト | `[{"x":123,"y":456}, {"x":789,"y":101}]` |
| `center_latitude` | Number | 中心緯度 | `35.6895` |
| `map_scale` | Number | 地図スケール (m/pixel) | `0.05` |
| `spacing_interval` | Number | 間隔 (meters) | `0.3` |

### 出力パラメータ / Output Parameters

| パラメータ名 | 型 | 説明 |
|-------------|----|----|
| `success` | Boolean | 処理成功フラグ |
| `roof_area` | Number | 屋根面積 (m²) |
| `effective_area` | Number | 有効面積 (m²) |
| `best_panel` | String | 最適パネル名 |
| `max_count` | Number | 最大配置数 |
| `panels` | Object | 各パネルタイプの詳細結果 |
| `visualization_b64` | String | 可視化画像 (Base64) |

## セットアップ / Setup

### 1. 依存関係のインストール / Install Dependencies

```bash
pip install flask opencv-python numpy scipy requests
```

### 2. APIサーバーの起動 / Start API Server

```bash
python api_integration.py
```

サーバーは `http://localhost:8000` で起動します。

### 3. テストの実行 / Run Tests

```bash
python test_integration.py
```

## 使用例 / Usage Examples

### Python例 / Python Example

```python
import requests
import json

# リクエストデータ
data = {
    "mask": "data:image/png;base64,iVBORw0KGgo...",
    "centers": [{"x": 250, "y": 200}],
    "center_latitude": 35.6895,
    "map_scale": 0.05,
    "spacing_interval": 0.3
}

# APIリクエスト
response = requests.post("http://localhost:8000/segment_click", json=data)
result = response.json()

print(f"最適パネル: {result['best_panel']}")
print(f"配置数: {result['max_count']} 枚")
```

### cURL例 / cURL Example

```bash
curl -X POST http://localhost:8000/segment_click \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```

## Base64変換ユーティリティ / Base64 Conversion Utilities

### 画像をBase64に変換 / Convert Image to Base64

```python
import cv2
import base64

def image_to_base64(image_path):
    with open(image_path, 'rb') as f:
        img_data = f.read()
    img_b64 = base64.b64encode(img_data).decode('utf-8')
    return f"data:image/png;base64,{img_b64}"

# 使用例
mask_b64 = image_to_base64("roof_mask.png")
```

### Base64を画像に変換 / Convert Base64 to Image

```python
import cv2
import base64
import numpy as np

def b64_to_cv2(b64str, flags=cv2.IMREAD_UNCHANGED):
    img_bytes = base64.b64decode(b64str.split(",")[-1])
    img_np = np.frombuffer(img_bytes, dtype=np.uint8)
    return cv2.imdecode(img_np, flags)

# 使用例
mask_image = b64_to_cv2(mask_b64, cv2.IMREAD_GRAYSCALE)
cv2.imwrite("decoded_mask.png", mask_image)
```

## エラーハンドリング / Error Handling

### 一般的なエラー / Common Errors

| エラーコード | 説明 | 対処法 |
|-------------|------|--------|
| `no_data` | リクエストデータなし | JSONデータを送信してください |
| `decode_error` | Base64デコードエラー | 正しいBase64形式を確認してください |
| `empty_or_invalid_mask` | 空または無効なマスク | マスク画像の内容を確認してください |
| `processing_error` | 処理エラー | ログを確認してください |

### レスポンス例 / Response Examples

#### 成功時 / Success Response
```json
{
  "success": true,
  "roof_area": 178.26,
  "effective_area": 50.07,
  "best_panel": "Standard_B",
  "max_count": 10,
  "panels": {
    "Standard_B": {
      "count_sim": 10,
      "orientation": "vertical"
    }
  },
  "visualization_b64": "data:image/png;base64,..."
}
```

#### エラー時 / Error Response
```json
{
  "success": false,
  "error": "decode_error",
  "message": "マスクのデコードに失敗しました"
}
```

## 開発・デバッグ / Development & Debugging

### ログの確認 / Check Logs
APIサーバーのコンソール出力でログを確認できます。

### テストデータの生成 / Generate Test Data
```bash
python test_integration.py
# 選択: 3. サンプルリクエストファイル作成
```

### ヘルスチェック / Health Check
```bash
curl http://localhost:8000/health
```

## 本番環境での運用 / Production Deployment

### 推奨設定 / Recommended Settings

1. **Gunicorn使用** / Use Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 api_integration:app
```

2. **Nginx設定** / Nginx Configuration
```nginx
location /segment_click {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

3. **環境変数** / Environment Variables
```bash
export FLASK_ENV=production
export LOG_LEVEL=INFO
```

## トラブルシューティング / Troubleshooting

### よくある問題 / Common Issues

1. **接続エラー** / Connection Error
   - APIサーバーが起動しているか確認
   - ポート8000が使用可能か確認

2. **メモリエラー** / Memory Error
   - 大きな画像の場合はリサイズを検討
   - サーバーのメモリ容量を確認

3. **計算結果が0** / Zero Results
   - マスク画像の内容を確認
   - map_scaleの値を確認

## 連絡先 / Contact

技術的な質問や問題がある場合は、開発チームまでお気軽にお問い合わせください。

---

**更新日 / Last Updated**: 2025-06-27
**バージョン / Version**: v1.0
