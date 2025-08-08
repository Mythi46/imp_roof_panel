# ベースイメージ
FROM python:3.10-slim

# 作業ディレクトリ
WORKDIR /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 依存関係だけ先にインストール（キャッシュ効くように）
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# モデルはコンテナ外からマウントし、環境変数 ROOF_MODEL_PATH で指定する方針
# COPY は行いません（本番環境での明示的なモデル管理を徹底）

# アプリケーションコードをコピー
COPY app/ ./app 

# FastAPI＋Uvicorn が使うポート
EXPOSE 8000

# デフォルトコマンド
# --reload は開発用（ファイル変更時に自動リロード）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
