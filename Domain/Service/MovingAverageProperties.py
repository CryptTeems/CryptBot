# user_info
API_KEY = '7MlQofOjfeh6l4lxtGaqLqr04IAxwimmuqYobvozpBmqipd259dZxxHs1tBVu70a'
SECRET_KEY = 'eIIwHSRH6bpKAlAmAfhVDMjt1pmRopvSp54uC9fVF09PnYmCwS4ye2rwpsfsWOa3'

# trade_info
TICKER = 'MATIC'  # 取引対象
CURRENCY = 'BUSD'  # USDT建て
SYMBOL = TICKER + CURRENCY
# judge_entry_status
ENTRY_STAY_STATUS = "0"
ENTRY_LONG_STATUS = "1"
ENTRY_SHORT_STATUS = "2"
# judge_close_status
CLOSE_STAY_STATUS = "0"
CLOSE_LONG_STATUS = "1"
CLOSE_SHORT_STATUS = "2"
SETTLEMENT_TYPE_MARKET = "MARKET"
ONE_DAY = "1 day ago UTC"
STOP_MARKET = 'STOP_MARKET'

# parameter
# 移動平均線のローソク足本数
DURATION_SHORT_TERM = 7
DURATION_MEDIUM_TERM = 25
DURATION_LONG_TERM = 99
# 損切りライン
LIMIT_PERCENT = 10
# 収益確定ライン
limit_percent = 50
# 取引ボリューム
ENTRY_VOLUME = 100
# status checker
ENTRY_LONG_STATUS_QUE = [4, 5, 6]
ENTRY_SHORT_STATUS_QUE = [1, 2, 3]
CLOSE_LONG_STATUS_QUE = [1, 2, 3]
CLOSE_SHORT_STATUS_QUE = [4, 5, 6]
