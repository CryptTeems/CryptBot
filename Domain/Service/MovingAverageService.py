import time
import json
from logging import getLogger, config
from binance.client import Client
from Domain.Service import MovingAverageProperties as pr
from Infrastructure.Client.TickerInfoClient import TickerInfoClient
from Infrastructure.Client.SettlementClient import SettlementClient
from Infrastructure.Client import TickerInfoClient as ticker
from Infrastructure.Client import SettlementClient
from logging import getLogger, config
import logging


class MovingAverageService:
    def get_chart_data(self):
        ticker_info = TickerInfoClient(self.logger)
        # chartDataの取得
        chart_data = ticker_info.get_chart_data(pr.SYMBOL, Client.KLINE_INTERVAL_1MINUTE, pr.ONE_DAY)
        return chart_data

    def get_chart_status(self, chart_data):
        """
            移動平均線の並びからステータスを返す
            :return:
            """
        ticker_info = TickerInfoClient(self.logger)
        # 移動平均線取得
        df_short_avg = ticker_info.get_moving_avg(pr.DURATION_SHORT_TERM, chart_data)
        df_medium_avg = ticker_info.get_moving_avg(pr.DURATION_MEDIUM_TERM, chart_data)
        df_long_avg = ticker_info.get_moving_avg(pr.DURATION_LONG_TERM, chart_data)

        # 現在の平均線からステータスポジションの取得
        avg_status = set_entry_status(df_short_avg, df_medium_avg, df_long_avg)
        return avg_status

    def get_status_history(self, chart_status_que, avg_status):
        """
            移動平均線の履歴情報の取得
            :param chart_status_que:
            :param status:
            :return:
            """
        while chart_status_que[0] == 0 or chart_status_que[1] == 0 or chart_status_que[2] == 0:
            chart_status_que = init_chart_status_que(chart_status_que, avg_status)
        return chart_status_que

    def judge_entry(self, chart_status_que):
        """
            トレンド変換の判定
            :return
                chart_status_queステータスが④⑤⑥:long
                chart_status_queステータスが①②③:short
                それ意外:stay
            """
        if chart_status_que == pr.ENTRY_LONG_STATUS_QUE:
            return pr.ENTRY_LONG_STATUS
        elif chart_status_que == pr.ENTRY_SHORT_STATUS_QUE:
            return pr.ENTRY_SHORT_STATUS
        else:
            return pr.ENTRY_STAY_STATUS

    def judge_close(self, chart_status_que):
        """
            judge close position
            :return
                chart_status_queステータスが①②③:close long
                chart_status_queステータスが④⑤⑥:close short
                それ意外:stay
            """
        if chart_status_que == pr.CLOSE_LONG_STATUS_QUE:
            return pr.CLOSE_LONG_STATUS
        elif chart_status_que == pr.CLOSE_SHORT_STATUS_QUE:
            return pr.CLOSE_SHORT_STATUS
        else:
            return pr.CLOSE_STAY_STATUS

    def close_entry(self, judge_close_status):
        """
            close処理
            """
        # 現在のpositionの取得
        volume = 0
        close_settlement = SettlementClient(self.logger, self.symbol, self.settlement_type, volume)
        now_order = close_settlement.get_position()

        # currentSide判定 entryをしているときのside
        current_side = close_settlement.get_current_position_side(now_order)

        # current volume
        current_volume = close_settlement.get_current_quantity(now_order)
        self.logger.info(judge_close_status)
        self.logger.info(current_side)
        # 1:close long
        if judge_close_status == pr.CLOSE_LONG_STATUS \
                and current_side == Client.SIDE_BUY:
            close_settlement.close_long_entry(current_volume)
        # 2:close short
        elif judge_close_status == pr.CLOSE_SHORT_STATUS \
                and current_side == Client.SIDE_BUY:
            close_settlement.close_short_entry(current_volume)

    def entry(self, judge_entry_status, mark_price):
        """
        entry処理
        """
        # 初期化
        entry_settlement = SettlementClient(self.logger, self.symbol, self.settlement_type, self.entry_volume)
        # current volume
        now_order = entry_settlement.get_position()
        # long entry
        if judge_entry_status == pr.ENTRY_LONG_STATUS:
            self.logger.info("long entryを実行します")
            stop_price = mark_price * 0.9
            entry_settlement.create_long_entry(stop_price)
        # short entry
        elif judge_entry_status != pr.ENTRY_SHORT_STATUS:
            self.logger.info("short entryを実行します")
            stop_price = mark_price * 1.1
            entry_settlement.create_short_entry(stop_price)

    def __init__(self, logger, sym, side, settlement_type, entry_volume):
        self.judge_close_status = None
        self.logger = logger
        self.symbol = sym
        self.side = side
        self.settlement_type = settlement_type
        self.entry_volume = entry_volume


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


def init_chart_status_que(que, status):
    """
    chart_status_queの初期化処理
    :param que:chart_status_que
    :param status: chart_status
    :return: que
    """
    status_queue = update_chart_status_que(que, status)
    return status_queue


def update_chart_status_que( chart_status_que, status):
    """
    chartから取得した、ステータスポジション履歴の更新
    :return: entry_status_que
    """
    del chart_status_que[0]
    chart_status_que.append(status)
    return chart_status_que


def get_price(sym):
    mark_price = ticker.get_mark_price(sym)
    return mark_price