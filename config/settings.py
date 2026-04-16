"""Configuration centralisée"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Configuration de l'application"""
    
    # API
    COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY', '')
    
    # Trading
    CRYPTO_SYMBOL = os.getenv('CRYPTO_SYMBOL', 'ethereum')
    VS_CURRENCY = os.getenv('VS_CURRENCY', 'usd')
    
    # Stratégie
    RSI_PERIOD = int(os.getenv('RSI_PERIOD', '14'))
    RSI_OVERSOLD = int(os.getenv('RSI_OVERSOLD', '30'))
    RSI_OVERBOUGHT = int(os.getenv('RSI_OVERBOUGHT', '70'))
    
    # Système
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '300'))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

settings = Settings()
