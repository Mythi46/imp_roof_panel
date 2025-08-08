import sys
import logging
import asyncio
from db import db_connect, get_cursor
from predict_processor import process_predict
from utils.sentry import send_message_to_sentry_err
from utils.log_config import setup_logging
setup_logging()


# clamp list取得
def get_clamps(cursor):
    try:
        # クエリを実行
        query = """
        SELECT clamps.id, clamps.channel_num, clamps.lat, clamps.lon, classes.name AS class_name, centers.city_code
        FROM clamps
        INNER JOIN clamp_details ON clamps.id = clamp_details.clamp_id
        LEFT JOIN center_maps ON clamps.center_map_id = center_maps.id
        LEFT JOIN centers ON center_maps.center_id = centers.id
        LEFT JOIN classes ON clamp_details.class_id = classes.id;
        """
        cursor.execute(query)
        data = cursor.fetchall()

        return data

    except Exception as e:
        send_message_to_sentry_err(f"An error occurred: {e}")
        return None


async def main():
    try:
        napi_conn = db_connect('napi_db')
        napi_cursor = get_cursor(napi_conn)
        if not napi_conn or not napi_cursor:
            send_message_to_sentry_err("Database connection failed.")
            return
        
        clamps = get_clamps(napi_cursor)
        if clamps is None:
            logging.info("No clamps data found.")
            return

        conn = db_connect('clamp_db')
        cursor = get_cursor(conn)
        if not conn or not cursor:
            send_message_to_sentry_err("clamp Database connection failed.")
            return

        # 各clampについて予測処理を開始
        tasks = [process_predict(clamp, conn, cursor) for clamp in clamps]
        await asyncio.gather(*tasks)

    except Exception as e:
        send_message_to_sentry_err(f"An error occurred: {e}")

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
            
        if napi_cursor is not None:
            napi_cursor.close()
        if napi_conn is not None:
            napi_conn.close()

if __name__ == '__main__':
    logging.info("start predict")
    asyncio.run(main())
    logging.info("fin predict")
