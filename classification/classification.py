import lightgbm as lgb
import numpy as np
from modelsclamp import DevGen
import logging
import pandas as pd
import pytz
from datetime import datetime
from datetime import datetime, timedelta
from db import db_connect, get_cursor


local_tz = pytz.timezone('Asia/Tokyo')
teacher_feature_data = None # 特徴量とラベルのリスト
model = None
index_to_label = None

def get_all_teacher_data():
    global teacher_feature_data
    conn = None
    cursor = None
    teacher_data = []
    try:
        conn = db_connect('clamp_db')
        cursor = get_cursor(conn)
        if not conn or not cursor:
            return None

        query = """
            SELECT 
                td.value, td.teacher_id, td.dev_at, t.class_id
            FROM 
                teacher_data td
            INNER JOIN 
                teachers t ON td.teacher_id = t.id
            ORDER BY 
                td.teacher_id, td.dev_at;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        data_map = {}
        for row in rows:
            teacher_id = row["teacher_id"]
            class_id = row["class_id"]
            value = row["value"]
            if teacher_id not in data_map:
                data_map[teacher_id] = {
                    "class_id": class_id,
                    "values": []
                }
            data_map[teacher_id]["values"].append(value)

        # 出力形式：[ [value_list, class_id], ... ]
        for record in data_map.values():
            teacher_data.append([record["values"], record["class_id"]])
    
        teacher_feature_data = [[get_features(X), y] for X, y in teacher_data]
        return True
    
    except Exception as e:
        logging.error(f"Error in get_all_teacher_data: {e}")
        return False

    finally:
        # カーソルと接続をクローズ
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


def check_clamp_details(clamp):
    try:
        current_time = datetime.now()
        time_threshold = current_time - timedelta(days=7) #予測が低ければ、7日間に1回実行する
        confidence = clamp["confidence"]
        updated_at = clamp["updated_at"]
        if confidence is not None:
            c1 = confidence < 0.9
            c2 = updated_at < time_threshold
            if c1 and c2:
                return True
        else:
            return True

        return False

    except Exception as e:
        clampId = clamp['id']
        logging.error(f"Error in check_clamp_details for clamp_id {clampId}: {e}")
        return False


def get_features(values):
    try:
        if not values:
            return [0] * 11  # 特徴量数と同じ長さのゼロベクトルを返す

        values = np.array(values)

        values = np.array(values)
        mean = np.mean(values)
        std = np.std(values)

        if std < 1e-8:
            skewness = 0.0
            kurtosis = 0.0
        else:
            skewness = np.mean((values - mean)**3) / (std**3)
            kurtosis = np.mean((values - mean)**4) / (std**4) - 3
            
        features = [
            mean,                         # 平均値
            std,                          # 標準偏差
            np.max(values),               # 最大値
            np.min(values),               # 最小値
            np.median(values),            # 中央値
            np.max(values) - np.min(values),  # 範囲（最大値 - 最小値）
            np.percentile(values, 25),    # 25パーセンタイル値
            np.percentile(values, 75),    # 75パーセンタイル値
            np.percentile(values, 75) - np.percentile(values, 25),  # 四分位範囲（IQR）
            skewness,                     # 歪度（skewness）
            kurtosis                      # 尖度（kurtosis）
        ]

        return features
    
    except Exception as e:
        logging.error(f"Error in get_features: {e}")
        return [0] * 11  # エラー時にはゼロベクトルを返す

def get_sorted_frame_target_data(cursor, clampId, channel):
    try:
        genTable = f"dev_gen_{clampId}"
        frameTable = f"dev_gen_frame_{clampId}"

        query = f"""
                    SELECT g.*, f.start_dev_gen_id, f.end_dev_gen_id
                    FROM {frameTable} AS f
                    INNER JOIN {genTable} AS g
                    ON g.id=f.start_dev_gen_id
                    WHERE g.channel = %s
                    ORDER BY f.id
                    LIMIT 10;
                """
        
        cursor.execute(query, (channel,))
        frames = cursor.fetchall()
        if not frames:
            logging.debug(f"No frames found for clampId={clampId}, channel={channel}")
            return None

        result_data = []
        for frame in frames:
            start_id = frame['start_dev_gen_id']
            end_id = frame['end_dev_gen_id']
            
            if end_id is not None:
                range_query = f"""
                    SELECT *
                    FROM {genTable}
                    WHERE channel = %s AND id BETWEEN %s AND %s
                    ORDER BY dev_at;
                """
                cursor.execute(range_query, (channel, start_id, end_id))
            else:
                range_query = f"""
                    SELECT *
                    FROM {genTable}
                    WHERE channel = %s AND id >= %s
                    ORDER BY dev_at;
                """
                cursor.execute(range_query, (channel, start_id))
            
            gen_data = cursor.fetchall()
            frame_df = pd.DataFrame(gen_data)
            result_data.append(frame_df)

        if not result_data:
            logging.debug(f"No data found for clampId={clampId}, channel={channel}")
            return None
        
        return result_data
    except Exception as e:
        logging.error(f"Error in get_sorted_frame_target_data for clampId={clampId}, channel={channel}: {e}")
        return None


def train_model():
    global model, index_to_label
    try:
        # 特徴量とラベルをそれぞれ抽出して numpy 配列に変換
        X = np.array([data[0] for data in teacher_feature_data])  # 特徴量のリストを numpy.array に変換
        y = np.array([data[1] for data in teacher_feature_data])  # ラベルのリストを numpy.array に変換

        # ユニークなラベルを抽出し、エンコード用のマッピングを作成
        unique_labels = sorted(list(set(y)))  # ラベルを昇順にソートしてユニークなラベルリストを作成
        label_to_index = {label: index for index, label in enumerate(unique_labels)}  # ラベル → インデックスのマッピングを作成
        index_to_label = {index: label for index, label in enumerate(unique_labels)}  # インデックス → ラベルのマッピングを作成

        # ラベルを [0, num_class-1] の範囲に変換（エンコード）
        y_encoded = np.array([label_to_index[label] for label in y])

        # クラス数の設定
        num_classes = len(unique_labels)

        # LightGBM のデータセット作成
        train_dataset = lgb.Dataset(X, label=y_encoded)

        # LightGBM のパラメータ設定
        params = {
            'objective': 'multiclass',
            'num_class': num_classes,  # クラス数はユニークラベルの数
            'learning_rate': 0.1,
            'verbosity': -1,
        }

        # LightGBM モデルの訓練
        model = lgb.train(
            params,
            train_dataset,
            num_boost_round=100
        )
        return True
    
    except Exception as e:
        logging.error(f"Error in train_model: {e}")
        return False

def predict(test_data):
    try:
        test_data = np.array(test_data)  # test_dataをnumpy配列に変換

        # モデルを用いてテストデータの予測確率を計算
        probabilities = model.predict(test_data, num_iteration=model.best_iteration)

        # 平均確率を計算（テストデータ全体の平均）
        mean_probabilities = np.mean(probabilities, axis=0)

        # 最も確率が高いクラスを取得し、そのクラスのラベルを返す
        final_predicted_class_index = np.argmax(mean_probabilities)
        final_predicted_class = index_to_label[final_predicted_class_index]
        final_confidence = mean_probabilities[final_predicted_class_index]

        return final_predicted_class, final_confidence
    
    except Exception as e:
        logging.error(f"Error in predict: {e}")
        return None, 0.0

def update_labels(conn, cursor, clamp_id, class_id, confidence):
    try:
        now_at = datetime.now(local_tz).strftime('%Y-%m-%d %H:%M:%S')

        query = f"""
        UPDATE clamp_details
        SET updated_at = %s,
            class_id = %s,
            confidence = %s
        WHERE clamp_id = %s
        """
        cursor.execute(query, (now_at, int(class_id), float(confidence), clamp_id))
        conn.commit()
        return True
    
    except Exception as e:
        logging.error(f"Error updating database for clamp_id={clamp_id}: {e}")
        conn.rollback()
        return False

async def handle_classification_request(conn, cursor, cursorClamp, dbTable, channel, clamp):
    try:
        clampId = clamp['id']
        if check_clamp_details(clamp):
            target_data = get_sorted_frame_target_data(cursorClamp, clampId, channel)                
            if not target_data or len(target_data) == 0:
                return True
            
            target_data = [df['value'].tolist() for df in target_data]
            target_feature_data = [get_features(values) for values in target_data]
            if not target_feature_data:
                return True

            final_predicted_class, final_confidence = predict(target_feature_data)
            logging.info(f"dbTable: {dbTable}, final_predicted_class: {final_predicted_class}, final_confidence: {final_confidence}")
            if final_predicted_class!=None:
                update_labels(conn, cursor, clampId, final_predicted_class, final_confidence)

        return True
    
    except Exception as e:
        logging.error(f"Error in handle_classification_request: {e}")
        return False
    