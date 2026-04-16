"""Module d'analyse technique."""
import logging
from typing import Optional, Dict, Any
import pandas as pd
import numpy as np
from config.settings import config

logger = logging.getLogger(__name__)

class TradingAnalyzer:
    """Analyseur de signaux de trading."""
    
    def __init__(
        self,
        rsi_period: int = None,
        rsi_oversold: int = None,
        rsi_overbought: int = None,
        ma_short: int = None,
        ma_long: int = None
    ):
        """Initialise l'analyseur."""
        self.rsi_period = rsi_period or config.RSI_PERIOD
        self.rsi_oversold = rsi_oversold or config.RSI_OVERSOLD
        self.rsi_overbought = rsi_overbought or config.RSI_OVERBOUGHT
        self.ma_short = ma_short or config.MA_SHORT_PERIOD
        self.ma_long = ma_long or config.MA_LONG_PERIOD
    
    def calculate_rsi(self, prices: pd.Series, period: int = None) -> pd.Series:
        """Calcule le RSI."""
        period = period or self.rsi_period
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_moving_averages(self, prices: pd.Series) -> Dict[str, pd.Series]:
        """Calcule les moyennes mobiles."""
        return {
            'ma_short': prices.rolling(window=self.ma_short).mean(),
            'ma_long': prices.rolling(window=self.ma_long).mean()
        }
    
    def analyze(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Analyse complète."""
        try:
            if df is None or len(df) < self.ma_long:
                logger.warning("Données insuffisantes pour l'analyse")
                return None
            
            # Calculs
            prices = df['price']
            rsi = self.calculate_rsi(prices)
            mas = self.calculate_moving_averages(prices)
            
            # Valeurs actuelles
            current_price = prices.iloc[-1]
            current_rsi = rsi.iloc[-1]
            current_ma_short = mas['ma_short'].iloc[-1]
            current_ma_long = mas['ma_long'].iloc[-1]
            
            # Signaux
            rsi_signal = self._get_rsi_signal(current_rsi)
            ma_signal = self._get_ma_signal(current_ma_short, current_ma_long)
            
            # Signal global
            if rsi_signal == 'BUY' and ma_signal == 'BUY':
                global_signal = 'STRONG_BUY'
            elif rsi_signal == 'BUY' or ma_signal == 'BUY':
                global_signal = 'BUY'
            elif rsi_signal == 'SELL' and ma_signal == 'SELL':
                global_signal = 'STRONG_SELL'
            elif rsi_signal == 'SELL' or ma_signal == 'SELL':
                global_signal = 'SELL'
            else:
                global_signal = 'HOLD'
            
            return {
                'price': current_price,
                'rsi': current_rsi,
                'ma_short': current_ma_short,
                'ma_long': current_ma_long,
                'rsi_signal': rsi_signal,
                'ma_signal': ma_signal,
                'global_signal': global_signal,
                'timestamp': df.index[-1]
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse: {e}")
            return None
    
    def _get_rsi_signal(self, rsi: float) -> str:
        """Détermine le signal RSI."""
        if rsi < self.rsi_oversold:
            return 'BUY'
        elif rsi > self.rsi_overbought:
            return 'SELL'
        return 'HOLD'
    
    def _get_ma_signal(self, ma_short: float, ma_long: float) -> str:
        """Détermine le signal MA."""
        if ma_short > ma_long * 1.02:  # 2% au-dessus
            return 'BUY'
        elif ma_short < ma_long * 0.98:  # 2% en-dessous
            return 'SELL'
        return 'HOLD'
