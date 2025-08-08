import os
import sentry_sdk
import logging
import inspect
from datetime import datetime

# SentryのDSNを設定
dsn = os.getenv('SENTRY_DSN')
sentry_sdk.init(
    dsn=dsn,
    traces_sample_rate=1.0
)

# メッセージを送信する関数
def send_message_to_sentry_info(message):
    # 呼び出し元のスタック情報を取得
    frame = inspect.currentframe().f_back
    filename = frame.f_code.co_filename
    lineno = frame.f_lineno
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # メッセージを構築
    message = f"[{timestamp}] {filename}:{lineno} - {message}"

    # ローカルログ出力
    logging.info(message)

    with sentry_sdk.push_scope() as scope:
        scope.set_level("info")
        sentry_sdk.capture_message(message)

def send_message_to_sentry_warn(message):
    # 呼び出し元のスタック情報を取得
    frame = inspect.currentframe().f_back
    filename = frame.f_code.co_filename
    lineno = frame.f_lineno
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # メッセージを構築
    message = f"[{timestamp}] {filename}:{lineno} - {message}"

    # ローカルログ出力
    logging.warning(message)

    with sentry_sdk.push_scope() as scope:
        scope.set_level("warning")
        sentry_sdk.capture_message(message)

def send_message_to_sentry_err(message):
    # 呼び出し元のスタック情報を取得
    frame = inspect.currentframe().f_back
    filename = frame.f_code.co_filename
    lineno = frame.f_lineno
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # メッセージを構築
    message = f"[{timestamp}] {filename}:{lineno} - {message}"

    # ローカルログ出力
    logging.error(message)

    # Sentry 送信
    with sentry_sdk.push_scope() as scope:
        scope.set_level("error")
        sentry_sdk.capture_message(message)