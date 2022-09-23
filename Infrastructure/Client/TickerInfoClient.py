from binance.client import Client
from Domain.Service import MovingAverageProperties as pr
import json
from logging import getLogger, config
import logging
import time

binance = Client(pr.API_KEY, pr.SECRET_KEY, {"timeout": 20})


class TickerInfoClient:
    def get_chart_data(self, sym, interval, lange):
        """
        1分足を1日分取得
        :return: data
        """
        self.sym = sym
        self.interval = interval
        self.lange = lange

        for _ in range(10):  # 最大10回実行
            try:
                chart_data = binance.get_historical_klines(
                    self.sym,
                    self.interval,
                    self.lange)
                return chart_data
            except Exception as e:
                self.logger.info("チャートデータの取得に失敗しました")
                time.sleep(1)
            else:
                break
        else:
            self.logger.info("チャートデータの取得最大回数に達しました")


    def get_moving_avg(self, duration, chart_data):
        """
        移動平均値を求める
        """
        self.duration = duration

        try:
            # 1分足のローソクの本数
            chart_data_max = len(chart_data) - 1
            sma_avg = 0.00
            for index in range(self.duration):
                sma_avg = sma_avg + float(chart_data[chart_data_max - index][4])
            return sma_avg / duration
        except:
            self.logger.error("移動平均線取得に失敗しました")

    def __init__(self, logger):
        self.duration = None
        self.lange = None
        self.interval = None
        self.sym = None
        self.logger = logger


def get_mark_price(sym):
    coin_info = binance.futures_mark_price(symbol=sym)
    return coin_info['markPrice']