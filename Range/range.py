from binance.client import Client
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import time
import properties as pr
from binance.enums import *
from datetime import datetime, date, timezone, timedelta

duration5 = 5  # 5分間隔
duration20 = 20  # 20分間隔
duration50 = 50  # 50分間隔
# interval = 10  # 10分おきに売買判断
trading_amount = 1  # trading金額
df_sma5 = pd.DataFrame()  # 5分移動平均
df_sma20 = pd.DataFrame()  # 20分移動平均
df_sma50 = pd.DataFrame()  # 50分移動平均

# entry_status
ENTRY_STATUS1 = "1"
ENTRY_STATUS2 = "2"
ENTRY_STATUS3 = "3"
ENTRY_STATUS4 = "4"
ENTRY_STATUS5 = "5"
ENTRY_STATUS6 = "6"

# 1分足のローソクの本数
chart_data_max = 1439

# entryを行うためのステータスを３つもつ配列
enry_status_que = [0,0,0]

# 取引ボリューム
volume = 100

# client
binance = Client(pr.API_KEY, pr.SECRET_KEY, {"timeout": 20})

def main():
    """
    main run()
    """
    # chartData取得
    # 取得データフォーマット
    # 時間、
    for interval in range(0, 3600, 1):
        time.sleep(1)
        chart_data = get_chart_data()

        # 5,20,50分移動平均の取得
        # df_sma5.append()
        df_sma5_avg = calc_moving_avg(chart_data,duration5,chart_data_max)
        df_sma20_avg = calc_moving_avg(chart_data,duration20,chart_data_max)
        df_sma50_avg = calc_moving_avg(chart_data,duration50,chart_data_max)

        # entry_statusの取得
        avg_status = set_entry_status(df_sma5_avg,df_sma20_avg,df_sma50_avg)

        # entry配列にデータを追加＆削除
        del enry_status_que[0]
        enry_status_que.append(avg_status)

        # status取得
        # return long short stay
        entry_result = judge_entry_point(enry_status_que)
        print(entry_result)

        # entry
        if entry_result=="long":
            # longEntryとshortの精算
            create_long_entry()
            close_short_entry()
        elif entry_result=="short":
            # shortEntryとlongの精算
            create_short_entry()
            close_long_entry()


def get_chart_data():
    """
    1分足を1日分取得
    :return: data
    """
    data = binance.get_historical_klines(pr.symbol, Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
    return data


def calc_moving_avg(chart_data,duration,chart_data_max):
    """
    移動平均値を求める
    """
    sma_avg = 0
    for index in range(duration):
        sma_avg = sma_avg + float(chart_data[chart_data_max-index][4])
    return sma_avg/duration


def set_entry_status(df_sma5_avg,df_sma20_avg,df_sma50_avg):
    """
    今の移動平均線のステータスを取得する
    """
    # 1:短→中→長
    if df_sma5_avg>=df_sma20_avg>=df_sma50_avg:
        now_chart_status = 1
    # 2:中→短→長
    elif df_sma20_avg>=df_sma5_avg>=df_sma50_avg:
        now_chart_status = 2
    # 3:中→長→短
    elif df_sma20_avg>=df_sma50_avg>=df_sma5_avg:
        now_chart_status = 3
    # 4:長→中→短
    elif df_sma50_avg>=df_sma20_avg>=df_sma5_avg:
        now_chart_status = 4
    # 5:長→短→中
    elif df_sma50_avg>=df_sma5_avg>=df_sma20_avg:
        now_chart_status = 5
    # 6:短→長→中
    elif df_sma5_avg>=df_sma50_avg>=df_sma20_avg:
        now_chart_status = 6
    return now_chart_status


def judge_entry_point(enry_status_que):
    """
    トレンド変換の判定
    条件：
    interval直前のステータスが⑤⑥①の順番になっている:long
    interval直前のステータスが②③④の順番になっている:short
    それ意外:stay
    """
    if enry_status_que[0]==5 and enry_status_que[1]==6 and enry_status_que[2]==1:
        return "long"
    elif enry_status_que[0]==2 and enry_status_que[1]==3 and enry_status_que[2]==4:
        return "short"
    else:
        return "stay"


def create_long_entry():
    """
    long entry
    :return: create_entry_result:結果
    """
    order = binance.futures_create_order(symbol=pr.symbol, side=Client.SIDE_BUY, type='MARKET', quantity=volume)
    print("Enrty long!! symbol:",
            order["symbol"],
            "volume:",
            order["origQty"],
            "USDT time:",
            datetime.fromtimestamp(order["updateTime"]/1000))
    create_entry_result = "long order success!!"
    return create_entry_result

def create_short_entry():
    """
    short entry
    :return: create_entry_result 結果
    """
    order = binance.futures_create_order(symbol=pr.symbol, side=Client.SIDE_SELL, type='MARKET', quantity=volume)
    print("Enrty short!! symbol:",
          order["symbol"],
          "volume:",
          order["origQty"],
          "USDT time:",
          datetime.fromtimestamp(order["updateTime"]/1000))
    create_entry_result = "short order success!!"
    return create_entry_result

def close_long_entry():
    """
    long close
    :return: create_entry_result:結果
    """
    order = binance.futures_create_order(symbol=pr.symbol, side=Client.SIDE_SELL, type='MARKET', quantity=volume)
    print("Close long!! symbol:",
          order["symbol"],
          "volume:",
          order["origQty"],
          "USDT time:",
          datetime.fromtimestamp(order["updateTime"]/1000))
    create_entry_result = "close long success!!"
    return create_entry_result

def close_short_entry():
    """
    short close
    :return: create_entry_result 結果
    """
    order = binance.futures_create_order(symbol=pr.symbol, side=Client.SIDE_BUY, type='MARKET', quantity=volume)
    print("Close short!! symbol:",
          order["symbol"],
          "volume:",
          order["origQty"],
          "USDT time:",
          datetime.fromtimestamp(order["updateTime"]/1000))
    create_entry_result = "close short success!!"
    return create_entry_result

if __name__ == '__main__':
    main()