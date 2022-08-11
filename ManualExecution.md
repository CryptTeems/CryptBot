# manual Execution
- pythonをサーバで実行するときにinstallするもの
```
ssh -i "avgBot.pem" ec2-user@ec2-54-250-247-187.ap-northeast-1.compute.amazonaws.com

pip install pandas
pip install python-binance  
```


```
python3
from binance.client import Client
client = Client()
```
- api reference
    - Python Binance 
      - https://python-binance.readthedocs.io/en/latest/market_data.html
    - howTo
      - https://modernimal.com/crypto-how-to-use-binance-api-5751
      - 
- frequent
```
import json
depth = client.get_order_book(symbol='BNBBTC')
trades = client.get_recent_trades(symbol='BNBBTC')
info = client.get_all_tickers()
print(json.dumps(info, indent=4))
```

order = client.create_margin_order(
isolatedSymbol='XRPUSDT',
isIsolated=True,
side='BUY',
type="LIMIT",
timeInForce='GTC',
quantity=1,
price='0.00001')

order = client.order_market_sell(symbol='ADAUSDT',quantity=0.01)


from datetime import datetime, date, timezone, timedelta

print("Enrty long!! symbol:",order["symbol"],"volume:",order["origQty"],"USDT time:",datetime.fromtimestamp(order["updateTime"]/1000))
order = client.futures_create_order(symbol="MATICUSDT", side="BUY", type='MARKET', quantity=6)

print("Enrty short!! symbol:","volume:",order["origQty"],"USDT time:", datetime.fromtimestamp(order["updateTime"]/1000))
trade_data = client.futures_coin_historical_trades(symbol='MATICUSDT')
trade_data = client.futures_get_open_orders(symbol='MATICUSDT')
print(trade_data)





```
オーダーAPI
order = binance.futures_create_order(symbol=pr.symbol, side=Client.SIDE_BUY, type='MARKET', quantity=volume)

```
order = client.futures_create_order(symbol="MATICUSDT", side="BUY", type='MARKET', quantity=6)
order = client.futures_create_order(symbol="MATICUSDT", side="BUY", type='MARKET', quantity=100)
print(order)

print(json.dumps(order, indent=4))


- testnet
```
client = Client(api_key, api_secret, testnet=True)
```



