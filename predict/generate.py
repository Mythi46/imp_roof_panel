import torch
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import logging
import pandas as pd
import pytz
from datetime import datetime, timedelta
import re
from db import db_connect, get_cursor
from decimal import Decimal
import asyncio
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import os
import pickle
import requests
import traceback
from modelsclamp import DevGen
from model_module import LSTMModel
from utils.sentry import send_message_to_sentry_err, send_message_to_sentry_info, send_message_to_sentry_warn

local_tz = pytz.timezone('Asia/Tokyo')

# Load environment variables
load_dotenv()

WEATHER_SERVER_KEY = os.getenv('WEATHER_SERVER_KEY')
WEATHER_SERVER_DOMAIN = os.getenv('WEATHER_SERVER_DOMAIN')

if WEATHER_SERVER_KEY is None:
    raise ValueError("API_KEYが環境変数に設定されていません。")
if WEATHER_SERVER_DOMAIN is None:
    raise ValueError("WEATHER_SERVER_DOMAINが環境変数に設定されていません。")

# Thread pool executor for synchronous tasks
executor = ThreadPoolExecutor(max_workers=5)

def load_model():
    """
    Load the pre-trained LSTM model from a .pth file and the scaler from a pickle file.
    """
    try:
        model_path = './model/lstm_generate_model.pth'
        scaler_path = './model/scaler.pkl'
        target_scaler_path='./model/target_scaler.pkl'

        # モデルのインスタンス化とロード
        # 修正後のモデル定義
        input_size = 10
        hidden_size = 128
        num_layers = 2
        output_size = 72
        model = LSTMModel(input_size, hidden_size, num_layers, output_size)
        model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu'),weights_only=True))
        model.eval()  # 評価モードに設定

        # スケーラーのロード
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        
        with open(target_scaler_path, 'rb') as f:
            target_scaler = pickle.load(f)

        return model, scaler,target_scaler
    except Exception as e:
        send_message_to_sentry_err(f"モデルのロード中にエラーが発生しました: {e}")
        return None, None
    
def fetch_weather_data(start_date, end_date, city_code):
    """
    Fetch weather data from the external API.
    """
    start_day = start_date.strftime('%Y-%m-%d')
    last_day = end_date.strftime('%Y-%m-%d')
    try:
        api_url = f"{WEATHER_SERVER_DOMAIN}/api/v1/past/list/hour"
        headers = {
            'Content-Type': 'application/json',
            'apikey': WEATHER_SERVER_KEY
        }
        params = {
            'start_day': start_day,
            'last_day': last_day,
            'city_code[]': [city_code]
        }
        #logging.debug(f"Fetching weather data from: {api_url} with params: {params}")
        response = requests.get(api_url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            #logging.debug(f"API Response Data: {data}")  # 追加
            # 指定したcity_codeのデータをフィルタリング
            filtered_data = [item for item in data if item.get('city_code') == city_code]
            if filtered_data:
                #logging.info(f"city_code {city_code} の天気データを取得しました。")
                #logging.debug(f"取得したデータの詳細:\n{filtered_data}")  # デバッグログを追加
                return filtered_data
            else:
                send_message_to_sentry_warn(f"city_code {city_code} のデータが見つかりませんでした。")
                return []
        else:
            send_message_to_sentry_err(f"天気データの取得に失敗しました。ステータスコード: {response.status_code} {response.text}")
            return []
        
    except Exception as e:
        send_message_to_sentry_err(f"fetch_weather_data 関数内でエラーが発生しました: {e}")
        return []


def process_weather_data(filtered_data):
    """
    Process and clean the fetched weather data.
    """
    try:
        # データを展開してリスト化
        records = []
        for entry in filtered_data:
            for record in entry.get('pasts', []):
                records.append({
                    'dev_at': record.get('date'),           # DateTime
                    'temp': record.get('temp'),             # Temperature
                    'wind_speed': record.get('speed'),      # Wind Speed
                    'wind_dir': record.get('dir'),          # Wind Direction
                    'precipitation': record.get('precipitation'),  # Precipitation
                    'snowfall': record.get('snow'),         # Snowfall
                    'humidity': record.get('humidity'),     # Humidity
                    # 他の必要な特徴量があれば追加
                })
        # DataFrameに変換
        data = pd.DataFrame(records)

        # 'dev_at' を datetime 型に変換
        data['dev_at'] = pd.to_datetime(data['dev_at'], errors='coerce')

        # タイムゾーンの確認とローカライズ
        if data['dev_at'].dt.tz is None:
            data['dev_at'] = data['dev_at'].dt.tz_localize('UTC').dt.tz_convert(local_tz)
        else:
            data['dev_at'] = data['dev_at'].dt.tz_convert(local_tz)

        # 年、月、日、時間の列を追加
        data['Month'] = data['dev_at'].dt.month
        data['day'] = data['dev_at'].dt.day
        data['Hour'] = data['dev_at'].dt.hour

        # 'is_weekend' の列を追加（0: 平日, 1: 週末）
        data['is_weekend'] = data['dev_at'].dt.weekday.isin([5, 6]).astype(int)

        # 不要な列を削除
        # 'weather_detail_id' がない場合は無視
        # data = data.drop(['dev_at', 'weather_detail_id'], axis=1)
        # 予測時には 'dev_at' が必要なので削除しない

        # データ型の変換
        object_cols = data.select_dtypes(include=['object']).columns
        for col in object_cols:
            data[col] = pd.to_numeric(data[col], errors='coerce')

        # 欠損値の処理
        data = data.dropna()

        # 特徴量の順序をトレーニング時と一致させる
        feature_cols = ['temp', 'wind_speed', 'wind_dir', 'precipitation', 'snowfall',
                        'humidity', 'Month', 'day', 'Hour', 'is_weekend']
        data = data[['dev_at'] + feature_cols]

        return data
    
    except Exception as e:
        send_message_to_sentry_err(f"process_weather_data 関数内でエラーが発生しました: {e}")
        return pd.DataFrame()


def make_forecast(model, scaler,target_scaler, data, forecast_start_date, sequence_length, forecast_steps):
    """
    Make forecasts using the LSTM model.
    """
    try:
        # シーケンスデータの作成
        # 過去のデータを取得
        sequence_data = data[(data['dev_at'] >= forecast_start_date - timedelta(hours=sequence_length)) &
                             (data['dev_at'] < forecast_start_date)].copy()

        if len(sequence_data) < sequence_length:
            send_message_to_sentry_err(f"シーケンス長 {sequence_length} に対してデータが不足しています。")
            return None

        # 特徴量のみを取得
        feature_cols = ['temp', 'wind_speed', 'wind_dir', 'precipitation', 'snowfall',
                        'humidity', 'Month', 'day', 'Hour', 'is_weekend']
        sequence_data = sequence_data[feature_cols]

        # スケーリング
        input_data = sequence_data.values.astype(np.float32)
        input_scaled = scaler.transform(input_data)

        # テンソルに変換し、形状を (batch_size=1, seq_length, num_features) に調整
        input_tensor = torch.tensor(input_scaled).unsqueeze(0)

        # モデルで予測
        model.eval()
        with torch.no_grad():
            outputs = model(input_tensor)
            # outputs.shape: (batch_size=1, forecast_steps)
            predictions_scaled = outputs.numpy().flatten()

        # 予測値を逆変換
        # predictions_scaled の形状を (n_samples, 1) に変換
        predictions_scaled = predictions_scaled.reshape(-1, 1)
        predictions_inv = target_scaler.inverse_transform(predictions_scaled).flatten()

        # 予測結果と対応する日時を組み合わせる
        predictions = []
        current_date = forecast_start_date
        for value in predictions_inv:
            predictions.append((value, current_date))
            current_date += timedelta(hours=1)

        return predictions

    except Exception as e:
        send_message_to_sentry_err(f"予測中にエラーが発生しました: {e}")
        return None


def insert_or_update_predict_data(conn, cursor, table, predict, channel, type):

    try:
        now_at = datetime.now(local_tz).strftime('%Y-%m-%d %H:%M:%S')
        
        for value, dev_at in predict:
            # 負の値を0に補正
            value = max(0.0, float(value))
            dev_at_str = dev_at.strftime('%Y-%m-%d %H:%M:%S')
            
            
            insert_query = f"""
            INSERT INTO {table} (
                value, channel, cite,
                dev_at, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                value,
                channel,
                DevGen.DataCiteGen,        # cite
                dev_at_str,
                now_at,   # created_at
                now_at,   # updated_at
            ))
            #logging.debug(f"Inserted new record for dev_at: {dev_at_str}, channel: {channel}")
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        logging.error(f"Database operation failed: {e}")
        logging.error(traceback.format_exc())
        return False

async def handle_generate_request(conn, cursor, dbTable, channel, city_code):
    """
    Handle the generate request: load model, fetch and process data, predict, and update the database.
    """
    try:
        if city_code == None or city_code == 0:
            return False

        # モデルとスケーラーのロードを非同期的に実行
        loop = asyncio.get_event_loop()
        model, scaler, target_scaler = await loop.run_in_executor(executor, load_model)
        if model is None or scaler is None or target_scaler is None:
            send_message_to_sentry_err(f"モデルまたはスケーラーのロードに失敗しました。{dbTable} {channel} {city_code}")
            return False

        # 予測開始日時の設定 .envで変更を指定
        USE_FIXED_DATE = os.getenv('USE_FIXED_DATE', 'False') == 'True'

        if USE_FIXED_DATE:
            # 固定日付を使用
            forecast_start_date = local_tz.localize(datetime(2024, 9, 14, 0, 0, 0))
            logging.info(f"Fixed forecast_start_date set to {forecast_start_date}")
        else:
            # 現在時刻を基に動的に設定
            now = datetime.now(local_tz)
            forecast_start_date = now.replace(minute=0, second=0, microsecond=0)
            logging.info(f"Dynamic forecast_start_date set to {forecast_start_date}")


        # パラメータ設定
        N = 7  # 過去N日分のデータを使用
        forecast_days = 3  # 予測する日数
        sequence_length = N * 24  # シーケンス長
        forecast_steps = forecast_days * 24  # 予測ステップ数

        # データ取得範囲の設定
        start_date = forecast_start_date - timedelta(hours=sequence_length)
        end_date = forecast_start_date + timedelta(hours=forecast_steps - 1)

        # 天気データの取得
        filtered_data = fetch_weather_data(start_date, end_date, city_code)
        if not filtered_data:
            return False

        # データの前処理
        data = process_weather_data(filtered_data)
        if data.empty:
            return False

        # 予測の実行
        predictions = make_forecast(model, scaler, target_scaler, data, forecast_start_date, sequence_length, forecast_steps)
        if predictions is None:
            return False

        # データベースへの挿入
        insert_or_update_predict_data(conn, cursor, dbTable, predictions, channel, 0)

        return True

    except Exception as e:
        send_message_to_sentry_err(f"handle_generate_request 関数内でエラーが発生しました: {e}")
        return False