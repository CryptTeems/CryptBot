# manual Execution
- command
```
python3
from binance.client import Client
client = Client('7MlQofOjfeh6l4lxtGaqLqr04IAxwimmuqYobvozpBmqipd259dZxxHs1tBVu70a', 'eIIwHSRH6bpKAlAmAfhVDMjt1pmRopvSp54uC9fVF09PnYmCwS4ye2rwpsfsWOa3')
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


- testnet
```
client = Client(api_key, api_secret, testnet=True)
```



