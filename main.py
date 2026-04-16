"""
Bot de trading crypto - Point d'entrée principal
"""

import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# Import des modules
from data.collector import CryptoDataCollector
from strategies.rsi_strategy import RSIStrategy
from config.settings import settings

# Configuration logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Fonction principale du bot"""
    
    logger.info("="*60)
    logger.info("🚀 DÉMARRAGE DU BOT DE TRADING")
    logger.info("="*60)
    
    # Vérification configuration
    logger.info("⚙️ INITIALISATION DE LA CONFIGURATION...")
    logger.info("✅ Configuration chargée:")
    logger.info(f"   Symbol: {settings.CRYPTO_SYMBOL}")
    logger.info(f"   Currency: {settings.VS_CURRENCY}")
    logger.info(f"   Interval: {settings.CHECK_INTERVAL}s")
    logger.info(f"   RSI Period: {settings.RSI_PERIOD}")
    
    # Initialisation collecteur
    try:
        collector = CryptoDataCollector(api_key=settings.COINGECKO_API_KEY)
        logger.info("✅ Collecteur de données initialisé")
    except Exception as e:
        logger.error(f"❌ Erreur initialisation collecteur: {e}")
        sys.exit(1)
    
    # Initialisation stratégie
    try:
        strategy = RSIStrategy(
            period=settings.RSI_PERIOD,
            oversold=30,
            overbought=70
        )
        logger.info("✅ Stratégie RSI initialisée")
    except Exception as e:
        logger.error(f"❌ Erreur initialisation stratégie: {e}")
        sys.exit(1)
    
    logger.info("="*60)
    logger.info("✅ INITIALISATION TERMINÉE - DÉBUT DU MONITORING")
    logger.info("="*60)
    
    # Boucle principale
    iteration = 0
    
    while True:
        iteration += 1
        
        try:
            logger.info("")
            logger.info(f"📊 ITÉRATION #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("="*60)
            
            # Récupération des données
            logger.info("🔄 Récupération des données...")
            df = collector.get_market_data(
                symbol=settings.CRYPTO_SYMBOL,
                vs_currency=settings.VS_CURRENCY,
                days=30
            )
            
            if df is None or df.empty:
                logger.warning("⚠️ Aucune donnée disponible, nouvelle tentative dans 60s")
                time.sleep(60)
                continue
            
            logger.info(f"✅ {len(df)} points de données récupérés")
            
            # Analyse de la stratégie
            logger.info("📈 Analyse de la stratégie RSI...")
            signal = strategy.analyze(df)
            
            if signal:
                logger.info(f"🎯 SIGNAL DÉTECTÉ: {signal['action']}")
                logger.info(f"   Prix: {signal['price']:.2f} {settings.VS_CURRENCY.upper()}")
                logger.info(f"   RSI: {signal['rsi']:.2f}")
                logger.info(f"   Raison: {signal['reason']}")
            else:
                logger.info("⏸️ Aucun signal de trading")
            
            # Attente avant prochaine itération
            logger.info(f"⏳ Prochaine analyse dans {settings.CHECK_INTERVAL} secondes...")
            time.sleep(settings.CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("")
            logger.info("="*60)
            logger.info("⏹️ ARRÊT DU BOT (interruption utilisateur)")
            logger.info("="*60)
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"❌ Erreur dans l'itération {iteration}: {e}")
            logger.exception("Détails de l'erreur:")
            logger.info("⏳ Nouvelle tentative dans 60 secondes...")
            time.sleep(60)

if __name__ == "__main__":
    main()
