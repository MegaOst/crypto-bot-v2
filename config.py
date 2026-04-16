import os
from typing import Final

# API Configuration
COINGECKO_API_KEY: Final[str] = os.getenv('COINGECKO_API_KEY', '')
BASE_URL: Final[str] = 'https://api.coingecko.com/api/v3'

# Trading Parameters
SYMBOL: Final[str] = os.getenv('SYMBOL', 'bitcoin')
VS_CURRENCY: Final[str] = os.getenv('VS_CURRENCY', 'usd')
CHECK_INTERVAL: Final[int] = int(os.getenv('CHECK_INTERVAL', '300'))
CACHE_TTL: Final[int] = int(os.getenv('CACHE_TTL', '180'))

# Technical Indicators
RSI_PERIOD: Final[int] = int(os.getenv('RSI_PERIOD', '14'))
RSI_OVERSOLD: Final[int] = int(os.getenv('RSI_OVERSOLD', '30'))
RSI_OVERBOUGHT: Final[int] = int(os.getenv('RSI_OVERBOUGHT', '70'))
MA_SHORT: Final[int] = int(os.getenv('MA_SHORT', '7'))
MA_LONG: Final[int] = int(os.getenv('MA_LONG', '25'))

# Logging
LOG_LEVEL: Final[str] = os.getenv('LOG_LEVEL', 'INFO')

def validate_config() -> None:
    """Valide la cohérence de la configuration"""
    if CACHE_TTL >= CHECK_INTERVAL:
        raise ValueError(f"CACHE_TTL ({CACHE_TTL}) doit être < CHECK_INTERVAL ({CHECK_INTERVAL})")
    if RSI_OVERSOLD >= RSI_OVERBOUGHT:
        raise ValueError(f"RSI_OVERSOLD ({RSI_OVERSOLD}) doit être < RSI_OVERBOUGHT ({RSI_OVERBOUGHT})")
    if MA_SHORT >= MA_LONG:
        raise ValueError(f"MA_SHORT ({MA_SHORT}) doit être < MA_LONG ({MA_LONG})")
    print("✅ Configuration validée")
