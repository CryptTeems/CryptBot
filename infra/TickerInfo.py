from binance.client import Client
from binance.exceptions import BinanceAPIException
import properties as pr

binance = Client(pr.API_KEY, pr.SECRET_KEY, {"timeout": 20})


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
