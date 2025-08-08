import os
import mysql.connector
from mysql.connector import Error

DB_USER = os.getenv('DB_USER', 'root')
DB_PASS = os.getenv('DB_PASS', 'pass')
DB_HOST = os.getenv('DB_HOST', 'localhost')  # 'nobest-iot' から 'localhost' に変更
DB_PORT = os.getenv('DB_PORT', '3306')

def db_connect(db_name):
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=db_name,
            port=DB_PORT,
            connection_timeout=3600,  # タイムアウトを1時間に設定（3600秒）
            pool_size=10,  # コネクションプールのサイズ
            pool_reset_session=True  # セッションのリセット
        )
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def get_cursor(conn):
    try:
        if not conn.is_connected():
            conn.reconnect(attempts=3, delay=5)  # 再接続を試みる

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SET time_zone = '+09:00'")  # 日本標準時 (JST) に設定
        return cursor
    except Error as e:
        print(f"Error getting cursor: {e}")
        return None
