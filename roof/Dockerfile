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

#モデル保存
COPY best_v2.pt ./roof/best_v2.pt

# アプリケーションコードをコピー
COPY app/ ./app 

# FastAPI＋Uvicorn が使うポート
EXPOSE 8000

# デフォルトコマンド
# --reload は開発用（ファイル変更時に自動リロード）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
