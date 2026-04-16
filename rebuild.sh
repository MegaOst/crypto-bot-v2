#!/bin/bash

echo "=========================================="
echo "🔥 NETTOYAGE ET RECONSTRUCTION TOTALE"
echo "=========================================="

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. SAUVEGARDE
echo -e "\n${YELLOW}📦 Sauvegarde de .env...${NC}"
if [ -f .env ]; then
    cp .env .env.backup
    echo -e "${GREEN}✅ .env sauvegardé${NC}"
else
    echo -e "${RED}⚠️  Aucun .env trouvé${NC}"
fi

# 2. NETTOYAGE BRUTAL
echo -e "\n${YELLOW}🗑️  Suppression de tous les fichiers...${NC}"
rm -rf config/ data/ strategies/ utils/ tests/
rm -f main.py requirements.txt Procfile railway.json
rm -f *.pyc __pycache__
echo -e "${GREEN}✅ Nettoyage terminé${NC}"

# 3. CRÉATION STRUCTURE
echo -e "\n${YELLOW}📁 Création de la structure...${NC}"
mkdir -p config data strategies

# 4. CRÉATION DES FICHIERS

# ===== config/__init__.py =====
echo -e "${YELLOW}📄 Création de config/__init__.py...${NC}"
cat > config/__init__.py << 'EOF'
"""Configuration package"""
from .settings import settings

__all__ = ['settings']
EOF

# ===== config/settings.py =====
echo -e "${YELLOW}📄 Création de config/settings.py...${NC}"
cat > config/settings.py << 'EOF'
"""Configuration centralisée"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Configuration de l'application"""
    
    # API
    COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY', '')
    
    # Trading
    CRYPTO_SYMBOL = os.getenv('CRYPTO_SYMBOL', 'ethereum')
    VS_CURRENCY = os.getenv('VS_CURRENCY', 'usd')
    
    # Stratégie
    RSI_PERIOD = int(os.getenv('RSI_PERIOD', '14'))
    RSI_OVERSOLD = int(os.getenv('RSI_OVERSOLD', '30'))
    RSI_OVERBOUGHT = int(os.getenv('RSI_OVERBOUGHT', '70'))
    
    # Système
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '300'))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

settings = Settings()
EOF

# ===== data/__init__.py =====
echo -e "${YELLOW}📄 Création de data/__init__.py...${NC}"
cat > data/__init__.py << 'EOF'
"""Data collection package"""
from .collector import CryptoDataCollector

__all__ = ['CryptoDataCollector']
EOF

# ===== data/collector.py =====
echo -e "${YELLOW}📄 Création de data/collector.py...${NC}"
cat > data/collector.py << 'EOF'
"""Module de collecte des données depuis l'API CoinGecko"""
import requests
import logging
import pandas as pd
from typing import Optional

logger = logging.getLogger(__name__)

class CryptoDataCollector:
    """Collecteur de données crypto via CoinGecko API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = requests.Session()
        self.session.headers.update({
            'x-cg-pro-api-key': api_key,
            'Accept': 'application/json'
        })
        logger.info(f"✅ Collecteur initialisé")
    
    def get_market_data(self, symbol: str, vs_currency: str = 'usd', days: int = 30) -> Optional[pd.DataFrame]:
        """Récupère l'historique de prix"""
        endpoint = f"{self.base_url}/coins/{symbol}/market_chart"
        params = {'vs_currency': vs_currency, 'days': days}
        
        try:
            logger.info(f"📡 Requête: {symbol} sur {days} jours")
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            prices = data.get('prices', [])
            volumes = data.get('total_volumes', [])
            
            if not prices:
                logger.error("❌ Aucune donnée reçue")
                return None
            
            df_prices = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df_volumes = pd.DataFrame(volumes, columns=['timestamp', 'volume'])
            df = pd.merge(df_prices, df_volumes, on='timestamp', how='left')
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            logger.info(f"✅ {len(df)} points récupérés")
            return df
            
        except Exception as e:
            logger.error(f"❌ Erreur: {e}")
            return None
EOF

# ===== strategies/__init__.py =====
echo -e "${YELLOW}📄 Création de strategies/__init__.py...${NC}"
cat > strategies/__init__.py << 'EOF'
"""Trading strategies package"""
from .rsi_strategy import RSIStrategy

__all__ = ['RSIStrategy']
EOF

# ===== strategies/rsi_strategy.py =====
echo -e "${YELLOW}📄 Création de strategies/rsi_strategy.py...${NC}"
cat > strategies/rsi_strategy.py << 'EOF'
"""Stratégie de trading basée sur le RSI"""
import logging
import pandas as pd
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class RSIStrategy:
    """Stratégie RSI (Relative Strength Index)"""
    
    def __init__(self, period: int = 14, oversold: int = 30, overbought: int = 70):
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        logger.info(f"✅ RSI Strategy: period={period}, oversold={oversold}, overbought={overbought}")
    
    def calculate_rsi(self, prices: pd.Series) -> pd.Series:
        """Calcule le RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def analyze(self, df: pd.DataFrame) -> Optional[Dict]:
        """Analyse les données et retourne un signal"""
        if df is None or len(df) < self.period:
            logger.warning("⚠️ Données insuffisantes")
            return None
        
        df['rsi'] = self.calculate_rsi(df['price'])
        current_rsi = df['rsi'].iloc[-1]
        current_price = df['price'].iloc[-1]
        
        logger.info(f"📊 RSI actuel: {current_rsi:.2f}")
        
        if current_rsi < self.oversold:
            return {
                'action': 'BUY',
                'price': current_price,
                'rsi': current_rsi,
                'reason': f'RSI en survente ({current_rsi:.2f} < {self.oversold})'
            }
        elif current_rsi > self.overbought:
            return {
                'action': 'SELL',
                'price': current_price,
                'rsi': current_rsi,
                'reason': f'RSI en surachat ({current_rsi:.2f} > {self.overbought})'
            }
        
        return None
EOF

# ===== main.py =====
echo -e "${YELLOW}📄 Création de main.py...${NC}"
cat > main.py << 'EOF'
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
EOF

# ===== requirements.txt =====
echo -e "${YELLOW}📄 Création de requirements.txt...${NC}"
cat > requirements.txt << 'EOF'
requests==2.31.0
pandas==2.2.0
python-dotenv==1.0.0
numpy==1.26.3
EOF

# ===== Procfile =====
echo -e "${YELLOW}📄 Création de Procfile...${NC}"
cat > Procfile << 'EOF'
worker: python main.py
EOF

# ===== railway.json =====
echo -e "${YELLOW}📄 Création de railway.json...${NC}"
cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python main.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF

# 5. RESTAURATION .env
if [ -f .env.backup ]; then
    echo -e "\n${YELLOW}📦 Restauration de .env...${NC}"
    cp .env.backup .env
    echo -e "${GREEN}✅ .env restauré${NC}"
fi

# 6. VÉRIFICATION
echo -e "\n${YELLOW}🔍 Vérification de la structure...${NC}"
tree -L 2 -I '__pycache__|*.pyc' || ls -laR

# 7. GIT
echo -e "\n${YELLOW}📤 Préparation Git...${NC}"
git add .
echo -e "${GREEN}✅ Fichiers ajoutés à Git${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}✅ RECONSTRUCTION TERMINÉE !${NC}"
echo "=========================================="
echo ""
echo "Prochaines étapes :"
echo "  1. git commit -m 'fix: complete rebuild'"
echo "  2. git push origin main --force"
echo "  3. railway logs --tail 100"
echo ""

