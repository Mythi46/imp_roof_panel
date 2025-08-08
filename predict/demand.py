import traceback
import pandas as pd
import numpy as np
import logging
from utils.sentry import send_message_to_sentry_err, send_message_to_sentry_warn
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
from modelsclamp import DevGen

def get_original_data(conn, cursor, dbTable, channel):
    try:
        # データを取得するクエリ
        query = f"SELECT id, dev_at, value FROM {dbTable} WHERE DATE_FORMAT(dev_at, '%i') = '00' AND dev_at >= DATE_ADD(CURDATE(), INTERVAL -31 DAY) AND dev_at < CURDATE() AND channel = {channel} ORDER BY dev_at DESC;"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        if not rows:
            return None
        
        df = pd.DataFrame(rows, columns=['id', 'dev_at', 'value'])
        return df

    except Exception as e:
        send_message_to_sentry_err(f"Error fetching data: {e}")
        return None


def create_data(df):
    Today = datetime.combine(datetime.now().date(), datetime.min.time())

    # x_testの生成
    x_test = df[(df['dev_at'] >= (Today - timedelta(days=7))) & (df['dev_at'] < (Today))].sort_values(by='dev_at', ascending=False)['value'].tolist()

    # x_data, y_dataの生成
    x_data = []
    y_data = []

    for i in range(21):
        # x_dataの生成
        x_data_i = df[(df['dev_at'] >= (Today - timedelta(days=(i + 10)))) & (df['dev_at'] < (Today - timedelta(days=(i + 3))))].sort_values(by='dev_at', ascending=False)['value'].tolist()
        x_data.append(x_data_i)

        # y_dataの生成
        y_data_i = df[(df['dev_at'] >= (Today - timedelta(days=(i + 3)))) & (df['dev_at'] < (Today - timedelta(days=(i))))].sort_values(by='dev_at', ascending=False)['value'].tolist()
        y_data.append(y_data_i)  
    
    for k in range(len(x_data) - 1, -1, -1):
        if len(x_data[k]) != 168 or len(y_data[k]) != 72:
            del x_data[k]
            del y_data[k]

    return x_data, y_data, x_test

# モデルの構築とトレーニングを行う関数
def train_lstm_model(x_list, y_list):
    try:
        # NumPy配列に変換
        X = np.array(x_list)  # (21, 168)
        Y = np.array(y_list)  # (21, 72)

        # LSTMに入力するため、Xの形状を (サンプル数, タイムステップ数, 特徴数) に変更
        X = X.reshape((X.shape[0], X.shape[1], 1))  # (21, 168, 1)

        # 訓練データとテストデータに分割
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

        # モデルの構築
        model = Sequential()
        model.add(LSTM(50, activation='relu', input_shape=(X.shape[1], X.shape[2])))
        model.add(Dense(72, activation='relu'))  # 出力層にReLUを適用

        # 学習率を小さめに設定
        optimizer = Adam(learning_rate=0.001)
        model.compile(optimizer=optimizer, loss='mse')

        # モデルのトレーニング
        model.fit(X_train, Y_train, epochs=1000, verbose=0)

        # テストデータでの評価
        loss = model.evaluate(X_test, Y_test, verbose=0)
        logging.info(f'Test Loss: {loss}')
        return model

    except Exception as e:
        send_message_to_sentry_err(f"モデルの学習においてエラーが発生しました: {e}")
        return None
            
# 予測を行う関数
def predict_y(target_x, model):
    try:
        # target_xの形状をモデルの入力に合わせて (1, 168, 1) に変換
        target_x = np.array(target_x).reshape((1, len(target_x), 1))

        # 予測
        y_predict = model.predict(target_x, verbose=0)[0]
        y_predict = [x if x >= 0 else 0 for x in y_predict]
    
        return y_predict
    
    except Exception as e:
        send_message_to_sentry_err(f"需要予測においてエラーが発生しました: {e}")
        return None


# DBのUPDATE（または追加）
def insert_or_update_predict_data(conn, cursor, table, predict, channel):
    try:        
        # 本日の00:00を基準とした時刻を取得
        Today = datetime.combine(datetime.now().date(), datetime.min.time())
        now_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # predictリストの各要素を順に処理
        for i, value in enumerate(predict):
            # valueを適切なfloat型に変換
            value = float(value)
            
            # dev_atを設定
            dev_at = Today + timedelta(minutes=i*60)
            dev_at_str = dev_at.strftime('%Y-%m-%d %H:%M:%S')
            
            # 値を挿入または更新
            query = f"""
            INSERT INTO {table} (value, channel, cite, dev_at, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                value = VALUES(value),
                updated_at = VALUES(updated_at)
            """
            cursor.execute(query, (
                value,                   # value
                channel,                 # channel
                DevGen.DataCiteGen,      # cite
                dev_at_str,              # dev_at
                now_at,                  # created_at
                now_at,                  # updated_at
            ))

        conn.commit()
    
    except Exception as e:
        conn.rollback()
        send_message_to_sentry_err(f"Database update failed: {e}")
        return False

# メイン処理関数
async def handle_demand_request(conn, cursor, dbTable, channel):

    try:
        original_data = get_original_data(conn, cursor, dbTable, channel)

        if original_data is None:
            return False

        # データをトレーニング用と予測用に分割
        x_data, y_data, x_test = create_data(original_data)
        if len(x_data) < 10:
            logging.debug(f"需要予測モデルの学習に必要なデータ数に満たなかったため、処理をスキップします。 dbTable: {dbTable} channel: {channel} x_data: {len(x_data)}, y_data: {len(y_data)}, x_test: {len(x_test)}")
            return True
        if len(x_test) < 10:
            logging.debug(f"需要予測モデルの予測に必要なデータ数に満たなかったため、処理をスキップします。 dbTable: {dbTable} channel: {channel} x_data: {len(x_data)}, y_data: {len(y_data)}, x_test: {len(x_test)}")
            return True

        # モデルをトレーニング
        model = train_lstm_model(x_data, y_data)
        if model is None:
            send_message_to_sentry_err(f"需要予測モデルの学習に失敗したため、処理をスキップします。 dbTable: {dbTable} channel: {channel} x_data: {len(x_data)}, y_data: {len(y_data)}, x_test: {len(x_test)}")
            return False
        
        predict = predict_y(x_test, model)
        logging.debug(f"prediction result {dbTable} channel={channel} predict={predict}  length: x_data: {len(x_data)}, y_data: {len(y_data)}, x_test: {len(x_test)}")

        if predict:
            insert_or_update_predict_data(conn, cursor, dbTable, predict, channel)
        return True

    except Exception as e:
        send_message_to_sentry_err(f"handle_generate_request 関数内でエラーが発生しました: {e}")
        return False