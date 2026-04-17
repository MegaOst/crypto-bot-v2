"""
Indicateurs techniques avec gestion d'erreurs
"""
import pandas as pd
import numpy as np

def calculate_rsi(data, period=14):
    """
    Calcule le RSI (Relative Strength Index)
    
    Args:
        data: DataFrame avec colonne 'close'
        period: Période de calcul
    
    Returns:
        Valeur RSI entre 0 et 100, ou 50 si erreur
    """
    try:
        if len(data) < period + 1:
            return 50.0
        
        delta = data['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
        
        # Éviter division par zéro
        rs = gain / loss.replace(0, 0.0001)
        rsi = 100 - (100 / (1 + rs))
        
        last_rsi = rsi.iloc[-1]
        return float(last_rsi) if not pd.isna(last_rsi) else 50.0
    except Exception as e:
        print(f"Erreur RSI: {e}")
        return 50.0

def calculate_moving_averages(data, short_period=20, long_period=50):
    """
    Calcule les moyennes mobiles
    
    Returns:
        Tuple (MA courte, MA longue)
    """
    try:
        if len(data) < long_period:
            return (0.0, 0.0)
        
        ma_short = data['close'].rolling(window=short_period).mean().iloc[-1]
        ma_long = data['close'].rolling(window=long_period).mean().iloc[-1]
        
        return (
            float(ma_short) if not pd.isna(ma_short) else 0.0,
            float(ma_long) if not pd.isna(ma_long) else 0.0
        )
    except Exception as e:
        print(f"Erreur MA: {e}")
        return (0.0, 0.0)

def calculate_bollinger_bands(data, period=20, std_dev=2):
    """
    Calcule les bandes de Bollinger
    
    Returns:
        Tuple (upper, middle, lower)
    """
    try:
        if len(data) < period:
            return (0.0, 0.0, 0.0)
        
        middle = data['close'].rolling(window=period).mean()
        std = data['close'].rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return (
            float(upper.iloc[-1]) if not pd.isna(upper.iloc[-1]) else 0.0,
            float(middle.iloc[-1]) if not pd.isna(middle.iloc[-1]) else 0.0,
            float(lower.iloc[-1]) if not pd.isna(lower.iloc[-1]) else 0.0
        )
    except Exception as e:
        print(f"Erreur Bollinger: {e}")
        return (0.0, 0.0, 0.0)

def calculate_macd(data, fast=12, slow=26, signal=9):
    """
    Calcule le MACD
    
    Returns:
        Tuple (macd, signal, histogram)
    """
    try:
        if len(data) < slow:
            return (0.0, 0.0, 0.0)
        
        ema_fast = data['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = data['close'].ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        
        return (
            float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else 0.0,
            float(signal_line.iloc[-1]) if not pd.isna(signal_line.iloc[-1]) else 0.0,
            float(histogram.iloc[-1]) if not pd.isna(histogram.iloc[-1]) else 0.0
        )
    except Exception as e:
        print(f"Erreur MACD: {e}")
        return (0.0, 0.0, 0.0)
