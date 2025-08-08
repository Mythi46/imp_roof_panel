# Roof Segmentation API

この API は、学習済み YOLO モデルを用いて屋根のセグメンテーションを行います。
アップロードされた画像に対して、検出されたマスク領域の PNG 画像（Base64 形式）と各領域の中心座標(x, y)を返します。

## エンドポイント

**POST** `/segment`

### 説明

- 画像ファイルをアップロードし、セグメントマスク画像と中心座標を取得します。

### リクエスト

- **Content-Type:** `multipart/form-data`
- **パラメータ:**

  - `image` (必須): 処理対象の画像ファイル (binary) 640×640 のサイズ限定で送ってください

#### `curl`例

```bash
curl -X POST \
  -F "image=@/path/to/your/image.jpg" \
  http://localhost:8000/segment
```

### レスポンス

- **ステータスコード:** `200 OK`
- **Content-Type:** `application/json`

#### 成功時 JSON スキーマ

```json
{
  "images": ["data:image/png;base64,iVBORw0KGg..."],
  "centers": [{ "x": 199, "y": 257 }]
}
```

#### バリデーションエラー (422)

```json
{
  "detail": [
    {
      "loc": ["body", "image"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## 使い方

1. **Docker コンテナのビルド＆起動** (Docker Compose を使用)

```bash
docker-compose up --build roof
```

2. **エンドポイントのテスト**

   - `curl` や Postman などで `POST` リクエストを送信。

3. **レスポンスの利用**

   - `images` に返される Base64 PNG を表示または保存。
   - `centers` の `(x,y)` を UI 上のボタン配置などに利用。

## 注意点

- `process_image` 関数内の `conf` パラメータ（デフォルト `0.8`）で検出閾値を調整可能です。
