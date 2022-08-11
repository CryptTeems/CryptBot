import json
import time
import properties as pr
from datetime import datetime, date, timezone, timedelta
import json
from logging import getLogger, config

# layer import
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException

duration_short_term = 7  # 短期線間隔
duration_medium_term = 25  # 中期線間隔
duration_long_term = 99  # 長期線間隔
df_sma_short = pd.DataFrame()  # 5分移動平均
df_sma_mid = pd.DataFrame()  # 20分移動平均
df_sma_long = pd.DataFrame()  # 50分移動平均

# entry_status
ENTRY_STATUS1 = "1"
ENTRY_STATUS2 = "2"
ENTRY_STATUS3 = "3"
ENTRY_STATUS4 = "4"
ENTRY_STATUS5 = "5"
ENTRY_STATUS6 = "6"

# entryを行うためのステータスを３つもつ配列
entry_status_que = [0, 0, 0]

# 取引ボリューム
volume = 100

# client
binance = Client(pr.API_KEY, pr.SECRET_KEY, {"timeout": 20})

# log message
statu_queue = " queue"
short = " MA7:"
medium = " MA25:"
long = " MA99:"
entry_judge = "judge:"

with open('../log/log_config.json', 'r') as f:
    log_conf = json.load(f)

config.dictConfig(log_conf)

logger = getLogger(__name__)
global chart_data


def main():
    """
    main run()
    """

    # print("バッチの実行が開始されました")
    logger.info("バッチの実行が開始されました")

    while True:
        # 1sおきに実行
        time.sleep(1)
        try:
            # chartDataの取得
            chart_data = get_chart_data()
            # 5,20,50分移動平均の取得
            # 1分足のローソクの本数
            chart_data_max = len(chart_data) - 1
            df_short_avg = calc_moving_avg(chart_data, duration_short_term, chart_data_max)
            df_medium_avg = calc_moving_avg(chart_data, duration_medium_term, chart_data_max)
            df_long_avg = calc_moving_avg(chart_data, duration_long_term, chart_data_max)

            # 現在の平均線からステータスポジションの取得
            avg_status = set_entry_status(df_short_avg, df_medium_avg, df_long_avg)

            # entryQueueの初期化処理
            if entry_status_que[0] == 0 or entry_status_que[1] == 0 or entry_status_que[2] == 0:
                update_entry_status_que(entry_status_que, avg_status)

            # 直前のチャートステータスと差分がある場合、Queueの更新とentryのジャッジを行う
            elif entry_status_que[2] != avg_status:
                # Queue履歴更新
                update_entry_status_que(entry_status_que, avg_status)
                # entryするか判定のためステータス取得
                # return:long short stay
                entry_result = judge_entry_point(entry_status_que)
                msg = entry_judge + str(entry_result) + statu_queue + str(entry_status_que) + short + str(
                    df_short_avg) + medium + str(df_medium_avg) + long + str(df_long_avg)
                logger.info(msg)

                # entry judge
                if entry_result == "long":
                    # longEntryとshortの精算
                    create_long_entry()
                    close_short_entry()
                elif entry_result == "short":
                    # shortEntryとlongの精算
                    create_short_entry()
                    close_long_entry()

        except BinanceAPIException as e:
            logger.error(e.status_code)
            logger.error(e.message)
        finally:
            del (chart_data)


def get_chart_data():
    """
    1分足を1日分取得
    :return: data
    """
    data = None
    try:
        while data is None:
            data = binance.get_historical_klines(pr.symbol, Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
            return data
    except:
        logger.error("チャートデータの取得に失敗しました")


def calc_moving_avg(chart_datas, duration, chart_data_max):
    """
    移動平均値を求める
    """
    sma_avg = 0
    for index in range(duration):
        sma_avg = sma_avg + float(chart_datas[chart_data_max - index][4])
    return sma_avg / duration


def update_entry_status_que(entry_status_ques, avg_status):
    """
    chartから取得した、ステータスポジション履歴の更新
    :return: entry_status_que
    """
    del entry_status_ques[0]
    entry_status_ques.append(avg_status)
    return entry_status_ques


def set_entry_status(short_avg, mid_avg, long_avg):
    """
    今の移動平均線のステータスを取得する
    """
    # 1:短→中→長
    if short_avg >= mid_avg >= long_avg:
        now_chart_status = 1
    # 2:中→短→長
    elif mid_avg >= short_avg >= long_avg:
        now_chart_status = 2
    # 3:中→長→短
    elif mid_avg >= long_avg >= short_avg:
        now_chart_status = 3
    # 4:長→中→短
    elif long_avg >= mid_avg >= short_avg:
        now_chart_status = 4
    # 5:長→短→中
    elif long_avg >= short_avg >= mid_avg:
        now_chart_status = 5
    # 6:短→長→中
    elif short_avg >= long_avg >= mid_avg:
        now_chart_status = 6
    return now_chart_status


def judge_entry_point(enry_status_que):
    """
    トレンド変換の判定
    条件：
    enry_status_queステータスが⑤⑥①の順番になった初回:long
    enry_status_queステータスが②③④の順番になった初回:short
    それ意外:stay
    """
    if enry_status_que[0] == 5 and enry_status_que[1] == 6 and enry_status_que[2] == 1:
        return "long"
    elif enry_status_que[0] == 2 and enry_status_que[1] == 3 and enry_status_que[2] == 4:
        return "short"
    else:
        return "stay"


def create_long_entry():
    """
    long entry
    """
    try:
        binance.futures_create_order(symbol=pr.symbol, side=Client.SIDE_BUY, type="MARKET", quantity=volume)
        msg = "Entry long!! long order success!!"
        logger.info(msg)
    except BinanceAPIException as e:
        logger.error("long注文に失敗しました")
        logger.error(e.status_code)
        logger.error(e.message)


def create_short_entry():
    """
    short entry
    """
    try:
        binance.futures_create_order(symbol=pr.symbol, side=Client.SIDE_SELL, type='MARKET', quantity=volume)
        msg = "Entry short!! short order success!!"
        logger.info(msg)
    except BinanceAPIException as e:
        logger.error("short注文に失敗しました")
        logger.error(e.status_code)
        logger.error(e.message)


def close_long_entry():
    """
    long close
    """
    try:
        binance.futures_create_order(symbol=pr.symbol, side=Client.SIDE_SELL, type='MARKET', quantity=volume)
        msg = "Close long!! close long success!!"
        logger.info(msg)
    except BinanceAPIException as e:
        logger.error("longポジションの精算に失敗しました")
        logger.error(e.status_code)
        logger.error(e.message)


def close_short_entry():
    """
    short close
    """
    try:
        binance.futures_create_order(symbol=pr.symbol, side=Client.SIDE_BUY, type='MARKET', quantity=volume)
        msg = "Close short!! close short success!!"
        logger.info(msg)
    except BinanceAPIException as e:
        logger.error("shortポジションの精算に失敗しました")
        logger.error(e.status_code)
        logger.error(e.message)


# local 動作確認用
if __name__ == '__main__':
    main()
