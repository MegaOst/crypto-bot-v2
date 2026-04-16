"""Module d'analyse des signaux de trading"""

from typing import Dict, List, Optional
from datetime import datetime

class MarketAnalyzer:
    """Analyseur de signaux de marché"""
    
    def __init__(self, rsi_period: int = 14):
        self.rsi_period = rsi_period
        self.rsi_oversold = 30
        self.rsi_overbought = 70
    
    def calculate_rsi(self, prices: List[Dict]) -> Optional[float]:
        """Calcule le RSI"""
        if len(prices) < self.rsi_period + 1:
            return None
        
        # Extraire les prix
        close_prices = [p['price'] for p in prices]
        
        # Calculer les variations
        deltas = [close_prices[i] - close_prices[i-1] 
                  for i in range(1, len(close_prices))]
        
        # Séparer gains et pertes
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        # Moyennes
        avg_gain = sum(gains[-self.rsi_period:]) / self.rsi_period
        avg_loss = sum(losses[-self.rsi_period:]) / self.rsi_period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    def analyze_signal(self, prices: List[Dict], current_price: float) -> Dict:
        """Analyse et génère un signal"""
        rsi = self.calculate_rsi(prices)
        
        signal = {
            'timestamp': datetime.now().isoformat(),
            'price': current_price,
            'rsi': rsi,
            'signal': 'HOLD',
            'confidence': 0
        }
        
        if rsi is None:
            signal['signal'] = 'WAIT'
            signal['reason'] = 'Données insuffisantes'
            return signal
        
        # Logique de signal
        if rsi < self.rsi_oversold:
            signal['signal'] = 'BUY'
            signal['confidence'] = min(100, int((self.rsi_oversold - rsi) * 3))
            signal['reason'] = f'RSI survendu ({rsi})'
        elif rsi > self.rsi_overbought:
            signal['signal'] = 'SELL'
            signal['confidence'] = min(100, int((rsi - self.rsi_overbought) * 3))
            signal['reason'] = f'RSI suracheté ({rsi})'
        else:
            signal['signal'] = 'HOLD'
            signal['reason'] = f'RSI neutre ({rsi})'
        
        return signal
