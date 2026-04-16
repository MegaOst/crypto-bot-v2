"""Configuration du bot de trading."""
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class TradingConfig:
    """Configuration centralisée."""
    
    # Crypto à analyser
    CRYPTO_SYMBOL: str = 'ethereum'
    VS_CURRENCY: str = 'usd'
    
    # Intervalles (en secondes)
    CHECK_INTERVAL: int = 300
    CACHE_TTL: int = 180
    
    # Indicateurs techniques
    RSI_PERIOD: int = 14
    RSI_OVERSOLD: int = 30
    RSI_OVERBOUGHT: int = 70
    MA_SHORT_PERIOD: int = 7
    MA_LONG_PERIOD: int = 25
    
    # API
    COINGECKO_API_KEY: str = ''
    
    # Logging
    LOG_LEVEL: str = 'INFO'
    
    def __post_init__(self):
        """Charge les variables d'environnement."""
        self.CRYPTO_SYMBOL = os.getenv('SYMBOL', self.CRYPTO_SYMBOL)
        self.VS_CURRENCY = os.getenv('VS_CURRENCY', self.VS_CURRENCY)
        self.CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', str(self.CHECK_INTERVAL)))
        self.CACHE_TTL = int(os.getenv('CACHE_TTL', str(self.CACHE_TTL)))
        self.RSI_PERIOD = int(os.getenv('RSI_PERIOD', str(self.RSI_PERIOD)))
        self.RSI_OVERSOLD = int(os.getenv('RSI_OVERSOLD', str(self.RSI_OVERSOLD)))
        self.RSI_OVERBOUGHT = int(os.getenv('RSI_OVERBOUGHT', str(self.RSI_OVERBOUGHT)))
        self.MA_SHORT_PERIOD = int(os.getenv('MA_SHORT', str(self.MA_SHORT_PERIOD)))
        self.MA_LONG_PERIOD = int(os.getenv('MA_LONG', str(self.MA_LONG_PERIOD)))
        self.COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY', self.COINGECKO_API_KEY)
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', self.LOG_LEVEL)

# Instance globale
config = TradingConfig()
