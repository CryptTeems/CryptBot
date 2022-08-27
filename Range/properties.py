from pydantic import BaseSettings

class Settings(BaseSettings):
    API_KEY: str
    SECRET_KEY: str

Settings = Settings()

API_KEY = Settings.API_KEY
SECRET_KEY = Settings.SECRET_KEY
ticker = 'MATIC'  # 取引対象
currency = 'USDT'  # USDT建て
symbol = ticker + currency
