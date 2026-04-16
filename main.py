import time
from datetime import datetime
from config import CHECK_INTERVAL, SYMBOL, validate_config
from data.market_data import MarketDataFetcher
from strategies.simple_strategy import SimpleStrategy
from utils.logger import setup_logger

logger = setup_logger('main')

def main():
    print("\n🚀 CRYPTO BOT V2 - DÉMARRAGE")
    print(f"   Symbole: {SYMBOL}")
    print(f"   Intervalle: {CHECK_INTERVAL}s\n")
    
    validate_config()
    
    fetcher = MarketDataFetcher()
    strategy = SimpleStrategy()
    iteration = 0
    
    while True:
        try:
            iteration += 1
            logger.info(f"📊 Itération #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            df = fetcher.fetch_ohlc(days=30)
            analysis = strategy.analyze(df)
            
            emoji = {'BUY': '🟢', 'SELL': '🔴', 'HOLD': '🟡'}[analysis['signal']]
            logger.info(f"{emoji} Signal: {analysis['signal']}")
            logger.info(f"   Prix: ${analysis['price']}")
            logger.info(f"   RSI: {analysis['rsi']}")
            logger.info(f"   MA {analysis['ma_short']} / {analysis['ma_long']}")
            logger.info(f"   Raison: {analysis['reason']}")
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("\n👋 Arrêt demandé par l'utilisateur")
            break
        except Exception as e:
            logger.error(f"❌ Erreur: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
