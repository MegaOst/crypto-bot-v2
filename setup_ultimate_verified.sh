#!/bin/bash

# ============================================================================
# CRYPTO TRADING BOT - SETUP COMPLET VÉRIFIÉ
# Version: 2.0.0
# Vérifié par: Chef de Projet + Dev Senior
# ============================================================================

set -e  # Arrêt sur erreur

echo "🚀 INSTALLATION BOT DE TRADING - VERSION VÉRIFIÉE"
echo "=================================================="

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Vérification environnement
echo -e "${BLUE}🔍 Vérification environnement...${NC}"
command -v python3 >/dev/null 2>&1 || { echo -e "${RED}❌ Python3 requis${NC}"; exit 1; }
echo -e "${GREEN}✅ Python3 trouvé${NC}"

# Structure
echo -e "${BLUE}📁 Création structure...${NC}"
mkdir -p {templates,static/{css,js},data,strategies,utils,logs}

# ============================================================================
# 1. CONFIG.PY
# ============================================================================
echo -e "${BLUE}📝 config.py...${NC}"
cat > config.py << 'EOF'
"""
Configuration centralisée du bot de trading
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration principale"""
    
    # Trading
    SYMBOL = os.getenv('SYMBOL', 'BTC/USDT')
    TIMEFRAME = os.getenv('TIMEFRAME', '5m')
    INITIAL_BALANCE = float(os.getenv('INITIAL_BALANCE', 1000))
    
    # Indicateurs
    RSI_PERIOD = int(os.getenv('RSI_PERIOD', 14))
    RSI_OVERSOLD = int(os.getenv('RSI_OVERSOLD', 30))
    RSI_OVERBOUGHT = int(os.getenv('RSI_OVERBOUGHT', 70))
    MA_SHORT = int(os.getenv('MA_SHORT', 20))
    MA_LONG = int(os.getenv('MA_LONG', 50))
    
    # Risk Management
    MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', 0.1))
    STOP_LOSS_PCT = float(os.getenv('STOP_LOSS', 0.02))
    TAKE_PROFIT_PCT = float(os.getenv('TAKE_PROFIT', 0.05))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = 'logs'
    LOG_FILE = f'{LOG_DIR}/trading_bot.log'
    TRADES_FILE = f'{LOG_DIR}/trades.json'
    PERFORMANCE_FILE = f'{LOG_DIR}/performance.json'
    
    # Server
    PORT = int(os.getenv('PORT', 8000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # API
    CCXT_TIMEOUT = 10000  # 10 secondes
    RETRY_ATTEMPTS = 3
    
    @classmethod
    def validate(cls):
        """Valide la configuration"""
        assert cls.MA_SHORT < cls.MA_LONG, "MA_SHORT doit être < MA_LONG"
        assert 0 < cls.RSI_OVERSOLD < cls.RSI_OVERBOUGHT < 100, "RSI invalide"
        assert cls.INITIAL_BALANCE > 0, "Balance initiale invalide"
        return True

config = Config()
EOF

# ============================================================================
# 2. UTILS/LOGGER.PY
# ============================================================================
echo -e "${BLUE}📝 utils/logger.py...${NC}"
cat > utils/__init__.py << 'EOF'
from .logger import setup_logger, get_log_content
from .indicators import calculate_rsi, calculate_moving_averages, calculate_bollinger_bands, calculate_macd

__all__ = [
    'setup_logger', 'get_log_content',
    'calculate_rsi', 'calculate_moving_averages', 
    'calculate_bollinger_bands', 'calculate_macd'
]
EOF

cat > utils/logger.py << 'EOF'
"""
Système de logging avec rotation et niveaux
"""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(name='trading_bot', log_file=None, max_bytes=10*1024*1024):
    """
    Configure un logger avec rotation
    
    Args:
        name: Nom du logger
        log_file: Chemin fichier log
        max_bytes: Taille max avant rotation (10MB par défaut)
    """
    os.makedirs('logs', exist_ok=True)
    
    if log_file is None:
        log_file = f'logs/{name}_{datetime.now().strftime("%Y%m%d")}.log'
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Éviter doublons
    if logger.handlers:
        return logger
    
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler avec rotation
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=max_bytes,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_log_content(log_file='logs/trading_bot.log', lines=200):
    """
    Récupère les dernières lignes du log
    
    Args:
        log_file: Chemin du fichier
        lines: Nombre de lignes à récupérer
    
    Returns:
        Liste des lignes
    """
    try:
        if not os.path.exists(log_file):
            return [f"⚠️ Fichier {log_file} introuvable"]
        
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            return all_lines[-lines:] if len(all_lines) > lines else all_lines
    except Exception as e:
        return [f"❌ Erreur lecture logs: {str(e)}"]
EOF

# ============================================================================
# 3. UTILS/INDICATORS.PY
# ============================================================================
echo -e "${BLUE}📝 utils/indicators.py...${NC}"
cat > utils/indicators.py << 'EOF'
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
EOF

# ============================================================================
# 4. DATA/MARKET_DATA.PY
# ============================================================================
echo -e "${BLUE}📝 data/market_data.py...${NC}"
cat > data/__init__.py << 'EOF'
from .market_data import MarketData
__all__ = ['MarketData']
EOF

cat > data/market_data.py << 'EOF'
"""
Récupération données marché avec retry et timeout
"""
import ccxt
import pandas as pd
import time
from utils.logger import setup_logger
from config import config

logger = setup_logger('market_data')

class MarketData:
    """Gestion données marché via CCXT"""
    
    def __init__(self, exchange_name='binance'):
        try:
            exchange_class = getattr(ccxt, exchange_name)
            self.exchange = exchange_class({
                'timeout': config.CCXT_TIMEOUT,
                'enableRateLimit': True
            })
            logger.info(f"✅ Exchange {exchange_name} initialisé")
        except Exception as e:
            logger.error(f"❌ Erreur init exchange: {e}")
            raise
    
    def get_ohlcv(self, symbol, timeframe='5m', limit=100):
        """
        Récupère les données OHLCV avec retry
        
        Args:
            symbol: Paire de trading
            timeframe: Intervalle
            limit: Nombre de bougies
        
        Returns:
            DataFrame avec OHLCV
        """
        for attempt in range(config.RETRY_ATTEMPTS):
            try:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                
                if not ohlcv:
                    logger.warning(f"⚠️ Données vides pour {symbol}")
                    return pd.DataFrame()
                
                df = pd.DataFrame(
                    ohlcv, 
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                
                logger.info(f"📊 {len(df)} bougies récupérées pour {symbol}")
                return df
                
            except ccxt.NetworkError as e:
                logger.warning(f"⚠️ Erreur réseau (tentative {attempt+1}/{config.RETRY_ATTEMPTS}): {e}")
                time.sleep(2 ** attempt)  # Backoff exponentiel
            except ccxt.ExchangeError as e:
                logger.error(f"❌ Erreur exchange: {e}")
                return pd.DataFrame()
            except Exception as e:
                logger.error(f"❌ Erreur inattendue: {e}")
                return pd.DataFrame()
        
        logger.error(f"❌ Échec après {config.RETRY_ATTEMPTS} tentatives")
        return pd.DataFrame()
    
    def get_current_price(self, symbol):
        """Récupère le prix actuel"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return float(ticker['last'])
        except Exception as e:
            logger.error(f"❌ Erreur prix: {e}")
            return 0.0
EOF

# ============================================================================
# 5. STRATEGIES/SIMPLE_STRATEGY.PY
# ============================================================================
echo -e "${BLUE}📝 strategies/simple_strategy.py...${NC}"
cat > strategies/__init__.py << 'EOF'
from .simple_strategy import SimpleStrategy
__all__ = ['SimpleStrategy']
EOF

cat > strategies/simple_strategy.py << 'EOF'
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
EOF

# ============================================================================
# 6. BOT.PY - CORRIGÉ
# ============================================================================
echo -e "${BLUE}📝 bot.py (VERSION CORRIGÉE)...${NC}"
cat > bot.py << 'EOF'
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
EOF

# ============================================================================
# 7. MAIN.PY - APPLICATION FLASK
# ============================================================================
echo -e "${BLUE}📝 main.py...${NC}"
cat > main.py << 'EOF'
"""
Application Flask - Interface web du bot
"""
from flask import Flask, render_template, jsonify
from bot import TradingBot
from utils.logger import setup_logger, get_log_content
from config import config
import threading
import time

app = Flask(__name__)
logger = setup_logger('main')

# Instance bot
bot = TradingBot()
latest_signal = None
running = False

def bot_loop():
    """Boucle principale du bot"""
    global latest_signal, running
    logger.info("🚀 Bot loop démarré")
    
    while running:
        try:
            latest_signal = bot.get_signal()
            
            if latest_signal:
                logger.info(f"📊 Signal: {latest_signal['signal']} @ ${latest_signal['price']:.2f}")
            
            # Pause 5 minutes
            time.sleep(300)
            
        except Exception as e:
            logger.error(f"❌ Erreur bot_loop: {e}", exc_info=True)
            time.sleep(60)  # Pause courte en cas d'erreur
    
    logger.info("⏸ Bot loop arrêté")

# ===== ROUTES WEB =====

@app.route('/')
def home():
    """Page principale - Dashboard"""
    return render_template('index.html')

@app.route('/logs')
def logs_page():
    """Page visualisation logs"""
    return render_template('logs.html')

@app.route('/health')
def health():
    """Health check pour Railway"""
    return jsonify({"status": "ok", "running": running}), 200

# ===== ROUTES API =====

@app.route('/api/status')
def api_status():
    """État complet du bot"""
    stats = bot.get_stats()
    trades = bot.get_trades_history(limit=20)
    performance = bot.get_performance_history(limit=50)
    
    return jsonify({
        'running': running,
        'latest_signal': latest_signal,
        'stats': stats,
        'trades': trades,
        'performance': performance
    })

@app.route('/api/logs')
def api_logs():
    """Récupération logs"""
    logs = get_log_content(config.LOG_FILE, lines=200)
    return jsonify({'logs': logs})

@app.route('/api/start')
def start_bot():
    """Démarre le bot"""
    global running
    
    if not running:
        running = True
        thread = threading.Thread(target=bot_loop, daemon=True)
        thread.start()
        logger.info("🚀 Bot démarré via API")
    else:
        logger.warning("⚠️ Bot déjà en cours")
    
    return jsonify({'status': 'started', 'running': running})

@app.route('/api/stop')
def stop_bot():
    """Arrête le bot"""
    global running
    running = False
    logger.info("⏸ Bot arrêté via API")
    return jsonify({'status': 'stopped', 'running': running})

@app.route('/api/export')
def export_data():
    """Export données JSON"""
    stats = bot.get_stats()
    trades = bot.get_trades_history(limit=100)
    performance = bot.get_performance_history(limit=100)
    
    export = {
        'stats': stats,
        'trades': trades,
        'performance': performance,
        'exported_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'config': {
            'symbol': config.SYMBOL,
            'timeframe': config.TIMEFRAME,
            'rsi_oversold': config.RSI_OVERSOLD,
            'rsi_overbought': config.RSI_OVERBOUGHT
        }
    }
    
    return jsonify(export)

if __name__ == '__main__':
    logger.info(f"🌐 Démarrage serveur sur port {config.PORT}")
    config.validate()  # Validation config
    app.run(host='0.0.0.0', port=config.PORT, debug=config.DEBUG)
EOF

# ============================================================================
# 8. TEMPLATES/INDEX.HTML
# ============================================================================
echo -e "${BLUE}📝 templates/index.html...${NC}"
cat > templates/index.html << 'HTMLEOF'
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Crypto Trading Bot</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .nav {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin: 20px 0;
        }
        .nav a {
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            background: rgba(255,255,255,0.2);
            border-radius: 8px;
            transition: all 0.3s;
        }
        .nav a:hover {
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
        }
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        .stat-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-box h3 { font-size: 0.9em; opacity: 0.9; margin-bottom: 10px; }
        .stat-box p { font-size: 1.8em; font-weight: bold; }
        .profit { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important; }
        .loss { background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%) !important; }
        .signal {
            text-align: center;
            padding: 30px;
            font-size: 2em;
            font-weight: bold;
            border-radius: 10px;
            margin: 20px 0;
        }
        .signal.BUY { background: #38ef7d; color: white; }
        .signal.SELL { background: #f45c43; color: white; }
        .signal.HOLD { background: #ffd700; color: #333; }
        .controls {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin-top: 20px;
        }
        button {
            padding: 15px 30px;
            font-size: 1em;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: transform 0.2s;
        }
        button:hover { transform: scale(1.05); }
        .btn-start { background: #38ef7d; color: white; }
        .btn-stop { background: #f45c43; color: white; }
        .status {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
        }
        .status.running { background: #38ef7d; color: white; }
        .status.stopped { background: #f45c43; color: white; }
        #chart-container {
            width: 100%;
            height: 300px;
            position: relative;
        }
        .trades-list {
            max-height: 400px;
            overflow-y: auto;
        }
        .trade-item {
            padding: 10px;
            margin: 5px 0;
            background: #f5f5f5;
            border-radius: 5px;
            border-left: 4px solid;
        }
        .trade-item.BUY { border-left-color: #38ef7d; }
        .trade-item.SELL { border-left-color: #f45c43; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Crypto Trading Bot</h1>
            <p>Dashboard Temps Réel</p>
        </div>

        <div class="nav">
            <a href="/">📊 Dashboard</a>
            <a href="/logs">📜 Logs</a>
            <a href="#" onclick="exportData()">💾 Export</a>
        </div>

        <div class="card">
            <h2>État du Bot</h2>
            <div style="text-align: center; margin: 20px 0;">
                <span class="status" id="bot-status">⏳ Chargement...</span>
            </div>
            <div class="controls">
                <button class="btn-start" onclick="startBot()">▶ Démarrer</button>
                <button class="btn-stop" onclick="stopBot()">⏸ Arrêter</button>
            </div>
        </div>

        <div class="card">
            <h2>📊 Statistiques</h2>
            <div class="stats-grid">
                <div class="stat-box">
                    <h3>Capital Initial</h3>
                    <p id="initial-balance">$-</p>
                </div>
                <div class="stat-box">
                    <h3>Capital Actuel</h3>
                    <p id="current-balance">$-</p>
                </div>
                <div class="stat-box" id="pl-box">
                    <h3>Profit/Perte</h3>
                    <p id="profit-loss">$-</p>
                </div>
                <div class="stat-box">
                    <h3>Trades</h3>
                    <p id="total-trades">-</p>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>📈 Performance</h2>
            <div id="chart-container">
                <canvas id="performance-chart"></canvas>
            </div>
        </div>

        <div class="card">
            <h2>🎯 Dernier Signal</h2>
            <div class="signal" id="signal">HOLD</div>
            <div class="stats-grid">
                <div class="stat-box">
                    <h3>Prix</h3>
                    <p id="price">$-</p>
                </div>
                <div class="stat-box">
                    <h3>RSI</h3>
                    <p id="rsi">-</p>
                </div>
                <div class="stat-box">
                    <h3>MA Court</h3>
                    <p id="ma-short">$-</p>
                </div>
                <div class="stat-box">
                    <h3>MA Long</h3>
                    <p id="ma-long">$-</p>
                </div>
            </div>
            <p style="text-align: center; color: #666; margin-top: 10px;" id="reason">-</p>
        </div>

        <div class="card">
            <h2>📜 Historique</h2>
            <div class="trades-list" id="trades-list">
                <p style="text-align: center; color: #999;">Aucun trade</p>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        let chart = null;

        async function updateStatus() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                
                // Statut
                const status = document.getElementById('bot-status');
                status.textContent = data.running ? '🟢 En marche' : '🔴 Arrêté';
                status.className = data.running ? 'status running' : 'status stopped';
                
                // Stats
                document.getElementById('initial-balance').textContent = '$' + data.stats.initial_balance;
                document.getElementById('current-balance').textContent = '$' + data.stats.current_balance;
                document.getElementById('profit-loss').textContent = 
                    '$' + data.stats.profit_loss + ' (' + data.stats.profit_loss_pct + '%)';
                document.getElementById('total-trades').textContent = data.stats.total_trades;
                
                const plBox = document.getElementById('pl-box');
                plBox.className = data.stats.profit_loss >= 0 ? 'stat-box profit' : 'stat-box loss';
                
                // Signal
                if (data.latest_signal) {
                    const sig = data.latest_signal;
                    document.getElementById('signal').textContent = sig.signal;
                    document.getElementById('signal').className = 'signal ' + sig.signal;
                    document.getElementById('price').textContent = '$' + sig.price;
                    document.getElementById('rsi').textContent = sig.rsi;
                    document.getElementById('ma-short').textContent = '$' + sig.ma_short;
                    document.getElementById('ma-long').textContent = '$' + sig.ma_long;
                    document.getElementById('reason').textContent = sig.reason;
                }
                
                // Trades
                if (data.trades && data.trades.length > 0) {
                    document.getElementById('trades-list').innerHTML = data.trades.map(t => `
                        <div class="trade-item ${t.signal}">
                            <strong>${t.signal}</strong> @ $${t.price} 
                            <span style="float: right;">${new Date(t.timestamp).toLocaleString()}</span>
                            <br><small>${t.reason}</small>
                        </div>
                    `).join('');
                }
                
                // Chart
                if (data.performance && data.performance.length > 1) {
                    updateChart(data.performance);
                }
            } catch (error) {
                console.error('Erreur:', error);
            }
        }

        function updateChart(perf) {
            const ctx = document.getElementById('performance-chart');
            
            if (chart) chart.destroy();
            
            chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: perf.map(p => new Date(p.timestamp).toLocaleTimeString()),
                    datasets: [{
                        label: 'Balance ($)',
                        data: perf.map(p => p.balance),
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }

        async function startBot() {
            await fetch('/api/start');
            updateStatus();
        }

        async function stopBot() {
            await fetch('/api/stop');
            updateStatus();
        }

        async function exportData() {
            const res = await fetch('/api/export');
            const data = await res.json();
            const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `trading_${Date.now()}.json`;
            a.click();
        }

        setInterval(updateStatus, 5000);
        updateStatus();
    </script>
</body>
</html>
HTMLEOF

# ============================================================================
# 9. TEMPLATES/LOGS.HTML
# ============================================================================
echo -e "${BLUE}📝 templates/logs.html...${NC}"
cat > templates/logs.html << 'HTMLEOF'
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📜 Logs - Trading Bot</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            background: #2d2d2d;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { color: #4ec9b0; }
        .nav a {
            color: #569cd6;
            text-decoration: none;
            padding: 10px 20px;
            background: #3e3e3e;
            border-radius: 5px;
        }
        .logs-container {
            background: #252526;
            border-radius: 10px;
            padding: 20px;
            max-height: 80vh;
            overflow-y: auto;
        }
        .log-line {
            padding: 5px 0;
            border-bottom: 1px solid #3e3e3e;
        }
        .log-INFO { color: #4ec9b0; }
        .log-WARNING { color: #dcdcaa; }
        .log-ERROR { color: #f48771; }
        button {
            padding: 10px 20px;
            background: #007acc;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin: 10px 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📜 Logs</h1>
            <div class="nav">
                <a href="/">← Dashboard</a>
            </div>
        </div>
        <div>
            <button onclick="refreshLogs()">🔄 Rafraîchir</button>
            <label><input type="checkbox" id="auto" checked> Auto (5s)</label>
        </div>
        <div class="logs-container" id="logs">Chargement...</div>
    </div>

    <script>
        let interval = null;

        async function refreshLogs() {
            try {
                const res = await fetch('/api/logs');
                const data = await res.json();
                const container = document.getElementById('logs');
                
                container.innerHTML = data.logs.map(line => {
                    let cls = 'log-line';
                    if (line.includes('INFO')) cls += ' log-INFO';
                    else if (line.includes('WARNING')) cls += ' log-WARNING';
                    else if (line.includes('ERROR')) cls += ' log-ERROR';
                    return `<div class="${cls}">${line}</div>`;
                }).join('');
                
                container.scrollTop = container.scrollHeight;
            } catch (error) {
                document.getElementById('logs').innerHTML = 'Erreur chargement';
            }
        }

        document.getElementById('auto').addEventListener('change', function() {
            if (this.checked) {
                interval = setInterval(refreshLogs, 5000);
            } else {
                clearInterval(interval);
            }
        });

        refreshLogs();
        interval = setInterval(refreshLogs, 5000);
    </script>
</body>
</html>
HTMLEOF

# ============================================================================
# 10. FICHIERS DE CONFIGURATION
# ============================================================================
echo -e "${BLUE}📝 Fichiers configuration...${NC}"

cat > requirements.txt << 'EOF'
flask==3.0.0
gunicorn==21.2.0
ccxt==4.2.0
pandas==2.1.4
python-dotenv==1.0.0
numpy==1.26.3
EOF

cat > railway.toml << 'EOF'
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 1 --threads 2 main:app"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "on-failure"
restartPolicyMaxRetries = 10
EOF

cat > .env << 'EOF'
# Trading
SYMBOL=BTC/USDT
TIMEFRAME=5m
INITIAL_BALANCE=1000

# Indicateurs
RSI_PERIOD=14
RSI_OVERSOLD=30
RSI_OVERBOUGHT=70
MA_SHORT=20
MA_LONG=50

# Risk Management
MAX_POSITION_SIZE=0.1
STOP_LOSS=0.02
TAKE_PROFIT=0.05

# Server
PORT=8000
DEBUG=False
LOG_LEVEL=INFO
EOF

cat > .gitignore << 'EOF'
__pycache__/
*.py[cod]
.Python
venv/
.env
.venv
*.log
logs/*.log
logs/*.json
.DS_Store
*.pyc
EOF

cat > README.md << 'EOF'
# 🤖 Crypto Trading Bot - Version Vérifiée

Bot de trading automatisé avec interface web complète.

## ✅ Vérifié par
- Chef de Projet: Architecture et structure
- Dev Senior: Code, erreurs, performances

## 📁 Structure
