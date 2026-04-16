import pandas as pd
import numpy as np

class RSIStrategy:
    def __init__(self, period=14, oversold=30, overbought=70):
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
    
    def calculate_rsi(self, prices):
        if len(prices) < self.period + 1:
            return None
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    
    def generate_signal(self, df):
        if df.empty or len(df) < self.period + 1:
            return 'HOLD', None, "Données insuffisantes"
        
        rsi = self.calculate_rsi(df['price'])
        
        if rsi is None or np.isnan(rsi):
            return 'HOLD', None, "RSI non calculable"
        
        if rsi < self.oversold:
            return 'BUY', rsi, f"RSI={rsi:.2f} < {self.oversold} (survente)"
        elif rsi > self.overbought:
            return 'SELL', rsi, f"RSI={rsi:.2f} > {self.overbought} (surachat)"
        else:
            return 'HOLD', rsi, f"RSI={rsi:.2f} (neutre)"
