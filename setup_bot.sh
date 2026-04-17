#!/bin/bash

set -e

echo "============================================================"
echo "🚀 RECONSTRUCTION COMPLÈTE DU BOT"
echo "============================================================"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}✅ $1${NC}"; }
log_warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Sauvegarde .env
if [ -f .env ]; then
    cp .env .env.backup
    log_info ".env sauvegardé"
fi

# Nettoyage TOTAL (y compris railway.json, railway.toml, etc.)
log_info "Nettoyage du répertoire..."
find . -maxdepth 1 -not -name '.git' -not -name '.env' -not -name '.env.backup' -not -name '.' -not -name '..' -not -name 'setup_bot.sh' -exec rm -rf {} + 2>/dev/null || true

# Crée requirements.txt
log_info "Création de requirements.txt..."
cat > requirements.txt << 'EOF'
flask==3.0.0
gunicorn==21.2.0
python-binance==1.0.19
pandas==2.1.4
numpy==1.26.2
ta==0.11.0
python-dotenv==1.0.0
EOF

# Crée config.py
log_info "Création de config.py..."
cat > config.py << 'EOF'
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
    BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')
    TESTNET = os.getenv('BINANCE_TESTNET', 'True').lower() == 'true'
    
    SYMBOL = os.getenv('SYMBOL', 'BTCUSDT')
    INTERVAL = os.getenv('INTERVAL', '5m')
    POSITION_SIZE = float(os.getenv('POSITION_SIZE', '50'))
    LEVERAGE = int(os.getenv('LEVERAGE', '10'))
    
    RSI_PERIOD = int(os.getenv('RSI_PERIOD', '14'))
    RSI_OVERBOUGHT = int(os.getenv('RSI_OVERBOUGHT', '70'))
    RSI_OVERSOLD = int(os.getenv('RSI_OVERSOLD', '30'))
    MACD_FAST = int(os.getenv('MACD_FAST', '12'))
    MACD_SLOW = int(os.getenv('MACD_SLOW', '26'))
    MACD_SIGNAL = int(os.getenv('MACD_SIGNAL', '9'))
    
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '300'))
    DRY_RUN = os.getenv('DRY_RUN', 'True').lower() == 'true'
    PORT = int(os.getenv('PORT', '8080'))
EOF

# Crée strategy.py
log_info "Création de strategy.py..."
cat > strategy.py << 'EOF'
import logging
import pandas as pd
from ta.momentum import RSIIndicator

logger = logging.getLogger(__name__)

class SimpleRSIStrategy:
    def __init__(self, client, symbol='BTCUSDT', interval='5m', rsi_period=14, 
                 rsi_oversold=30, rsi_overbought=70):
        self.client = client
        self.symbol = symbol
        self.interval = interval
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        
    def get_signal(self):
        try:
            klines = self.client.get_klines(
                symbol=self.symbol,
                interval=self.interval,
                limit=100
            )
            
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'trades',
                'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            
            df['close'] = pd.to_numeric(df['close'])
            
            rsi_indicator = RSIIndicator(close=df['close'], window=self.rsi_period)
            df['rsi'] = rsi_indicator.rsi()
            
            current_rsi = df['rsi'].iloc[-1]
            current_price = df['close'].iloc[-1]
            
            logger.info(f"📊 {self.symbol} - Price: ${current_price:.2f}, RSI: {current_rsi:.2f}")
            
            if current_rsi < self.rsi_oversold:
                logger.info(f"🟢 BUY signal - RSI {current_rsi:.2f} < {self.rsi_oversold}")
                return 'BUY'
            elif current_rsi > self.rsi_overbought:
                logger.info(f"🔴 SELL signal - RSI {current_rsi:.2f} > {self.rsi_overbought}")
                return 'SELL'
            else:
                logger.info(f"⚪ HOLD - RSI in neutral zone")
                return 'HOLD'
                
        except Exception as e:
            logger.error(f"❌ Error getting signal: {e}")
            return 'HOLD'
EOF

# Crée bot.py
log_info "Création de bot.py..."
cat > bot.py << 'EOF'
import logging
import time
import threading
from binance.client import Client
from config import Config
from strategy import SimpleRSIStrategy

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self):
        self.is_running = False
        self.thread = None
        
        try:
            self.client = Client(Config.BINANCE_API_KEY, Config.BINANCE_API_SECRET, testnet=Config.TESTNET)
            logger.info("✅ Binance client initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Binance: {e}")
            self.client = None
            
        self.strategy = SimpleRSIStrategy(
            client=self.client,
            symbol=Config.SYMBOL,
            interval=Config.INTERVAL,
            rsi_period=Config.RSI_PERIOD,
            rsi_oversold=Config.RSI_OVERSOLD,
            rsi_overbought=Config.RSI_OVERBOUGHT
        )
        
    def start(self):
        if self.is_running:
            logger.warning("⚠️ Bot already running")
            return
            
        self.is_running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("✅ Bot started")
        
    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("🛑 Bot stopped")
        
    def _run(self):
        logger.info("=" * 50)
        logger.info("🚀 TRADING BOT STARTED")
        logger.info(f"📊 Symbol: {Config.SYMBOL}")
        logger.info(f"⏰ Check interval: {Config.CHECK_INTERVAL}s")
        logger.info(f"🎮 Dry run: {Config.DRY_RUN}")
        logger.info("=" * 50)
        
        while self.is_running:
            try:
                signal = self.strategy.get_signal()
                
                if signal == 'BUY':
                    logger.info(f"💰 [DRY RUN] Would BUY {Config.SYMBOL}")
                elif signal == 'SELL':
                    logger.info(f"💸 [DRY RUN] Would SELL {Config.SYMBOL}")
                    
                time.sleep(Config.CHECK_INTERVAL)
                
            except Exception as e:
                logger.error(f"❌ Error in bot loop: {e}")
                time.sleep(60)
                
    def get_status(self):
        return {
            'running': self.is_running,
            'symbol': Config.SYMBOL,
            'interval': Config.INTERVAL,
            'dry_run': Config.DRY_RUN
        }
EOF

# Crée main.py
log_info "Création de main.py..."
cat > main.py << 'EOF'
import os
from flask import Flask, jsonify
from bot import TradingBot

app = Flask(__name__)
bot = TradingBot()

@app.route('/')
def index():
    return jsonify({'status': 'online', 'message': 'Crypto Trading Bot API'})

@app.route('/api/status')
def status():
    return jsonify(bot.get_status())

@app.route('/api/start', methods=['POST'])
def start_bot():
    bot.start()
    return jsonify({'message': 'Bot started'})

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    bot.stop()
    return jsonify({'message': 'Bot stopped'})

if __name__ == '__main__':
    if os.getenv('RAILWAY_ENVIRONMENT'):
        bot.start()
    
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
EOF

# Crée Procfile
log_info "Création de Procfile..."
echo "web: gunicorn main:app --bind 0.0.0.0:\$PORT --workers 1 --timeout 120" > Procfile

# Crée .gitignore
log_info "Création de .gitignore..."
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
.env
.env.backup
.venv/
venv/
*.log
.DS_Store
setup_bot.sh
railway.json
railway.toml
nixpacks.toml
EOF

# Crée .env template si n'existe pas
if [ ! -f .env ]; then
    log_warn "Création de .env template..."
    cat > .env << 'EOF'
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
BINANCE_TESTNET=True
SYMBOL=BTCUSDT
INTERVAL=5m
POSITION_SIZE=50
LEVERAGE=10
RSI_PERIOD=14
RSI_OVERBOUGHT=70
RSI_OVERSOLD=30
MACD_FAST=12
MACD_SLOW=26
MACD_SIGNAL=9
CHECK_INTERVAL=300
DRY_RUN=True
EOF
fi

# Ouvre .env avec Sublime Text
log_info "Ouverture de .env avec Sublime Text..."
if command -v subl &> /dev/null; then
    subl .env
    log_warn "⚠️  ÉDITE .env avec tes clés API"
elif command -v open &> /dev/null; then
    open -a "Sublime Text" .env 2>/dev/null || log_error "Ouvre .env manuellement"
else
    log_error "Ouvre .env manuellement avec Sublime Text"
fi

read -p "Appuie sur ENTER quand .env est édité et sauvegardé..."

# Git setup
if [ ! -d .git ]; then
    log_info "Initialisation de git..."
    git init
    git branch -M main
fi

git add .

echo ""
log_info "Fichiers créés:"
ls -1

echo ""
log_info "Status git:"
git status --short

echo ""
echo "============================================================"
echo "🚀 COMMIT ET PUSH"
echo "============================================================"

read -p "Faire le commit maintenant ? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git commit -m "feat: minimal working bot with RSI strategy"
    log_info "Commit fait !"
    
    read -p "Push sur origin main ? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push -u origin main --force
        log_info "Push fait !"
    fi
fi

echo ""
echo "============================================================"
echo "✅ TERMINÉ"
echo "============================================================"
echo ""
echo "📋 Dans Railway, ajoute ces variables:"
echo "   - Copie TOUT le contenu de .env"
echo "   - Colle dans Settings > Environment Variables"
echo ""
echo "🚀 Le bot démarrera automatiquement"
echo ""

