import logging
import mysql.connector
from mysql.connector import Error
from modelsclamp import DevGen
from datetime import timedelta

def get_train_data(cursor, table, channel):
    query = f"SELECT * FROM {table} WHERE channel = %s AND frame = {DevGen.DataFrameEnd} ORDER BY id ASC LIMIT 40"
    cursor.execute(query, (channel,))
    data = cursor.fetchall()
    return data

def train_data_check(conn, cursor, gen_table_name, channel):
    try:
        oldest_dev_gen = get_train_data(cursor, gen_table_name, channel)

        studyc = 0
        c = 0
        start = -1
        end = -1

        for i, v in enumerate(oldest_dev_gen):
            if v['label'] == DevGen.DataLabelNone:
                if start < 0:
                    start = i
                elif c<=30:
                    end = i
                c += 1
            else:
                # 途中に違う判定データがあったらリセット
                c = 0
                start = -1
                end = -1
                if v['label'] == DevGen.DataLabelGoodTeach:
                    studyc += 1

        if studyc >= 30:
            # 十分に教師データあり
            # 異常検知呼び出し
            return True,True

        if c < 30:
            # 教師にすべきデータが十分にたまってない
            logging.info(f"not enogth study data")
            return True,False

        # startの時間に1分追加
        new_start_time = oldest_dev_gen[start]['dev_at'] + timedelta(minutes=1)

        logging.debug("updating first study data register %s to %s", new_start_time, oldest_dev_gen[end]['dev_at'])

        update_query = f"""
            UPDATE {gen_table_name}
            SET label = {DevGen.DataLabelGoodTeach}
            WHERE dev_at BETWEEN %s AND %s
        """
        cursor.execute(update_query, (new_start_time, oldest_dev_gen[end]['dev_at']))
        conn.commit()
        return True,True

    except Error as e:
        logging.error("error updating committed status: %s", str(e))
        return False,False