import os
from dataclasses import dataclass

@dataclass
class TradingConfig:
    """Configuration du bot de trading"""
    
    # Crypto à analyser
    CRYPTO_SYMBOL: str = os.getenv('SYMBOL', 'ethereum')  # ← 'SYMBOL' pas 'CRYPTO_SYMBOL'
    VS_CURRENCY: str = os.getenv('VS_CURRENCY', 'usd')
    
    # Intervalles (en secondes)
    CHECK_INTERVAL: int = int(os.getenv('CHECK_INTERVAL', '300'))
    CACHE_TTL: int = int(os.getenv('CACHE_TTL', '180'))
    
    # Indicateurs techniques
    RSI_PERIOD: int = int(os.getenv('RSI_PERIOD', '14'))
    RSI_OVERSOLD: int = int(os.getenv('RSI_OVERSOLD', '30'))
    RSI_OVERBOUGHT: int = int(os.getenv('RSI_OVERBOUGHT', '70'))
    MA_SHORT_PERIOD: int = int(os.getenv('MA_SHORT', '20'))      # ← CHANGÉ ICI
    MA_LONG_PERIOD: int = int(os.getenv('MA_LONG', '50'))       # ← CHANGÉ ICI
    
    # API
    COINGECKO_API_KEY: str = os.getenv('COINGECKO_API_KEY', '')
    
    # Logs
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    def __post_init__(self):
        """Validation de la configuration"""
        if self.CHECK_INTERVAL < self.CACHE_TTL:
            raise ValueError(
                f"CHECK_INTERVAL ({self.CHECK_INTERVAL}) doit être >= CACHE_TTL ({self.CACHE_TTL})"
            )
        
        if self.RSI_PERIOD < 2:
            raise ValueError(f"RSI_PERIOD ({self.RSI_PERIOD}) doit être >= 2")
        
        if not (0 < self.RSI_OVERSOLD < self.RSI_OVERBOUGHT < 100):
            raise ValueError(
                f"RSI invalides: oversold={self.RSI_OVERSOLD}, overbought={self.RSI_OVERBOUGHT}"
            )
