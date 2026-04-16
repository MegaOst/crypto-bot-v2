import pandas as pd
from typing import Tuple

def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi.iloc[-1], 2)

def calculate_ma(prices: pd.Series, period: int) -> Tuple[float, pd.Series]:
    ma_series = prices.rolling(window=period).mean()
    return round(ma_series.iloc[-1], 2), ma_series
