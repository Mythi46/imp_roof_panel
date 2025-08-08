# Pythonのベースイメージを使用
FROM python:3.12.3-slim

# 環境変数の設定（警告の抑制など）
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 必要なパッケージのインストール（libgomp1 など）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgomp1 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# pip のアップグレード
RUN pip install --upgrade pip

# 作業ディレクトリを設定
WORKDIR /app

# Python パッケージのインストール
COPY predict/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースコードをコピー
COPY predict/ .

# サーバーを起動するコマンドを指定
CMD ["python", "main.py"]