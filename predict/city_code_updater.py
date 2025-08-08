import logging
import pandas as pd
import re
from geopy.geocoders import Nominatim
from geopy.distance import geodesic  # 緯度経度からの距離計算に使用


geolocator = Nominatim(user_agent="geoapiExercises")

# TSVファイルの読み込み
# 緯度経度から市町村コードを取得するためのデータを作成
df = pd.read_csv('/app/data/town.tsv', delimiter='\t', header=0, names=["city_code", "prefecture", "city_name", "latitude", "longitude"])




# 正規表現を使った市町村名検索関数
def find_city_code(city_name, lat, lon):
    # 市町村名の正規表現検索（末尾の「市」「町」「村」などを省略して部分一致検索）
    pattern = re.compile(re.escape(city_name).replace("市", "").replace("町", "").replace("村", ""))
    matches = df[df["city_name"].str.contains(pattern, na=False)]

    if not matches.empty:
        # 候補が複数ある場合、緯度経度で最も近い市町村を選ぶ
        matches.loc[:, "distance"] = matches.apply(lambda row: geodesic((lat, lon), (row["latitude"], row["longitude"])).kilometers, axis=1)

        nearest_match = matches.loc[matches["distance"].idxmin()]
        return nearest_match["city_code"]
    else:
        logging.warning(f"No matching city_code found for {city_name}")
        return None

# 緯度経度から市町村名を取得してcity_codeを決定する関数
def get_city_code_from_latlon(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), language="ja")
        if location and "address" in location.raw:
            address = location.raw["address"]
            city_name = address.get("city") or address.get("town") or address.get("village") or address.get("municipality")
            logging.info(f"Geocoded city_name: {city_name}")

            # 正規表現でcity_nameと一致するcity_codeを取得
            return find_city_code(city_name, lat, lon)
        else:
            logging.warning(f"No address found for lat: {lat}, lon: {lon}")
            return None

    except Exception as e:
        logging.error(f"Error in geocoding lat: {lat}, lon: {lon}: {e}")
        return None
    

def update_city_code(cursor, clamp_id, city_code):
    try:
        update_query = "UPDATE clamps SET city_code = %s WHERE id = %s;"
        cursor.execute(update_query, (int(city_code), clamp_id))  # intに変換
        logging.info(f"Updated city_code for clamp_id {clamp_id} to {city_code}")

    except Exception as e:
        logging.error(f"Database error on update for clamp_id {clamp_id}: {e}")

