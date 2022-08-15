import datetime
import time

import pandas as pd
import properties as pr
import json
from logging import getLogger, config
import mplfinance as mpf                # pip install mplfinance
# layer import
from binance.client import Client
from binance.exceptions import BinanceAPIException
import matplotlib as mpl
import matplotlib.pyplot as plt

API_KEY = '7MlQofOjfeh6l4lxtGaqLqr04IAxwimmuqYobvozpBmqipd259dZxxHs1tBVu70a'
SECRET_KEY = 'eIIwHSRH6bpKAlAmAfhVDMjt1pmRopvSp54uC9fVF09PnYmCwS4ye2rwpsfsWOa3'

# client
binance = Client(API_KEY, SECRET_KEY)


df_chart_chart = pd.DataFrame()
df_income_history = pd.DataFrame()

data_chart = binance.get_historical_klines("MATICUSDT", Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
data_income_history = binance.futures_income_history()

df_chart = pd.DataFrame(data_chart, columns=["datetime", "Open", "High", "Low", "Close", "del", "del", "del", "del", "del", "del", "del"])
df_chart = df_chart.drop(columns="del", axis=1)

df_income_history = pd.DataFrame(data_income_history)
df_income_history = df_income_history.drop(columns="info", axis=1)
df_income_history = df_income_history.drop(columns="tranId", axis=1)
df_income_history = df_income_history.drop(columns="tradeId", axis=1)
for num in range(len(df_income_history)):
    df_income_history["time"][num] = pd.to_datetime(datetime.datetime.fromtimestamp(df_income_history["time"][num]/1000))
#df_chart.set_index('time', inplace=True)
df_income_history["income"] = df_income_history["income"].astype(float)


for num in range(len(df_chart)):
    df_chart["datetime"][num] = pd.to_datetime(datetime.datetime.fromtimestamp(df_chart["datetime"][num]/1000))
df_chart.set_index('datetime', inplace=True)
df_chart["Open"] = df_chart["Open"].astype(float)
df_chart["High"] = df_chart["High"].astype(float)
df_chart["Low"] = df_chart["Low"].astype(float)
df_chart["Close"] = df_chart["Close"].astype(float)

#fig = mpf.figure(figsize=(11, 8))
#ax1 = fig.subplots()
#ax1.barh(list(df_income_history), df_income_history["income"], color="orange")
#ax2 = ax1.twiny()
#mpf.plot(df_chart, ax=ax2, type="candle", mav=(7, 25, 99))
#fig.suptitle('test')
#mpf.show()  #or plt.show()

# ローソク
mpf.plot(df_chart, type='candle', mav=(7, 25, 99))

#df_income_history.plot(x="time", y="income")
#df_income_history.plot(figsize=(9, 6))
plt.show()

#print(df_chart)