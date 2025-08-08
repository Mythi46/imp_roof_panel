import logging
import os
import sys

# 環境変数からログレベルを取得（デフォルトはINFO）
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

# ログレベルを文字列からloggingモジュールの定数に変換
log_level = getattr(logging, log_level, logging.INFO)

# ログの設定
logging.basicConfig(
    level=log_level,
    format='%(name)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]',
    stream=sys.stdout
)
