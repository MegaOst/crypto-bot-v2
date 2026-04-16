"""Stratégie de trading basée sur le RSI"""
import logging
import pandas as pd
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class RSIStrategy:
    """Stratégie RSI (Relative Strength Index)"""
    
    def __init__(self, period: int = 14, oversold: int = 30, overbought: int = 70):
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        logger.info(f"✅ RSI Strategy: period={period}, oversold={oversold}, overbought={overbought}")
    
    def calculate_rsi(self, prices: pd.Series) -> pd.Series:
        """Calcule le RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def analyze(self, df: pd.DataFrame) -> Optional[Dict]:
        """Analyse les données et retourne un signal"""
        if df is None or len(df) < self.period:
            logger.warning("⚠️ Données insuffisantes")
            return None
        
        df['rsi'] = self.calculate_rsi(df['price'])
        current_rsi = df['rsi'].iloc[-1]
        current_price = df['price'].iloc[-1]
        
        logger.info(f"📊 RSI actuel: {current_rsi:.2f}")
        
        if current_rsi < self.oversold:
            return {
                'action': 'BUY',
                'price': current_price,
                'rsi': current_rsi,
                'reason': f'RSI en survente ({current_rsi:.2f} < {self.oversold})'
            }
        elif current_rsi > self.overbought:
            return {
                'action': 'SELL',
                'price': current_price,
                'rsi': current_rsi,
                'reason': f'RSI en surachat ({current_rsi:.2f} > {self.overbought})'
            }
        
        return None
