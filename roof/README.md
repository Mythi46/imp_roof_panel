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

## 新增：/segment_masks（推荐给面板计算使用）

POST /segment_masks

- 说明：返回 0/255 的二值掩膜（PNG base64）与中心点，方便下游太阳能板计算直接使用。
- 请求：multipart/form-data，字段 image。
- 响应示例：
  {
    "masks": ["data:image/png;base64,iVBORw0KGg..."],
    "centers": [{"x": 199, "y": 257}]
  }

## 生产部署权重加载

- 服务启动时会按以下优先级加载模型权重：
  1) 环境变量 ROOF_MODEL_PATH 指定的模型路径
  2) preroof/runs/.../best.pt（若存在）
  3) roof/best_v2.pt（仓库内默认）
  4) 容器内 /app/roof/best_v2.pt（Docker 默认路径）

- 使用 docker-compose：
  - 在 compose.yml 中，roof 服务默认设置：
    - ROOF_MODEL_PATH=/models/roof_best.pt
    - 将宿主机权重挂载到 /models/roof_best.pt
  - 你可以通过环境变量 ROOF_MODEL_HOST_PATH 指定宿主机权重文件绝对路径。

- 注意：preroof 的模型完全替代旧模型。生产环境必须通过 ROOF_MODEL_PATH 指定权重；不再使用仓库内的旧 best_v2.pt。


