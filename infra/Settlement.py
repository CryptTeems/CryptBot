from binance.client import Client
from binance.exceptions import BinanceAPIException
import properties as pr

binance = Client(pr.API_KEY, pr.SECRET_KEY, {"timeout": 20})


class Settlement:
    def create_long_entry(sym, si, ty, qua):
        """
        long entry
        """
        try:
            binance.futures_create_order(symbol=sym, side=si, type=ty, quantity=qua)
            msg = "long entry success!!"
            logger.info(msg)
        except BinanceAPIException as e:
            logger.error("long注文に失敗しました")
            logger.error(e.status_code)
            logger.error(e.message)

    def create_short_entry(sym, si, ty, qua):
        """
        short entry
        """
        try:
            binance.futures_create_order(symbol=sym, side=si, type=ty, quantity=qua)
        except BinanceAPIException as e:
            logger.error("short注文に失敗しました")
            logger.error(e.status_code)
            logger.error(e.message)

    def close_long_entry(sym, si, ty, qua):
        """
        long close
        """
        try:
            binance.futures_create_order(symbol=sym, side=si, type=ty, quantity=qua)
        except BinanceAPIException as e:
            logger.error("longポジションの精算に失敗しました")
            logger.error(e.status_code)
            logger.error(e.message)

    def close_short_entry(sym, si, ty, qua):
        """
        short close
        """
        try:
            binance.futures_create_order(symbol=sym, side=si, type=ty, quantity=qua)
            msg = "short entry success!!"
            logger.info(msg)
        except BinanceAPIException as e:
            logger.error("shortポジションの精算に失敗しました")
            logger.error(e.status_code)
            logger.error(e.message)


def current_position_side(order):
    """
    保持しているオーダーのsideを判定
    :return: 0:no_position 1:long_position 2:short_position
    """
    try:
        # current_position_orderの取得
        position_amt = float(order[0]["positionAmt"])

        # side判定
        if int(position_amt) > 0:
            return 1
        elif int(position_amt) < 0:
            return 2
        else:
            return 0

    except BinanceAPIException as e:
        logger.error("positionの取得に失敗しました")
        logger.error(e.status_code)
        logger.error(e.message)


def get_current_quantity(order):
    """
    保持しているオーダーのquantityを判定
    :return: quantity
    """
    try:
        # current_position_orderの取得
        position_amt = float(order[0]["positionAmt"])
        return abs(position_amt)

    except BinanceAPIException as e:
        logger.error("現在のボリューム取得に失敗しました")
        logger.error(e.status_code)
        logger.error(e.message)