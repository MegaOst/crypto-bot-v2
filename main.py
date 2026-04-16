import sys
import os

# FORCER L'AFFICHAGE IMMÉDIAT DES LOGS
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

print("=" * 60)
print("🚀 DÉMARRAGE DU BOT - VERSION DEBUG")
print("=" * 60)
print(f"📂 Répertoire de travail: {os.getcwd()}")
print(f"📁 Fichiers présents: {os.listdir('.')}")
print(f"🐍 Version Python: {sys.version}")
print("=" * 60)

# Vérifier les variables d'environnement
print("\n🔧 VARIABLES D'ENVIRONNEMENT:")
env_vars = [
    'CRYPTO_SYMBOL',
    'VS_CURRENCY', 
    'CHECK_INTERVAL',
    'CACHE_TTL',
    'RSI_PERIOD',
    'LOG_LEVEL'
]

for var in env_vars:
    value = os.getenv(var, '❌ NON DÉFINIE')
    print(f"   {var}: {value}")

print("=" * 60)

# Importer les modules
print("\n📦 IMPORT DES MODULES...")

try:
    print("   - Importing config...")
    from config.settings import TradingConfig
    print("   ✅ config.settings OK")
except Exception as e:
    print(f"   ❌ ERREUR config.settings: {e}")
    sys.exit(1)

try:
    print("   - Importing data collector...")
    from data.collector import CryptoDataCollector
    print("   ✅ data.collector OK")
except Exception as e:
    print(f"   ❌ ERREUR data.collector: {e}")
    sys.exit(1)

try:
    print("   - Importing analyzer...")
    from strategies.analyzer import TradingAnalyzer
    print("   ✅ strategies.analyzer OK")
except Exception as e:
    print(f"   ❌ ERREUR strategies.analyzer: {e}")
    sys.exit(1)

print("\n✅ TOUS LES MODULES IMPORTÉS")
print("=" * 60)

# Initialiser la config
print("\n⚙️ INITIALISATION DE LA CONFIGURATION...")
try:
    config = TradingConfig()
    print(f"✅ Configuration chargée:")
    print(f"   Symbol: {config.CRYPTO_SYMBOL}")
    print(f"   Interval: {config.CHECK_INTERVAL}s")
    print(f"   Cache: {config.CACHE_TTL}s")
except Exception as e:
    print(f"❌ ERREUR Configuration: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 60)

# Lancer la boucle principale
print("\n🔄 DÉMARRAGE DE LA BOUCLE PRINCIPALE...")

import time

iteration = 0
while True:
    iteration += 1
    print(f"\n{'='*60}")
    print(f"📊 ITÉRATION #{iteration} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    try:
        # Collecter les données
        print("🔄 Récupération des données...")
        collector = CryptoDataCollector(config)
        df = collector.get_historical_data(
    symbol=config.crypto_symbol,
    vs_currency=config.vs_currency,
    days=30
)
        
        if df is None or df.empty:
            print("⚠️ Aucune donnée récupérée")
        else:
            print(f"✅ {len(df)} points de données récupérés")
            print(f"   Prix actuel: {df['close'].iloc[-1]:.2f} {config.VS_CURRENCY.upper()}")
            
            # Analyser
            print("\n📈 Analyse technique...")
            analyzer = TradingAnalyzer(config)
            signal = analyzer.analyze(df)
            
            print(f"\n{'='*60}")
            print(f"🎯 SIGNAL: {signal['action']}")
            print(f"   Raison: {signal['reason']}")
            if signal.get('rsi'):
                print(f"   RSI: {signal['rsi']:.2f}")
            if signal.get('ma_short'):
                print(f"   MA court: {signal['ma_short']:.2f}")
            if signal.get('ma_long'):
                print(f"   MA long: {signal['ma_long']:.2f}")
            print(f"{'='*60}")
            
    except Exception as e:
        print(f"\n❌ ERREUR dans l'itération {iteration}:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Attendre avant la prochaine itération
    wait_time = config.CHECK_INTERVAL
    print(f"\n⏳ Prochaine analyse dans {wait_time} secondes...")
    time.sleep(wait_time)
