"""
Stratégie de trading RSI + Moving Averages
"""
from utils.indicators import calculate_rsi, calculate_moving_averages
from utils.logger import setup_logger
from config import config
from datetime import datetime

logger = setup_logger('strategy')

class SimpleStrategy:
    """Stratégie basée sur RSI et MA"""
    
    def __init__(self):
        self.name = "RSI + MA Strategy"
        logger.info(f"🎯 Stratégie initialisée: {self.name}")
    
    def analyze(self, data):
        """
        Analyse les données et génère un signal
        
        Args:
            data: DataFrame OHLCV
        
        Returns:
            Dict avec signal, prix, indicateurs, raison
        """
        try:
            # Validation données
            if data is None or data.empty:
                return self._no_signal("Pas de données")
            
            if len(data) < config.MA_LONG:
                return self._no_signal(f"Données insuffisantes ({len(data)} < {config.MA_LONG})")
            
            # Calculs
            current_price = float(data['close'].iloc[-1])
            rsi = calculate_rsi(data, config.RSI_PERIOD)
            ma_short, ma_long = calculate_moving_averages(
                data, 
                config.MA_SHORT, 
                config.MA_LONG
            )
            
            # Logique de signal
            signal = 'HOLD'
            reason = ''
            
            # Conditions BUY
            if rsi < config.RSI_OVERSOLD and ma_short > ma_long:
                signal = 'BUY'
                reason = f'RSI survendu ({rsi:.1f}) + Tendance haussière (MA{config.MA_SHORT} > MA{config.MA_LONG})'
                logger.info(f"🟢 SIGNAL BUY @ ${current_price:.2f} | {reason}")
            
            # Conditions SELL
            elif rsi > config.RSI_OVERBOUGHT and ma_short < ma_long:
                signal = 'SELL'
                reason = f'RSI suracheté ({rsi:.1f}) + Tendance baissière (MA{config.MA_SHORT} < MA{config.MA_LONG})'
                logger.info(f"🔴 SIGNAL SELL @ ${current_price:.2f} | {reason}")
            
            # HOLD
            else:
                reason = f'Conditions neutres (RSI: {rsi:.1f}, MA{config.MA_SHORT}: ${ma_short:.2f}, MA{config.MA_LONG}: ${ma_long:.2f})'
            
            return {
                'signal': signal,
                'price': round(current_price, 2),
                'rsi': round(rsi, 2),
                'ma_short': round(ma_short, 2),
                'ma_long': round(ma_long, 2),
                'reason': reason,
                'timestamp': data.index[-1].strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse: {e}", exc_info=True)
            return self._no_signal(f"Erreur: {str(e)}")
    
    def _no_signal(self, reason):
        """Retourne un signal HOLD par défaut"""
        return {
            'signal': 'HOLD',
            'price': 0.0,
            'rsi': 0.0,
            'ma_short': 0.0,
            'ma_long': 0.0,
            'reason': reason,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
