import logging
from db import db_connect, get_cursor
import mysql.connector
import asyncio
from asyncio import Semaphore
import logging
from frame import handle_frame_request
from detect import handle_detect_request
from train_data import train_data_check
from classification import handle_classification_request, get_all_teacher_data, train_model

# 最大同時実行数を10に制限
semaphore = Semaphore(5)


# clamp list取得
def get_clamps():
    conn = None
    cursor = None
    try:
        conn = db_connect('napi_db')
        cursor = get_cursor(conn)
        if not conn or not cursor:
            return None

        query = """
                SELECT clamps.id, clamps.channel_num, 
                clamp_details.class_id, clamp_details.confidence, clamp_details.updated_at 
                FROM clamps
                INNER JOIN clamp_details ON clamps.id = clamp_details.clamp_id;
                """
        cursor.execute(query)
        data = cursor.fetchall()

        return data

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None

    finally:
        # カーソルと接続をクローズ
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


async def process_clamp(clamp):
        clampId = clamp['id']
        dbTable = f"dev_gen_{clampId}"

        async with semaphore:
            conn = None
            cursor = None
            try:
                conn = db_connect('napi_db')
                if not conn:
                    return

                cursor = get_cursor(conn)
                if not cursor:
                    return
                
                connClamp = db_connect('clamp_db')
                if not connClamp:
                    return

                cursorClamp = get_cursor(connClamp)
                if not cursorClamp:
                    return
                

                # TODO : channel 1固定　ゆくゆくメインチャンネルを設定し、それだけで判定する
                channel = 1

                # frame区画の取得
                ok = await handle_frame_request(connClamp, cursorClamp, clampId, channel)
                if not ok:
                    return
                
                # 測定対象物推論
                ok = await handle_classification_request(conn, cursor, cursorClamp, dbTable, channel, clamp)
                if not ok:
                    return

# TODO: 異常検知は一旦なし➡dev_gen_frameに引っ越しするため
                # ok, exist=train_data_check(conn, cursor, dbTable, channel)
                # if not ok:
                #     return

                # if exist:
                #     ok = await handle_detect_request(conn, cursor, dbTable, f"dev_fault_{clampId}", channel)
                #     if not ok:
                #         return

            except Exception as e:
                logging.error(f"processing clampid={clampId}: {e}")

            finally:
                if conn:
                    conn.close()
                if cursor:
                    cursor.close()
                if connClamp:
                    connClamp.close()
                if cursorClamp:
                    cursorClamp.close()

async def main():
    try:
        clamps = get_clamps()
        if clamps is None:
            logging.info("No clamps data found.")
            return

        ret = get_all_teacher_data()
        if not ret:
            logging.error("No teacher data found.")
            return
        
        ret = train_model()
        if not ret:
            logging.error("Model training failed.")
            return

        tasks = [process_clamp(clamp) for clamp in clamps]
        await asyncio.gather(*tasks)

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == '__main__':
    logging.info("start classification")
    asyncio.run(main())
    logging.info("fin classification")