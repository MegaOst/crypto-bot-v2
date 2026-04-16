import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY', '')
    CRYPTO_SYMBOL = os.getenv('CRYPTO_SYMBOL', 'ethereum')
    VS_CURRENCY = os.getenv('VS_CURRENCY', 'usd')
    RSI_PERIOD = int(os.getenv('RSI_PERIOD', '14'))
    RSI_OVERSOLD = int(os.getenv('RSI_OVERSOLD', '30'))
    RSI_OVERBOUGHT = int(os.getenv('RSI_OVERBOUGHT', '70'))
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '60'))

settings = Settings()
