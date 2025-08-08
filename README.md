# Nobest-IoT-AI

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
