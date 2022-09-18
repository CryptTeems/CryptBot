import time
import MovingAverageProperties as pr
import json
from logging import getLogger, config
import binance
from binance.client import Client
from binance.exceptions import BinanceAPIException
from infra import Settlement as st
from infra import TickerInfo as ticker

duration_short_term = 7  # 短期線間隔
duration_medium_term = 25  # 中期線間隔
duration_long_term = 99  # 長期線間隔

# entry_status
ENTRY_STATUS1 = "1"
ENTRY_STATUS2 = "2"
ENTRY_STATUS3 = "3"
ENTRY_STATUS4 = "4"
ENTRY_STATUS5 = "5"
ENTRY_STATUS6 = "6"

# 取引ボリューム
volume = 0.25

# client
binance = Client(pr.API_KEY, pr.SECRET_KEY, {"timeout": 20})

# log message
statu_queue = ", queue"
short = " MA7:"
medium = " MA25:"
long = " MA99:"
entry_judge = " judge:"
current_side_msg = "current_side:"

# todo logRename path変更
with open('../log/log_config.json', 'r') as f:
    log_conf = json.load(f)
config.dictConfig(log_conf)
logger = getLogger(__name__)


def main():
    """
    main run()
    """
    logger.info("バッチの実行が開始されました")

    # entryを行うためのステータスを３つもつ配列
    chart_status_que = [0, 0, 0]

    while True:
        # 1sおきに実行
        time.sleep(1)
        try:
            # chartDataの取得
            chart_data = ticker.get_chart_data()

            # 1分足のローソクの本数
            chart_data_max = len(chart_data) - 1

            # 短中長の移動平均線取得
            df_short_avg = ticker.calc_moving_avg(chart_data, duration_short_term, chart_data_max)
            df_medium_avg = ticker.calc_moving_avg(chart_data, duration_medium_term, chart_data_max)
            df_long_avg = ticker.calc_moving_avg(chart_data, duration_long_term, chart_data_max)

            # 現在の平均線からステータスポジションの取得
            avg_status = set_entry_status(df_short_avg, df_medium_avg, df_long_avg)

            # entryQueueの初期化処理
            while chart_status_que[0] == 0 or chart_status_que[1] == 0 or chart_status_que[2] == 0:
                chart_status_que = init_chart_status_que(chart_status_que, avg_status)

            # 直前のチャートステータスと差分がある場合、Queueの更新とentryのジャッジを行う
            if chart_status_que[2] != avg_status:
                # 現在のpositionの取得
                now_order = binance.futures_position_information(symbol=pr.symbol)

                # currentSide判定
                # 0:no_position 1:long 2:short
                current_side = st.current_position_side(now_order)
                # current volume判定
                current_volume = st.get_current_quantity(now_order)

                # Queue履歴更新
                update_chart_status_que(chart_status_que, avg_status)

                # entry判定
                # 1:long 2:short 0:stay
                judgment_entry_result = judge_entry(chart_status_que)

                # close判定
                # 0:stay 1:close long 2:close short
                judgment_close_result = judge_close(chart_status_que)

                msg = current_side_msg + str(current_side) + statu_queue + str(chart_status_que) + short + str(
                    df_short_avg) + medium + str(df_medium_avg) + long + str(df_long_avg)
                logger.info(msg)

                # entry
                entry(pr.symbol, "MARKET", volume, judgment_entry_result)

                # ポジションを解除
                close_entry(pr.symbol, "MARKET", current_volume, current_side, judgment_close_result)

        except BinanceAPIException as e:
            logger.error(e.status_code)
            logger.error(e.message)
        finally:
            del chart_data


def update_chart_status_que(chart_status_que, avg_status):
    """
    chartから取得した、ステータスポジション履歴の更新
    :return: entry_status_que
    """
    del chart_status_que[0]
    chart_status_que.append(avg_status)
    return chart_status_que


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


def judge_entry(chart_status_que):
    """
    トレンド変換の判定
    :return
        chart_status_queステータスが④⑤⑥:long
        chart_status_queステータスが①②③:short
        それ意外:stay
    """
    if chart_status_que[0] == 4 and chart_status_que[1] == 5 and chart_status_que[2] == 6:
        return 1
    elif chart_status_que[0] == 1 and chart_status_que[1] == 2 and chart_status_que[2] == 3:
        return 2
    else:
        return 0


def judge_close(chart_status_que):
    """
    judge close position
    :return
        chart_status_queステータスが①②③:close long
        chart_status_queステータスが④⑤⑥:close short
        それ意外:stay
    """
    if chart_status_que[0] == 1 and chart_status_que[1] == 2 and chart_status_que[2] == 3:
        return 1
    elif chart_status_que[0] == 4 and chart_status_que[1] == 5 and chart_status_que[2] == 6:
        return 2
    else:
        return 0


def close_entry(sym, ty, qua, side_position, judgment_close_result):
    """
    close処理
    :param judgment_close_result: close判断結果
    :param sym:symbol
    :param ty: type 'MARKET'
    :param qua: quantity
    :param side_position: buy or sell
    """
    # 1:close long
    if judgment_close_result == 1 and side_position == 1:
        st.close_long_entry(sym, Client.SIDE_SELL, ty, qua)
        msg = "close long success!!"
        logger.info(msg)
    # 2:close short
    elif judgment_close_result == 2 and side_position == 2:
        st.close_short_entry(sym, Client.SIDE_BUY, ty, qua)
        msg = "close short success!!"
        logger.info(msg)


def entry(sym, ty, qua, judge_status):
    """
    entry処理
    :param judge_status: 1:long 2:short
    :param sym:symbol
    :param ty: type
    :param qua: quantity
    """
    # long entry
    if judge_status == 1:
        st.create_long_entry(sym, Client.SIDE_BUY, ty, qua)
    # short entry
    elif judge_status == 2:
        st.close_short_entry(sym, Client.SIDE_SELL, ty, qua)


# local 動作確認用
if __name__ == '__main__':
    main()
