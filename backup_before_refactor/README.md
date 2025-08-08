# Roof Segmentation API

学習済み **YOLOv8 segmentation** モデルを用いて、クリック 1 発で屋根を検出・切り抜く FastAPI サーバです。

---

## 1. セットアップ

###  ローカル（Python 仮想環境）

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload  # デフォルト :8000
```

###  Docker Compose 一発起動

```bash
docker compose up --build roof
# ⇒ http://localhost:8000 で稼働
```

---

## 2. エンドポイント仕様

| メソッド | パス               | 説明             |
| ---- | ---------------- | -------------- |
| POST | `/segment_click` | 指定座標を含む屋根を切り抜き |

###  リクエスト

* **Content-Type**: `multipart/form-data`

| キー      | 型    | 必須 | 説明                   |
| ------- | ---- | -- | -------------------- |
| `x`     | int  | ✔︎ | クリックした **X 座標 (px)** |
| `y`     | int  | ✔︎ | クリックした **Y 座標 (px)** |
| `image` | file | ✔︎ | 入力画像 (PNG/JPEG 可)    |

#### curl 例

```bash
curl -X POST http://localhost:8000/segment_click \
  -F "x=1300" \
  -F "y=715"  \
  -F "image=@/path/to/image.png"
```

#### Postman での設定例

| 項目     | 値                                   |
| ------ | ----------------------------------- |
| Method | POST                                |
| URL    | `http://0.0.0.0:8000/segment_click` |
| Body   | `form-data`                         |

| Key   | Value                                        | Type |
| ----- | -------------------------------------------- | ---- |
| x     | 1300                                         | Text |
| y     | 715                                          | Text |
| image | `/Users/…/スクリーンショット 2025-06-17 10.53.39.png` | File |

送信すると **Status 200 OK** と共に JSON が返ります。

###  レスポンス

#### A. クリック領域が屋根以外の場合

```json
{
  "bbox": [1032, 525, 1533, 867],
  "label": "Baren-Land"
}
```

#### B. クリック領域が屋根 (roof) の場合

```json
{
  "bbox": [275, 368, 327, 420],
  "label": "roof",
  "roof_rgba": "data:image/png;base64,iVBORw0K...",
  "segments": [
    {
      "image": "data:image/png;base64,iVBORw0K...",
      "center": { "x": 299, "y": 390 }
    },
    {
      "image": "data:image/png;base64,iVBORw0K...",
      "center": { "x": 310, "y": 405 }
    }
  ]
}
```

* **`roof_rgba`** : クリック屋根全体を透過 PNG として返却
* **`segments`** : 同屋根をさらに区分けした各マスク PNG とその重心座標

###  エラー

| ステータス | 条件 / 内容                        |
| ----- | ------------------------------ |
| 404   | クリック地点に対象クラスが存在しない             |
| 422   | x/y が int でない、画像未添付などバリデーション失敗 |
| 500   | モデル推論中の例外（スタックトレースはコンソールに出力）   |

---

## 3. モデル・パラメータ調整

* 多屋根検出 `conf=0.2`, 単屋根細分割 `conf=0.5`（`main.py` 内）
* `TARGET_CLASSES = {"roof", "Baren-Land", "farm", "rice-fields"}`


