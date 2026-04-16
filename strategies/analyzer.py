"""Module d'analyse technique."""
import logging
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """Analyseur technique pour le trading."""
    
    def __init__(
        self,
        rsi_period: int = 14,
        rsi_oversold: int = 30,
        rsi_overbought: int = 70,
        ma_short: int = 7,
        ma_long: int = 25
    ):
        """
        Initialise l'analyseur.
        
        Args:
            rsi_period: Période du RSI
            rsi_oversold: Seuil de survente
            rsi_overbought: Seuil de surachat
            ma_short: Période de la moyenne courte
            ma_long: Période de la moyenne longue
        """
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.ma_short = ma_short
        self.ma_long = ma_long
        logger.info(f"✅ Analyzer initialisé (RSI={rsi_period}, MA={ma_short}/{ma_long})")
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Calcule le RSI (Relative Strength Index).
        
        Args:
            prices: Série de prix
            period: Période de calcul
            
        Returns:
            Série contenant les valeurs RSI
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_moving_averages(
        self,
        prices: pd.Series,
        short_period: int = 7,
        long_period: int = 25
    ) -> Dict[str, pd.Series]:
        """
        Calcule les moyennes mobiles.
        
        Args:
            prices: Série de prix
            short_period: Période courte
            long_period: Période longue
            
        Returns:
            Dictionnaire avec 'short' et 'long'
        """
        return {
            'short': prices.rolling(window=short_period).mean(),
            'long': prices.rolling(window=long_period).mean()
        }
    
    def analyze(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Analyse complète des données.
        
        Args:
            df: DataFrame avec colonnes 'timestamp' et 'price'
            
        Returns:
            Dictionnaire avec les indicateurs et signaux
        """
        try:
            if df is None or len(df) < self.ma_long:
                logger.warning(f"Pas assez de données ({len(df) if df is not None else 0} < {self.ma_long})")
                return None
            
            # Calcul des indicateurs
            df['rsi'] = self.calculate_rsi(df['price'], self.rsi_period)
            mas = self.calculate_moving_averages(df['price'], self.ma_short, self.ma_long)
            df['ma_short'] = mas['short']
            df['ma_long'] = mas['long']
            
            # Dernières valeurs
            latest = df.iloc[-1]
            
            current_price = latest['price']
            current_rsi = latest['rsi']
            current_ma_short = latest['ma_short']
            current_ma_long = latest['ma_long']
            
            # Signaux RSI
            if current_rsi <= self.rsi_oversold:
                rsi_signal = 'OVERSOLD (BUY)'
            elif current_rsi >= self.rsi_overbought:
                rsi_signal = 'OVERBOUGHT (SELL)'
            else:
                rsi_signal = 'NEUTRAL'
            
            # Signaux MA
            if current_ma_short > current_ma_long:
                ma_signal = 'BULLISH (BUY)'
            elif current_ma_short < current_ma_long:
                ma_signal = 'BEARISH (SELL)'
            else:
                ma_signal = 'NEUTRAL'
            
            # Signal global
            if 'BUY' in rsi_signal and 'BUY' in ma_signal:
                global_signal = '🟢 STRONG BUY'
            elif 'SELL' in rsi_signal and 'SELL' in ma_signal:
                global_signal = '🔴 STRONG SELL'
            elif 'BUY' in rsi_signal or 'BUY' in ma_signal:
                global_signal = '🟡 WEAK BUY'
            elif 'SELL' in rsi_signal or 'SELL' in ma_signal:
                global_signal = '🟠 WEAK SELL'
            else:
                global_signal = '⚪ HOLD'
            
            return {
                'price': current_price,
                'rsi': current_rsi,
                'rsi_signal': rsi_signal,
                'ma_short': current_ma_short,
                'ma_long': current_ma_long,
                'ma_signal': ma_signal,
                'global_signal': global_signal,
                'timestamp': latest['timestamp']
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse: {e}", exc_info=True)
            return None
