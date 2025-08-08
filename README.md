# Nobest-IoT-AI
# IMP Roof Panel

本项目包含：
- 屋顶检测服务（roof，FastAPI）：现已完全使用 preroof 强化版模型
- 太阳能板计算服务（panel_count，Flask）
- 需求预测与分类等其他模块

## 快速开始（生产权重）

- 准备权重文件（preroof 训练输出或你提供的生产权重）
- 设置宿主机环境变量并启动 docker compose：
  - Windows PowerShell:
    - `$env:ROOF_MODEL_HOST_PATH="D:\\models\\roof_best.pt"`
  - bash:
    - `export ROOF_MODEL_HOST_PATH=/opt/models/roof_best.pt`
  - `docker compose up -d roof`

compose.yml 已将宿主机权重挂载为 `/models/roof_best.pt`，并通过 `ROOF_MODEL_PATH=/models/roof_best.pt` 被服务加载。生产环境必须提供该权重，不再使用旧的 best_v2.pt。

## 新接口（推荐给面板计算）

- 屋顶检测：`POST /segment_masks`（multipart/form-data: image）
  - 返回 `masks`（PNG base64，0/255 二值）与 `centers`
- 面板计算：`POST /calculate_panels`
  - 支持 `roof_masks`（数组，批量）或 `roof_mask`（单个）

## 本地端到端示例

- 启动屋顶检测（本地权限重）
  - 在 roof 下：`uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - 设置环境变量 `ROOF_MODEL_PATH` 指向你的权重
- 启动面板计算
  - 在 panel_count 下：`python api_integration.py`（端口 8001）
- 运行客户端
  - `python panel_count/roof_detection_client.py`

---


## 準備

### docker

「.env」ファイルを中身を管理者より発行してもらって、ルートフォルダ配下に配置してください。

```bash
WEATHER_SERVER_DOMAIN='http://back_api:8898'
WEATHER_SERVER_KEY="abc"
USE_FIXED_DATE=True
```

### db起動
別リポジトリのNobet-IoTにおいて、dbを起動してください。
```shell
docker-compose up -d --build db
```

## ローカル環境 実行
分類データを入れる場合、nobest-iotリポジトリをローカル実行すると、data/teacherフォルダが作成されるため、その中に分類データを入れ、migrationを再起動させると分類データは挿入されます。

```shell
docker-compose up -d --build
```

## staging 環境 deploy

まず、上記"一括"で起動した環境に対してテストしましょう
develop ブランチに PR 出してマージします
分類データを更新している場合[ここ](https://drive.google.com/drive/folders/1e_zCF6j7jjhDpYMiikryZQuje3gnb4WC?usp=drive_link)から[GCPのteacherフォルダ](https://console.cloud.google.com/storage/browser/nobest-iot/teacher)にデータをuploadします。
GCP で手動で deploy 実行。5分以内にmigrationを実行しないと上記分類データは挿入されないため注意が必要です。

## 本番環境 deploy

staging で確認をまずしましょう。
分類データを入れる場合は、[本番環境のGCPのteacherフォルダ](https://console.cloud.google.com/storage/browser/nobest-iot-gcs/teacher)に入れます。
その後、main ブランチに PR 出して、マージすると自動的に deploy されます。deploy前に分類データを入れつつ、5分以内にマージしてください。
