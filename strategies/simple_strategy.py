import pandas as pd
from typing import Dict
from config import RSI_PERIOD, RSI_OVERSOLD, RSI_OVERBOUGHT, MA_SHORT, MA_LONG
from utils.indicators import calculate_rsi, calculate_ma
from utils.logger import setup_logger

logger = setup_logger(__name__)

class SimpleStrategy:
    def analyze(self, df: pd.DataFrame) -> Dict:
        prices = df['close']
        current_price = prices.iloc[-1]
        
        # RSI
        current_rsi = calculate_rsi(prices, RSI_PERIOD)
        
        # Moving Averages
        ma_short, ma_short_series = calculate_ma(prices, MA_SHORT)
        ma_long, ma_long_series = calculate_ma(prices, MA_LONG)
        
        # Croisements
        golden_cross = (ma_short_series.iloc[-2] <= ma_long_series.iloc[-2] and 
                       ma_short_series.iloc[-1] > ma_long_series.iloc[-1])
        death_cross = (ma_short_series.iloc[-2] >= ma_long_series.iloc[-2] and 
                      ma_short_series.iloc[-1] < ma_long_series.iloc[-1])
        
        # Logique de trading
        signal = 'HOLD'
        reason = []
        
        if current_rsi < RSI_OVERSOLD and golden_cross:
            signal = 'BUY'
            reason = [f'RSI survente ({current_rsi})', 'Golden Cross']
        elif current_rsi > RSI_OVERBOUGHT and death_cross:
            signal = 'SELL'
            reason = [f'RSI surachat ({current_rsi})', 'Death Cross']
        elif golden_cross:
            signal = 'BUY'
            reason = ['Golden Cross']
        elif death_cross:
            signal = 'SELL'
            reason = ['Death Cross']
        
        return {
            'signal': signal,
            'price': round(current_price, 2),
            'rsi': current_rsi,
            'ma_short': ma_short,
            'ma_long': ma_long,
            'reason': ' + '.join(reason) if reason else 'Pas de signal clair'
        }
