import pandas as pd
import logging
import logconf
from modelsclamp import DevGen
import pytz
from datetime import datetime

local_tz = pytz.timezone('Asia/Tokyo')



def get_latest_dev_gen_data(cursor, clampId, channel):
    # Define the table names
    genTable = f"dev_gen_{clampId}"
    frameTable = f"dev_gen_frame_{clampId}"

    # SQL query to get the latest dev_gen data for the specified channel
    query = f"""
        SELECT g.*
        FROM {frameTable} AS f
        INNER JOIN {genTable} AS g ON g.id = f.end_dev_gen_id
        WHERE g.channel = %s and g.cite<>{DevGen.DataCiteGen}
        ORDER BY g.dev_at DESC
        LIMIT 1;
    """

    # Execute the query and fetch the data
    cursor.execute(query, (channel,))
    data = cursor.fetchone()
    return data


"""
frame登録(/frame)用関数
"""
def get_sorted_frame_0_data(cursor, clampId, channel):
    genTable = f"dev_gen_{clampId}"
    
    latest_data = get_latest_dev_gen_data(cursor, clampId, channel)
    
    if latest_data:
        latest_dev_at = latest_data['dev_at']
        
        query = f"""
            SELECT *
            FROM {genTable}
            WHERE channel = %s AND dev_at > %s
            ORDER BY dev_at;
        """
        cursor.execute(query, (channel, latest_dev_at))
    else:
        query = f"""
            SELECT *
            FROM {genTable}
            WHERE channel = %s
            ORDER BY dev_at;
        """
        cursor.execute(query, (channel,))

    # Fetch and return all future data
    future_data = cursor.fetchall()
    return future_data

# Frameを修正する関数
def update_frame(data, on_to_off_border=0.1, off_to_on_border=0.5):
    off_sequence = 0
    on_flag = 0
    first_index = -1
    last_index = -1

    sequence_id_pairs = []

    for index, row in enumerate(data):
        if on_flag == 0:
            if row['value'] > off_to_on_border:
                first_index = index
                on_flag = 1
                off_sequence = 0
        else:
            if row['value'] < on_to_off_border:
                off_sequence += 1
                if off_sequence >= 20:
                    last_index = index - 20
                    on_flag = 0
                    first_id = data[first_index]['id']
                    last_id = data[last_index]['id']
                    
                    sequence_id_pairs.append((first_id, last_id))
            else:
                off_sequence = 0

    return sequence_id_pairs

# データベースにFrameを更新する関数
def update_db_frame(conn, cursor, clampId, sequence_id_pairs):
    frameTable = f"dev_gen_frame_{clampId}"

    query = f"""
        INSERT INTO {frameTable} (start_dev_gen_id, end_dev_gen_id, label) VALUES (%s, %s, 0);
    """
    values = sequence_id_pairs

    logging.debug(f"[update_db_frame] SQL Query Template: {query.strip()} inserted={len(sequence_id_pairs)} pairs")
    cursor.executemany(query, values)
    conn.commit()

async def handle_frame_request(conn, cursor, clampId, channel):
    try:
        frame_0_data = get_sorted_frame_0_data(cursor, clampId, channel)
        if not frame_0_data:
            return True

        sequence_id_pairs = update_frame(frame_0_data)
        if not sequence_id_pairs:
            return True

        update_db_frame(conn, cursor, clampId, sequence_id_pairs)
        conn.commit()
        return True


    except Exception as e:
        logging.error(f"An error occurred: {e}")
        conn.rollback()
        return False
