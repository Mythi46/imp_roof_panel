import pandas as pd
import numpy as np
import logging
import logconf
from datetime import datetime, timedelta
from scipy.stats import kurtosis, skew
import pywt
from sklearn.mixture import GaussianMixture
from modelsclamp import DevGen
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from kneed import KneeLocator
import pytz
from datetime import datetime

local_tz = pytz.timezone('Asia/Tokyo')

def get_sorted_train_data(cursor, table, channel):
    query = f"""
        SELECT * FROM {table}
        WHERE (label=%s OR label=%s)
        AND (frame=%s OR frame=%s)
        AND channel=%s
        ORDER BY dev_at;
    """
    cursor.execute(query, (DevGen.DataLabelGoodTeach, DevGen.DataLabelGoodInference, DevGen.DataFrameStart, DevGen.DataFrameEnd, channel))
    data = cursor.fetchall()
    return data

def get_sorted_target_data(cursor, table, channel):
    query = f"""
        SELECT * FROM {table}
        WHERE label=%s
        AND (frame=%s OR frame=%s)
        AND channel=%s
        ORDER BY dev_at;
    """
    cursor.execute(query, (DevGen.DataLabelNone, DevGen.DataFrameStart, DevGen.DataFrameEnd, channel))
    data = cursor.fetchall()
    return data

def split_data(data):
    result_data = []
    current_group = []

    for row in data:
        if row['frame'] == DevGen.DataFrameStart:
            current_group.append(row)
        else:  # Frameが2の場合
            current_group.append(row)
            result_data.append(pd.DataFrame(current_group))
            current_group = []

    if current_group:
        result_data.append(pd.DataFrame(current_group))

    return result_data


def check_and_remove_errors_from_dfs(df_list):
    cleaned_df_list = []

    for df in df_list:
        # 'dev_at'カラムがdatetime型であることを確認
        df['dev_at'] = pd.to_datetime(df['dev_at'])

        # タイムスタンプ間の差分を計算
        df['time_diff'] = df['dev_at'].diff()

        # 最初の行（NaTを含む）を除外してエラーを検出
        error_rows = df.iloc[1:][df['time_diff'].iloc[1:] > timedelta(seconds=90)]

        if not error_rows.empty:
            error_ids = error_rows['id'].tolist()
            logging.error(f"異常検知が行われませんでした。dev_gen.id: {error_ids}")

            # エラーが発生した行の前後を表示
            for idx in error_rows.index:
                # 前の行が存在する場合の処理
                if idx - 1 in df.index:
                    prev_row = df.loc[idx - 1, ['id', 'dev_at', 'time_diff']]
                    logging.error(f"Previous row - id: {prev_row['id']}, dev_at: {prev_row['dev_at']}, time_diff: {prev_row['time_diff']}")
                else:
                    logging.error(f"No previous row found for id: {df.loc[idx, 'id']}")

                # エラー行の情報を表示
                logging.error(f"Error row - id: {df.loc[idx, 'id']}, dev_at: {df.loc[idx, 'dev_at']}, time_diff: {df.loc[idx, 'time_diff']}")

                # 次の行が存在する場合の処理
                if idx + 1 in df.index:
                    next_row = df.loc[idx + 1, ['id', 'dev_at', 'time_diff']]
                    logging.error(f"Next row - id: {next_row['id']}, dev_at: {next_row['dev_at']}, time_diff: {next_row['time_diff']}")
                else:
                    logging.error(f"No next row found for id: {df.loc[idx, 'id']}")

        else:
            cleaned_df_list.append(df)

    return cleaned_df_list

def calculate_features(on_data_list):

    features_list = []

    print_index = 0
    for df in on_data_list:
        feature_list = []
        # シーケンス長をデータフレームの長さで計算
        sequence_length = len(df)
        feature_list.append(sequence_length)

        # データフレームの最初と最後に8分ずつのvalue=0のデータを追加
        zero_data_start = pd.DataFrame({'value': [0]*8})
        zero_data_end = pd.DataFrame({'value': [0]*8})
        modified_df = pd.concat([zero_data_start, df, zero_data_end], ignore_index=True)

        if print_index == 0:
            logging.info(f"modified_df: {modified_df[['value', 'dev_at']]}")
            print_index += 1

        # 特徴量の計算
        mean_value = modified_df['value'].mean()
        feature_list.append(mean_value)

        max_value = modified_df['value'].max()
        feature_list.append(max_value)

        min_value = modified_df['value'].min()
        feature_list.append(min_value)

        std_dev = modified_df['value'].std()
        feature_list.append(std_dev)

        kurt = kurtosis(modified_df['value'])
        feature_list.append(kurt)

        skewness = skew(modified_df['value'])
        feature_list.append(skewness)

        values = modified_df['value'].values
        coeffs = pywt.wavedec(values, 'db1', level=2)
        coeffs_0 = coeffs[0]
        coeffs_1 = coeffs[1]

        #エネルギー4分割
        quarter_len = len(coeffs_0) // 4
        coeffs_0q1 = coeffs_0[:quarter_len]
        coeffs_0q2 = coeffs_0[quarter_len:2*quarter_len]
        coeffs_0q3 = coeffs_0[2*quarter_len:3*quarter_len]
        coeffs_0q4 = coeffs_0[3*quarter_len:]

        coeffs_1q1 = coeffs_1[:quarter_len]
        coeffs_1q2 = coeffs_1[quarter_len:2*quarter_len]
        coeffs_1q3 = coeffs_1[2*quarter_len:3*quarter_len]
        coeffs_1q4 = coeffs_1[3*quarter_len:]

        # エネルギー計算
        energy0q1 = np.sum(np.square(coeffs_0q1))
        energy0q2 = np.sum(np.square(coeffs_0q2))
        energy0q3 = np.sum(np.square(coeffs_0q3))
        energy0q4 = np.sum(np.square(coeffs_0q4))

        energy1q1 = np.sum(np.square(coeffs_1q1))
        energy1q2 = np.sum(np.square(coeffs_1q2))
        energy1q3 = np.sum(np.square(coeffs_1q3))
        energy1q4 = np.sum(np.square(coeffs_1q4))

        # 特徴量リストに追加
        feature_list.append(energy0q1)
        feature_list.append(energy0q2)
        feature_list.append(energy0q3)
        feature_list.append(energy0q4)
        feature_list.append(energy1q1)
        feature_list.append(energy1q2)
        feature_list.append(energy1q3)
        feature_list.append(energy1q4)

        # NaNが含まれているかチェック
        if any(np.isnan(feature_list)):
            logging.error(f"id={df.iloc[0]['id']}から始まるdfでfeatures_nan_errorが発生しました")
            feature_list = [0 if np.isnan(x) else x for x in feature_list]
            logging.error(f"修正後の features_list: {features_list}")

        features_list.append(feature_list)

    logging.debug(f"features_list[0]: {features_list[0]}")

    return features_list

# エルボー法によるコンポーネント数決定関数
def determine_optimal_clusters(train_features):
    max_clusters = int(len(train_features) / 20) + 2

    if max_clusters < 2:
      return 1
    else:
      # 標準化
      scaler = StandardScaler()
      scaled_features = scaler.fit_transform(train_features)

      # クラスター数ごとの誤差（inertia）を格納するリスト
      inertia = []

      # 各クラスター数に対してKMeansを実行
      for n_clusters in range(1, max_clusters + 1):
          kmeans = KMeans(n_clusters=n_clusters, random_state=42)
          kmeans.fit(scaled_features)
          inertia.append(kmeans.inertia_)

      # KneeLocatorを使ってエルボーを自動検出
      kl = KneeLocator(range(1, max_clusters + 1), inertia, curve='convex', direction='decreasing')
      optimal_clusters = kl.elbow

      if optimal_clusters:
        return optimal_clusters
      else:
        return 1


# GMMの学習関数
def train_gmm(features_list, reg_covar=1e-4):
    n_components = determine_optimal_clusters(features_list)
    logging.debug(f"n_components: {n_components}")

    try:
        gmm = GaussianMixture(n_components=n_components, reg_covar=reg_covar, random_state=42)
        gmm.fit(features_list)
        return gmm
    except Exception as e:
        logging.error(f"An error occurred during GMM fitting: {e}")
        return None

# 異常検知関数
def classify_anomalies(gmm, features_list):
    cluster_ranges = []
    for i in range(gmm.n_components):
        cluster_data = gmm.means_[i]
        cluster_min = cluster_data - 3 * np.sqrt(np.diag(gmm.covariances_[i]))
        cluster_max = cluster_data + 3 * np.sqrt(np.diag(gmm.covariances_[i]))
        cluster_ranges.append((cluster_min, cluster_max))
    classifications = []
    for point in features_list:
        in_cluster = False
        for (cluster_min, cluster_max) in cluster_ranges:
            if np.all(point >= cluster_min) and np.all(point <= cluster_max):
                in_cluster = True
                break
        if in_cluster:
            classifications.append(0)
        else:
            classifications.append(1)
    return classifications

def classify_anomalies(train_features, target_features):
    #トレーニングデータを使用したクラスタリング(クラス数2)
    kmeans = KMeans(n_clusters=2, random_state=0)
    kmeans.fit(train_features)
    centers = kmeans.cluster_centers_
    distances = pairwise_distances(train_features, centers)
    max_distances = np.max(distances, axis=0)

    # target_featuresの異常検知
    classifications = []
    for target in target_features:
        target = np.array(target).reshape(1, -1)
        target_distances = pairwise_distances(target, centers)
        closest_class = np.argmin(target_distances)
        if target_distances[0][closest_class] > max_distances[closest_class]:
            classifications.append(1)  # 異常
        else:
            classifications.append(0)  # 正常

    return classifications


def update_labels(conn, cursor, table, channel, anomaly_table, target_data, classifications):
    try:
        now_at = datetime.now(local_tz).strftime('%Y-%m-%d %H:%M:%S')
        for i, df in enumerate(target_data):
            new_detail = 2 if classifications[i] == 0 else 4
            ids = df['id'].tolist()
            ids_str = ', '.join(map(str, ids))

            query = f"UPDATE {table} SET detail = %s, reason = %s, updated_at = %s WHERE id IN ({ids_str})"
            cursor.execute(query, (new_detail, new_reason, now_at))

            if classifications[i] == 1:
                start = df.iloc[0]['dev_at'].strftime('%Y-%m-%d %H:%M:%S')
                end = df.iloc[-1]['dev_at'].strftime('%Y-%m-%d %H:%M:%S')
                cite = 2
                mode = "異常"
                query = f"""
                INSERT INTO {anomaly_table} (start, end, mode, created_at, channel, cite)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (start, end, mode, now_at, channel, cite))

        conn.commit()
        logging.info("Database updated successfully")
        return True

    except Exception as e:
        logging.error(f"Error updating database: {e}")
        conn.rollback()
        return False

def calculate_classifications(train_features_list, target_features_list):
    try:
        gmm = train_gmm(train_features_list)
        if gmm:
            classifications = classify_anomalies(gmm, target_features_list)
            return classifications
    except Exception as e:
        logging.error(f"Error classify_anomalies: {e}")


    try:
        if len(train_features_list) < 30:
            logging.error(f"トレーニングデータが不足しています: {e}")
        else:
            classifications = classify_anomalies(train_features_list, target_features_list)
            return classifications
    except Exception as e:
        logging.error(f"Error classify_anomalies: {e}")

    return None



async def handle_detect_request(conn, cursor, dbTable, dbTableAnomaly, channel):
    logging.info(f"detect start: {dbTable} {dbTableAnomaly} ch={channel}")
    try:
        train_original_data = get_sorted_train_data(cursor, dbTable, channel)
        target_original_data = get_sorted_target_data(cursor, dbTable, channel)

        if train_original_data and target_original_data:
            train_data = split_data(train_original_data)
            target_data = split_data(target_original_data)

            if train_data and target_data:
                train_data = check_and_remove_errors_from_dfs(train_data)
                target_data = check_and_remove_errors_from_dfs(target_data)

                if train_data and target_data:
                    train_features_list = calculate_features(train_data)
                    target_features_list = calculate_features(target_data)

                    if train_features_list and target_features_list:
                        classifications = calculate_classifications(train_features_list, target_features_list)

                    if classifications:
                        logging.debug(f"class: {classifications}")
                        return update_labels(conn, cursor, dbTable, channel, dbTableAnomaly, target_data, classifications)
        return True

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return False
