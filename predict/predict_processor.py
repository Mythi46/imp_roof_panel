import logging
from demand import handle_demand_request
from generate import handle_generate_request
from asyncio import Semaphore
from utils.sentry import send_message_to_sentry_err

# 最大同時実行数を制限
semaphore = Semaphore(5)

# clampごとの予測処理を行う関数
async def process_predict(clamp, conn, cursor):
    clamp_id = clamp['id']
    dbTable = f"dev_gen_{clamp_id}"
    ch_num=clamp['channel_num']

    async with semaphore:
        try:
            for ch in range(ch_num):
                channel = ch + 1

                # 条件に応じた処理を実行
                cname=clamp["class_name"]
                if cname and cname == "solar":
                    ok = await handle_generate_request(conn, cursor, dbTable, channel, clamp["city_code"])
                else:
                    ok = await handle_demand_request(conn, cursor, dbTable, channel)

                if not ok:
                    return

        except Exception as e:
            send_message_to_sentry_err(f"processing prediction clampid={clamp_id}: {e}")
