"""Bot de trading crypto - Point d'entrée principal"""
import logging
import sys
import time
from datetime import datetime

from data.collector import CryptoDataCollector
from strategies.rsi_strategy import RSIStrategy
from config.settings import settings

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def main():
    """Fonction principale du bot"""
    
    logger.info("="*60)
    logger.info("🚀 DÉMARRAGE DU BOT DE TRADING")
    logger.info("="*60)
    logger.info(f"   Symbol: {settings.CRYPTO_SYMBOL}")
    logger.info(f"   Currency: {settings.VS_CURRENCY}")
    logger.info(f"   Interval: {settings.CHECK_INTERVAL}s")
    logger.info(f"   RSI Period: {settings.RSI_PERIOD}")
    
    try:
        collector = CryptoDataCollector(api_key=settings.COINGECKO_API_KEY)
        strategy = RSIStrategy(
            period=settings.RSI_PERIOD,
            oversold=settings.RSI_OVERSOLD,
            overbought=settings.RSI_OVERBOUGHT
        )
        logger.info("✅ Initialisation terminée")
    except Exception as e:
        logger.error(f"❌ Erreur initialisation: {e}")
        sys.exit(1)
    
    logger.info("="*60)
    
    iteration = 0
    
    while True:
        iteration += 1
        
        try:
            logger.info(f"\n📊 ITÉRATION #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("="*60)
            
            df = collector.get_market_data(
                symbol=settings.CRYPTO_SYMBOL,
                vs_currency=settings.VS_CURRENCY,
                days=30
            )
            
            if df is None or df.empty:
                logger.warning("⚠️ Aucune donnée, retry dans 60s")
                time.sleep(60)
                continue
            
            signal = strategy.analyze(df)
            
            if signal:
                logger.info(f"🎯 SIGNAL: {signal['action']}")
                logger.info(f"   Prix: {signal['price']:.2f} {settings.VS_CURRENCY.upper()}")
                logger.info(f"   RSI: {signal['rsi']:.2f}")
                logger.info(f"   Raison: {signal['reason']}")
            else:
                logger.info("⏸️ Aucun signal")
            
            logger.info(f"⏳ Prochaine analyse dans {settings.CHECK_INTERVAL}s...")
            time.sleep(settings.CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("\n⏹️ ARRÊT DU BOT")
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"❌ Erreur itération {iteration}: {e}")
            logger.exception("Détails:")
            time.sleep(60)

if __name__ == "__main__":
    main()
