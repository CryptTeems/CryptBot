import json
import time
from logging import getLogger, config
from Domain.Service import MovingAverageProperties as pr
from Domain.Service.MovingAverageService import MovingAverageService
from Domain.Service import MovingAverageService as ma
from binance.client import Client
with open('../../log/log_config.json', 'r') as f:
    log_conf = json.load(f)
config.dictConfig(log_conf)
logger = getLogger(__name__)


def main():
    logger.info("バッチの実行が開始されました")
    # 初期化
    chart_status_history = [0, 0, 0]

    while True:
        # 1sおきに実行
        time.sleep(1)

        # 初期化
        service = MovingAverageService(logger, pr.SYMBOL, Client.SIDE_BUY, pr.SETTLEMENT_TYPE_MARKET, pr.ENTRY_VOLUME)
        chart_data = service.get_chart_data()
        # 移動平均線の並びからStatusを取得
        status = service.get_chart_status(chart_data)
        # 移動平均線のステータス履歴を取得
        chart_status_history = service.get_status_history(chart_status_history, status)
        # entryを行うか判断
        if status != chart_status_history[2]:
            chart_status_history = ma.update_chart_status_que(chart_status_history, status)
            msg = "status:" + str(status) \
                  + " status_history:" + str(chart_status_history)
            logger.info(msg)
            # entryの判定
            judge_entry_status = service.judge_entry(chart_status_history)
            # closeの判定
            judge_close_status = service.judge_close(chart_status_history)

            # markPrice取得
            mark_price = ma.get_price(pr.SYMBOL)

            # entry
            if judge_entry_status == pr.ENTRY_LONG_STATUS or judge_entry_status == pr.ENTRY_SHORT_STATUS:
                service.entry(judge_entry_status, mark_price)
            # close
            if judge_close_status == pr.CLOSE_LONG_STATUS or judge_close_status == pr.CLOSE_SHORT_STATUS:
                service.close_entry(judge_close_status, mark_price)



# local 動作確認用
if __name__ == '__main__':
    main()
