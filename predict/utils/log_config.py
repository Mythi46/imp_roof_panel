import logging
import os

log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
log_level = getattr(logging, log_level, logging.INFO)

def setup_logging():
    # ロガーを設定
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # フォーマットの設定
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
    # コンソールハンドラーの設定
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # ハンドラーをロガーに追加
    logger.addHandler(console_handler)