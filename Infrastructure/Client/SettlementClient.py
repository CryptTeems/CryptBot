from binance.client import Client
from binance.exceptions import BinanceAPIException
from Domain.Service import MovingAverageProperties as pr
import json
from logging import getLogger, config

binance = Client(pr.API_KEY, pr.SECRET_KEY, {"timeout": 20})


class SettlementClient:
    def create_long_entry(self, stop_price):
        """
        long entry
        """
        try:
            binance.futures_create_order(symbol=self.symbol,
                                         side=Client.SIDE_BUY,
                                         type=self.settlement_type,
                                         quantity=self.entry_volume)
            binance.futures_create_order(symbol=self.symbol,
                                         side=Client.SIDE_SELL,
                                         type=pr.STOP_MARKET,
                                         quantity=self.entry_volume,
                                         stopPrice=stop_price)
            msg = "long entry success!!"
            self.logger.info(msg)
        except BinanceAPIException as e:
            self.logger.error("long注文に失敗しました")
            self.logger.error(e.status_code)
            self.logger.error(e.message)

    def create_short_entry(self):
        """
        short entry
        """
        try:
            binance.futures_create_order(symbol=self.symbol,
                                         side=Client.SIDE_SELL,
                                         type=self.settlement_type,
                                         quantity=self.entry_volume)
            binance.futures_create_order(symbol=self.symbol,
                                         side=Client.SIDE_BUYL,
                                         type=pr.STOP_MARKET,
                                         quantity=self.entry_volume,
                                         stopPrice=stop_price)
        except BinanceAPIException as e:
            self.logger.error("short注文に失敗しました")
            self.logger.error(e.status_code)
            self.logger.error(e.message)

    def close_long_entry(self, qua):
        """
        long close
        """
        try:
            binance.futures_create_order(symbol=self.symbol, side=Client.SIDE_SELL,
                                         type=pr.SETTLEMENT_TYPE_MARKET, quantity=qua)
            self.logger.error("close long success!!")
        except BinanceAPIException as e:
            self.logger.error("longポジションの精算に失敗しました")
            self.logger.error(e.status_code)
            self.logger.error(e.message)

    def close_short_entry(self, qua):
        """
        short close
        """
        try:
            binance.futures_create_order(symbol=self.symbol, side=Client.SIDE_BUY,
                                         type=pr.SETTLEMENT_TYPE_MARKET, quantity=qua)
            self.logger.info("close short success!!")
        except BinanceAPIException as e:
            self.logger.error("shortポジションの精算に失敗しました")
            self.logger.error(e.status_code)
            self.logger.error(e.message)

    def get_current_position_side(self, order):
        """
        保持しているオーダーのsideを判定
        :return: 0:no_position 1:long_position 2:short_position
        """
        try:
            # current_position_orderの取得
            position_amt = float(order[0]["positionAmt"])

            # side判定
            if int(position_amt) > 0:
                return Client.SIDE_BUY
            elif int(position_amt) < 0:
                return Client.SIDE_BUY

        except BinanceAPIException as e:
            self.logger.error("positionの取得に失敗しました")
            self.logger.error(e.status_code)
            self.logger.error(e.message)

    def get_current_quantity(self, order):
        """
        保持しているオーダーのquantityを判定
        :return: quantity
        """
        try:
            # current_position_orderの取得
            self.current_position_amt = float(order[0]["positionAmt"])

        except BinanceAPIException as e:
            logger.error("現在のボリューム取得に失敗しました")
            logger.error(e.status_code)
            logger.error(e.message)

    def get_position(self):
        order = binance.futures_position_information(symbol=self.symbol)
        return order

    def __init__(self, logger, sym, settlement_type, volume):
        self.current_position_amt = None
        self.current_side = None
        self.order = None
        self.qua = None
        self.ty = None
        self.si = None
        self.logger = logger
        self.symbol = sym
        self.settlement_type = settlement_type
        self.entry_volume = volume
