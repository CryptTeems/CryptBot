# manual Execution
- ソース入れ替えしたときの再実行手順
- todo shell化
```
ssh -i "avgBot.pem" ec2-user@ec2-54-250-247-187.ap-northeast-1.compute.amazonaws.com
sudo rm -r RangeBot/
sudo rm -r cryptBot_app/
python3 -m venv cryptBot_app/env
source ~/cryptBot_app/env/bin/activate
pip install pip --upgrade
pip install python-binance
git clone https://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@github.com/CryptTeems/CryptBot.git
cd /home/ec2-user/RangeBot/Range
cp /dev/null log/MovingAverageLog
nohup python3 /home/ec2-user/RangeBot/Range/MovingAverage.py &
```
- トラブル時のコマンド
```
rm -r to\ be\ replaced 
python3 -m venv avgbot_app/env
source ~/avgbot_app/env/bin/activate
pip install pip --upgrade
git clone https://github.com/shoo5123/RangeBot.git
pip install python-binance
```
- 環境変数の設定コマンド
```
export API_KEY='APIキー'
export SECRET_KEY='SECRETキー'
確認コマンド
printenv
```
- ロググループ再セット
- 参考　https://business.ntt-east.co.jp/content/cloudsolution/column-try-28.html
```
sudo systemctl start awslogsd
sudo systemctl status awslogsd
```

- api reference
```
- Python Binance 
  - https://python-binance.readthedocs.io/en/latest/market_data.html
- howTo
  - https://modernimal.com/crypto-how-to-use-binance-api-5751
```
- デバック用コマンド
```
python3
from binance.client import Client
client = Client('7MlQofOjfeh6l4lxtGaqLqr04IAxwimmuqYobvozpBmqipd259dZxxHs1tBVu70a','eIIwHSRH6bpKAlAmAfhVDMjt1pmRopvSp54uC9fVF09PnYmCwS4ye2rwpsfsWOa3')
client.get_historical_klines('BNBBTC', Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
now_order = client.futures_position_information(symbol='ETHUSDT')
import json
depth = client.get_order_book(symbol='BNBBTC')
trades = client.get_recent_trades(symbol='BNBBTC')
info = client.get_all_tickers()
print(json.dumps(info, indent=4))
order = client.futures_create_order(symbol="BTCUSDT", side="SELL", type='MARKET', quantity=100)
order = client.futures_create_order(symbol="MATICUSDT", side="SELL", type='MARKET', quantity=6)
order = client.futures_position_information(symbol="MATICUSDT")
now_order = client.futures_position_information(symbol="MATICBUSD")
```

- 集計用
```
webサイトで取得
https://www.binance.com/ja/my/orders/futures/tradehistory
```


- testnet cmd
```
client = Client(api_key, api_secret, testnet=True)
```

- init インタープリター設定
```
実行環境をusr/binのPythonに変更
cloneしたリポジトリ配下で python3 -m venv rangebot/env
source /Users/iwasakitakashidai/IdeaProjects/RangeBot/rangebot/env/bin/activate
```

info = client.futures_income_history()
print(json.dumps(info, indent=4))


print(type(now_order[0]["positionAmt"]))
print(int(float(now_order[0]["positionAmt"])))



order = client.futures_position_information(symbol="ETHBUSD")
print(json.dumps(order, indent=2))

futures_create_order

order = client.futures_create_order(symbol="BTCUSDT", side="SELL", type='STOP', quantity=100)
print(order)
now_order = client.futures_position_information(symbol="MATICBUSD")
print(now_order)

# create order 
order = client.futures_create_order(symbol="SANDBUSD", side="BUY", type='MARKET', quantity=10)
# stop order
order = client.futures_create_order(symbol="SANDBUSD", side="SELL",type='STOP_MARKET', quantity=10, stopPrice=0.82)
now_order = client.futures_position_information(symbol="SANDBUSD")
print(order)
price = client.futures_mark_price(symbol="SANDBUSD")
print(int(price['markPrice']) * 1)
print() 