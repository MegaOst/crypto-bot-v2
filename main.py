import logging
from flask import Flask, jsonify, render_template, request
from bot import TradingBot
from config import Config
from datetime import datetime
import threading

# Configuration logging avancée
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Force l'affichage dans Railway logs
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
bot = TradingBot()

# ✅ DÉMARRE LE BOT AU LANCEMENT DE L'APP
def init_bot():
    """Initialise et démarre le bot en arrière-plan"""
    try:
        logger.info("=" * 50)
        logger.info("🚀 CRYPTO TRADING BOT - RAILWAY MODE")
        logger.info("=" * 50)
        logger.info(f"📊 Symbol: {Config.SYMBOL}")
        logger.info(f"⚡ Leverage: {Config.LEVERAGE}x")
        logger.info(f"💰 Position Size: {Config.POSITION_SIZE_USDT} USDT")
        logger.info(f"⏰ Check Interval: {Config.CHECK_INTERVAL}s")
        logger.info("=" * 50)
        
        # Démarre le bot dans un thread séparé
        bot_thread = threading.Thread(target=bot.start, daemon=True)
        bot_thread.start()
        logger.info("✅ Bot thread started successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")

# Lance le bot au démarrage (en mode production uniquement)
if __name__ != '__main__':
    init_bot()

# Routes
@app.route('/')
def dashboard():
    logger.info("📊 Dashboard accessed")
    return render_template('dashboard.html')

@app.route('/health')
def health():
    logger.info("💚 Health check requested")
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "bot_running": bot.is_running if hasattr(bot, 'is_running') else False
    })

@app.route('/api/status')
def get_status():
    logger.info("📡 Status requested")
    try:
        status = {
            "is_running": bot.is_running if hasattr(bot, 'is_running') else False,
            "symbol": Config.SYMBOL,
            "leverage": Config.LEVERAGE,
            "position_size": Config.POSITION_SIZE_USDT,
            "check_interval": Config.CHECK_INTERVAL,
            "current_time": datetime.now().isoformat()
        }
        
        # Ajoute la position actuelle si disponible
        if hasattr(bot, 'current_position'):
            status['current_position'] = bot.current_position
            
        return jsonify(status)
    except Exception as e:
        logger.error(f"❌ Error getting status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/start', methods=['POST'])
def start_bot():
    logger.info("🚀 Manual bot start requested")
    try:
        if not bot.is_running:
            bot_thread = threading.Thread(target=bot.start, daemon=True)
            bot_thread.start()
            return jsonify({"message": "Bot started successfully"})
        else:
            return jsonify({"message": "Bot is already running"})
    except Exception as e:
        logger.error(f"❌ Error starting bot: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def stop_bot():
    logger.info("🛑 Bot stop requested")
    try:
        bot.stop()
        return jsonify({"message": "Bot stopped successfully"})
    except Exception as e:
        logger.error(f"❌ Error stopping bot: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Mode développement local
    logger.info("🔧 Starting in development mode...")
    init_bot()
    app.run(host='0.0.0.0', port=8080, debug=False)
