"""Point d'entrée du bot de trading crypto."""
import sys
import time
import logging
from datetime import datetime

# Import de la config
from config.settings import config

# Import des modules
from data.collector import CryptoDataCollector
from strategies.analyzer import TechnicalAnalyzer

# Configuration du logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_banner():
    """Affiche la bannière de démarrage."""
    print("\n" + "=" * 60)
    print("🚀 CRYPTO BOT - DÉMARRAGE")
    print("=" * 60)
    print(f"   Symbol: {config.CRYPTO_SYMBOL}")
    print(f"   Currency: {config.VS_CURRENCY}")
    print(f"   Interval: {config.CHECK_INTERVAL}s")
    print(f"   RSI Period: {config.RSI_PERIOD}")
    print(f"   MA Periods: {config.MA_SHORT_PERIOD}/{config.MA_LONG_PERIOD}")
    print("=" * 60 + "\n")

def main():
    """Fonction principale."""
    
    # Bannière
    print_banner()
    
    # Vérification de la clé API
    if not config.COINGECKO_API_KEY:
        logger.error("❌ COINGECKO_API_KEY non définie !")
        sys.exit(1)
    
    logger.info(f"🔑 API Key: {config.COINGECKO_API_KEY[:10]}...")
    
    # Initialisation des modules
    try:
        collector = CryptoDataCollector(api_key=config.COINGECKO_API_KEY)
        analyzer = TechnicalAnalyzer(
            rsi_period=config.RSI_PERIOD,
            rsi_oversold=config.RSI_OVERSOLD,
            rsi_overbought=config.RSI_OVERBOUGHT,
            ma_short=config.MA_SHORT_PERIOD,
            ma_long=config.MA_LONG_PERIOD
        )
        logger.info("✅ Modules initialisés")
    except Exception as e:
        logger.error(f"❌ Erreur d'initialisation: {e}")
        sys.exit(1)
    
    # Boucle principale
    iteration = 0
    
    while True:
        iteration += 1
        
        try:
            print("\n" + "=" * 60)
            print(f"📊 ITÉRATION #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 60)
            
            # Collecte des données
            print("🔄 Récupération des données...")
            df = collector.get_historical_data(
                symbol=config.CRYPTO_SYMBOL,
                vs_currency=config.VS_CURRENCY,
                days=30
            )
            
            if df is None or len(df) == 0:
                logger.warning("❌ Pas de données disponibles")
                print(f"⏳ Nouvelle tentative dans {config.CHECK_INTERVAL}s...")
                time.sleep(config.CHECK_INTERVAL)
                continue
            
            print(f"✅ {len(df)} points de données récupérés")
            
            # Analyse
            print("🔍 Analyse en cours...")
            analysis = analyzer.analyze(df)
            
            if analysis:
                print("\n" + "=" * 60)
                print("📈 RÉSULTATS DE L'ANALYSE:")
                print("=" * 60)
                print(f"   💰 Prix actuel:     ${analysis['price']:.2f}")
                print(f"   📊 RSI({config.RSI_PERIOD}):          {analysis['rsi']:.2f}")
                print(f"      → Signal:        {analysis['rsi_signal']}")
                print(f"   📉 MA({config.MA_SHORT_PERIOD}):           ${analysis['ma_short']:.2f}")
                print(f"   📈 MA({config.MA_LONG_PERIOD}):          ${analysis['ma_long']:.2f}")
                print(f"      → Signal:        {analysis['ma_signal']}")
                print("=" * 60)
                print(f"   🎯 SIGNAL GLOBAL:   {analysis['global_signal']}")
                print("=" * 60)
            else:
                print("❌ Échec de l'analyse")
            
            # Attente
            print(f"\n⏳ Prochaine analyse dans {config.CHECK_INTERVAL} secondes...\n")
            time.sleep(config.CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n👋 Arrêt du bot demandé par l'utilisateur")
            break
            
        except Exception as e:
            logger.error(f"❌ Erreur dans l'itération {iteration}: {e}", exc_info=True)
            print(f"⏳ Nouvelle tentative dans {config.CHECK_INTERVAL}s...")
            time.sleep(config.CHECK_INTERVAL)

if __name__ == "__main__":
    main()
