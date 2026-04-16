"""Configuration du bot de trading."""
import os
from dataclasses import dataclass

@dataclass
class TradingConfig:
    """Configuration centralisée."""
    
    # Crypto à analyser
    CRYPTO_SYMBOL: str = os.getenv('SYMBOL', 'ethereum')
    VS_CURRENCY: str = os.getenv('VS_CURRENCY', 'usd')
    
    # Intervalles (en secondes)
    CHECK_INTERVAL: int = int(os.getenv('CHECK_INTERVAL', '300'))
    CACHE_TTL: int = int(os.getenv('CACHE_TTL', '180'))
    
    # Indicateurs techniques
    RSI_PERIOD: int = int(os.getenv('RSI_PERIOD', '14'))
    RSI_OVERSOLD: int = int(os.getenv('RSI_OVERSOLD', '30'))
    RSI_OVERBOUGHT: int = int(os.getenv('RSI_OVERBOUGHT', '70'))
    MA_SHORT_PERIOD: int = int(os.getenv('MA_SHORT', '7'))
    MA_LONG_PERIOD: int = int(os.getenv('MA_LONG', '25'))
    
    # API
    COINGECKO_API_KEY: str = os.getenv('COINGECKO_API_KEY', '')
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')

# Instance globale
config = TradingConfig()
