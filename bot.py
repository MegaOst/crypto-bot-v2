"""
Bot de trading principal avec gestion positions et performance
"""
from data.market_data import MarketData
from strategies.simple_strategy import SimpleStrategy
from utils.logger import setup_logger
from config import config
from datetime import datetime
import json
import os

logger = setup_logger('bot')

class TradingBot:
    """Bot de trading automatisé"""
    
    def __init__(self):
        self.market_data = MarketData()
        self.strategy = SimpleStrategy()
        
        # État
        self.positions = []  # Positions ouvertes
        self.balance = config.INITIAL_BALANCE
        self.initial_balance = config.INITIAL_BALANCE
        
        # Historiques
        self.trades_log = []
        self.performance_log = []
        
        # Chargement données sauvegardées
        self._load_persisted_data()
        
        logger.info(f"🤖 Bot initialisé | Capital: ${self.balance:.2f} | Stratégie: {self.strategy.name}")
    
    def _load_persisted_data(self):
        """Charge les données sauvegardées"""
        os.makedirs(config.LOG_DIR, exist_ok=True)
        
        # Trades
        if os.path.exists(config.TRADES_FILE):
            try:
                with open(config.TRADES_FILE, 'r') as f:
                    self.trades_log = json.load(f)
                logger.info(f"📂 {len(self.trades_log)} trades chargés")
            except Exception as e:
                logger.warning(f"⚠️ Erreur chargement trades: {e}")
        
        # Performance
        if os.path.exists(config.PERFORMANCE_FILE):
            try:
                with open(config.PERFORMANCE_FILE, 'r') as f:
                    self.performance_log = json.load(f)
                logger.info(f"📊 {len(self.performance_log)} points performance chargés")
            except Exception as e:
                logger.warning(f"⚠️ Erreur chargement performance: {e}")
    
    def get_signal(self):
        """
        Récupère signal de trading actuel
        
        Returns:
            Dict avec signal et indicateurs
        """
        try:
            # Récupération données marché
            data = self.market_data.get_ohlcv(
                config.SYMBOL, 
                config.TIMEFRAME, 
                limit=100
            )
            
            if data.empty:
                logger.warning("⚠️ Pas de données marché")
                return None
            
            # Analyse stratégie
            signal = self.strategy.analyze(data)
            
            if signal is None:
                return None
            
            # Si signal BUY/SELL, traiter
            if signal['signal'] in ['BUY', 'SELL']:
                self._execute_signal(signal)
            
            return signal
            
        except Exception as e:
            logger.error(f"❌ Erreur get_signal: {e}", exc_info=True)
            return None
    
    def _execute_signal(self, signal):
        """
        Exécute un signal de trading (simulation)
        
        Args:
            signal: Dict avec type signal et prix
        """
        try:
            # Simulation simple: 10% du capital
            amount = self.balance * config.MAX_POSITION_SIZE
            
            if signal['signal'] == 'BUY' and amount > 0:
                # Achat
                quantity = amount / signal['price']
                self.positions.append({
                    'type': 'LONG',
                    'entry_price': signal['price'],
                    'quantity': quantity,
                    'timestamp': datetime.now().isoformat()
                })
                self.balance -= amount
                logger.info(f"💰 BUY {quantity:.6f} @ ${signal['price']:.2f} | Balance: ${self.balance:.2f}")
            
            elif signal['signal'] == 'SELL' and self.positions:
                # Vente de la première position
                position = self.positions.pop(0)
                sell_amount = position['quantity'] * signal['price']
                profit = sell_amount - (position['quantity'] * position['entry_price'])
                
                self.balance += sell_amount
                logger.info(f"💵 SELL {position['quantity']:.6f} @ ${signal['price']:.2f} | Profit: ${profit:.2f} | Balance: ${self.balance:.2f}")
            
            # Sauvegarde
            self._log_trade(signal)
            self._update_performance()
            
        except Exception as e:
            logger.error(f"❌ Erreur exécution: {e}", exc_info=True)
    
    def _log_trade(self, signal):
        """Enregistre un trade"""
        trade = {
            'timestamp': datetime.now().isoformat(),
            'signal': signal['signal'],
            'price': signal['price'],
            'rsi': signal['rsi'],
            'reason': signal['reason'],
            'balance': round(self.balance, 2)
        }
        
        self.trades_log.append(trade)
        
        try:
            with open(config.TRADES_FILE, 'w') as f:
                json.dump(self.trades_log, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde trade: {e}")
    
    def _update_performance(self):
        """Met à jour les métriques de performance"""
        profit_loss = self.balance - self.initial_balance
        profit_loss_pct = (profit_loss / self.initial_balance) * 100
        
        perf = {
            'timestamp': datetime.now().isoformat(),
            'balance': round(self.balance, 2),
            'profit_loss': round(profit_loss, 2),
            'profit_loss_pct': round(profit_loss_pct, 2),
            'positions': len(self.positions)
        }
        
        self.performance_log.append(perf)
        
        try:
            with open(config.PERFORMANCE_FILE, 'w') as f:
                json.dump(self.performance_log, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde performance: {e}")
    
    def get_stats(self):
        """Retourne statistiques actuelles"""
        profit_loss = self.balance - self.initial_balance
        profit_loss_pct = (profit_loss / self.initial_balance) * 100
        
        return {
            'initial_balance': round(self.initial_balance, 2),
            'current_balance': round(self.balance, 2),
            'profit_loss': round(profit_loss, 2),
            'profit_loss_pct': round(profit_loss_pct, 2),
            'total_trades': len(self.trades_log),
            'open_positions': len(self.positions),
            'symbol': config.SYMBOL,
            'timeframe': config.TIMEFRAME
        }
    
    def get_trades_history(self, limit=20):
        """Retourne historique trades"""
        return self.trades_log[-limit:][::-1]  # Derniers en premier
    
    def get_performance_history(self, limit=50):
        """Retourne historique performance"""
        return self.performance_log[-limit:]
