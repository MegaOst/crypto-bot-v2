"""
Configuration centralisée du bot de trading
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration principale"""
    
    # Trading
    SYMBOL = os.getenv('SYMBOL', 'BTC/USDT')
    TIMEFRAME = os.getenv('TIMEFRAME', '5m')
    INITIAL_BALANCE = float(os.getenv('INITIAL_BALANCE', 1000))
    
    # Indicateurs
    RSI_PERIOD = int(os.getenv('RSI_PERIOD', 14))
    RSI_OVERSOLD = int(os.getenv('RSI_OVERSOLD', 30))
    RSI_OVERBOUGHT = int(os.getenv('RSI_OVERBOUGHT', 70))
    MA_SHORT = int(os.getenv('MA_SHORT', 20))
    MA_LONG = int(os.getenv('MA_LONG', 50))
    
    # Risk Management
    MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', 0.1))
    STOP_LOSS_PCT = float(os.getenv('STOP_LOSS', 0.02))
    TAKE_PROFIT_PCT = float(os.getenv('TAKE_PROFIT', 0.05))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = 'logs'
    LOG_FILE = f'{LOG_DIR}/trading_bot.log'
    TRADES_FILE = f'{LOG_DIR}/trades.json'
    PERFORMANCE_FILE = f'{LOG_DIR}/performance.json'
    
    # Server
    PORT = int(os.getenv('PORT', 8000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # API
    CCXT_TIMEOUT = 10000  # 10 secondes
    RETRY_ATTEMPTS = 3
    
    @classmethod
    def validate(cls):
        """Valide la configuration"""
        assert cls.MA_SHORT < cls.MA_LONG, "MA_SHORT doit être < MA_LONG"
        assert 0 < cls.RSI_OVERSOLD < cls.RSI_OVERBOUGHT < 100, "RSI invalide"
        assert cls.INITIAL_BALANCE > 0, "Balance initiale invalide"
        return True

config = Config()
