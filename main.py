"""Bot de trading crypto - Point d'entrée principal."""
import sys
import os
import time
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("=" * 60)
print("🚀 DÉMARRAGE DU BOT - VERSION DEBUG")
print("=" * 60)
print(f"📂 Répertoire de travail: {os.getcwd()}")
print(f"📁 Fichiers présents: {os.listdir('.')}")
print(f"🐍 Version Python: {sys.version}")

# Import de la config
try:
    print("=" * 60)
    print("🔧 VARIABLES D'ENVIRONNEMENT:")
    print(f"   CRYPTO_SYMBOL: {os.getenv('SYMBOL', '❌ NON DÉFINIE')}")
    print(f"   VS_CURRENCY: {os.getenv('VS_CURRENCY', 'usd')}")
    print(f"   CHECK_INTERVAL: {os.getenv('CHECK_INTERVAL', '300')}")
    print(f"   CACHE_TTL: {os.getenv('CACHE_TTL', '180')}")
    print(f"   RSI_PERIOD: {os.getenv('RSI_PERIOD', '14')}")
    print(f"   LOG_LEVEL: {os.getenv('LOG_LEVEL', 'INFO')}")
    print("=" * 60)
    
    print("📦 IMPORT DES MODULES...")
    
    print("   - Importing config...")
    from config.settings import config
    print("   ✅ config.settings OK")
    
    print("   - Importing data collector...")
    from data.collector import CryptoDataCollector
    print("   ✅ data.collector OK")
    
    print("   - Importing analyzer...")
    from strategies.analyzer import TradingAnalyzer
    print("   ✅ strategies.analyzer OK")
    
    print("✅ TOUS LES MODULES IMPORTÉS")
    
except Exception as e:
    print(f"❌ ERREUR FATALE lors de l'import: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

def main():
    """Boucle principale du bot."""
    print("=" * 60)
    print("🔄 DÉMARRAGE DE LA BOUCLE PRINCIPALE...")
    print("=" * 60)
    
    # Initialisation
    print("⚙️ INITIALISATION DE LA CONFIGURATION...")
    print(f"✅ Configuration chargée:")
    print(f"   Symbol: {config.CRYPTO_SYMBOL}")
    print(f"   Interval: {config.CHECK_INTERVAL}s")
    print(f"   Cache: {config.CACHE_TTL}s")
    
    collector = CryptoDataCollector()
    analyzer = TradingAnalyzer()
    
    iteration = 0
    
    while True:
        try:
            iteration += 1
            print("=" * 60)
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
                time.sleep(config.CHECK_INTERVAL)
                continue
            
            print(f"✅ {len(df)} points de données récupérés")
            
            # Analyse
            print("🔍 Analyse en cours...")
            analysis = analyzer.analyze(df)
            
            if analysis:
                print("=" * 60)
                print("📈 RÉSULTATS DE L'ANALYSE:")
                print(f"   💰 Prix: ${analysis['price']:.2f}")
                print(f"   📊 RSI: {analysis['rsi']:.2f} → {analysis['rsi_signal']}")
                print(f"   📉 MA Court: ${analysis['ma_short']:.2f}")
                print(f"   📈 MA Long: ${analysis['ma_long']:.2f}")
                print(f"   🎯 Signal MA: {analysis['ma_signal']}")
                print(f"   🚦 SIGNAL GLOBAL: {analysis['global_signal']}")
                print("=" * 60)
            else:
                print("❌ Échec de l'analyse")
            
            # Attente
            print(f"⏳ Prochaine analyse dans {config.CHECK_INTERVAL} secondes...")
            time.sleep(config.CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n👋 Arrêt du bot demandé")
            break
        except Exception as e:
            print("=" * 60)
            print(f"❌ ERREUR dans l'itération {iteration}:")
            print(f"   {str(e)}")
            print("=" * 60)
            import traceback
            traceback.print_exc()
            time.sleep(config.CHECK_INTERVAL)

if __name__ == "__main__":
    main()
