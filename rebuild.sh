#!/bin/bash

echo "=========================================="
echo "🔥 NETTOYAGE ET RECONSTRUCTION TOTALE"
echo "=========================================="

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. SAUVEGARDE
echo -e "\n${YELLOW}📦 Sauvegarde de .env...${NC}"
if [ -f .env ]; then
    cp .env .env.backup
    echo -e "${GREEN}✅ .env sauvegardé${NC}"
fi

# 2. NETTOYAGE
echo -e "\n${YELLOW}🗑️  Nettoyage...${NC}"
rm -rf config/ data/ strategies/ __pycache__/
rm -f main.py requirements.txt Procfile railway.json
echo -e "${GREEN}✅ Nettoyage terminé${NC}"

# 3. STRUCTURE
echo -e "\n${YELLOW}📁 Création structure...${NC}"
mkdir -p config data strategies

# 4. FICHIERS CONFIG
cat > config/__init__.py << 'EOF'
from .settings import settings
__all__ = ['settings']
EOF

cat > config/settings.py << 'EOF'
import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY', '')
    CRYPTO_SYMBOL = os.getenv('CRYPTO_SYMBOL', 'ethereum')
    VS_CURRENCY = os.getenv('VS_CURRENCY', 'usd')
    RSI_PERIOD = int(os.getenv('RSI_PERIOD', '14'))
    RSI_OVERSOLD = int(os.getenv('RSI_OVERSOLD', '30'))
    RSI_OVERBOUGHT = int(os.getenv('RSI_OVERBOUGHT', '70'))
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '60'))

settings = Settings()
EOF

# 5. FICHIERS DATA
cat > data/__init__.py << 'EOF'
from .collector import DataCollector
__all__ = ['DataCollector']
EOF

cat > data/collector.py << 'EOF'
import requests
import pandas as pd
from datetime import datetime

class DataCollector:
    def __init__(self, api_key, symbol, vs_currency='usd'):
        self.api_key = api_key
        self.symbol = symbol
        self.vs_currency = vs_currency
        self.base_url = 'https://api.coingecko.com/api/v3'
    
    def get_current_price(self):
        url = f'{self.base_url}/simple/price'
        params = {'ids': self.symbol, 'vs_currencies': self.vs_currency}
        headers = {'x-cg-demo-api-key': self.api_key} if self.api_key else {}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get(self.symbol, {}).get(self.vs_currency)
        except Exception as e:
            print(f"❌ Erreur récupération prix: {e}")
            return None
    
    def get_historical_data(self, days=30):
        url = f'{self.base_url}/coins/{self.symbol}/market_chart'
        params = {'vs_currency': self.vs_currency, 'days': days}
        headers = {'x-cg-demo-api-key': self.api_key} if self.api_key else {}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            prices = data.get('prices', [])
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"❌ Erreur données historiques: {e}")
            return pd.DataFrame()
EOF

# 6. FICHIERS STRATEGIES
cat > strategies/__init__.py << 'EOF'
from .rsi_strategy import RSIStrategy
__all__ = ['RSIStrategy']
EOF

cat > strategies/rsi_strategy.py << 'EOF'
import pandas as pd
import numpy as np

class RSIStrategy:
    def __init__(self, period=14, oversold=30, overbought=70):
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
    
    def calculate_rsi(self, prices):
        if len(prices) < self.period + 1:
            return None
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    
    def generate_signal(self, df):
        if df.empty or len(df) < self.period + 1:
            return 'HOLD', None, "Données insuffisantes"
        
        rsi = self.calculate_rsi(df['price'])
        
        if rsi is None or np.isnan(rsi):
            return 'HOLD', None, "RSI non calculable"
        
        if rsi < self.oversold:
            return 'BUY', rsi, f"RSI={rsi:.2f} < {self.oversold} (survente)"
        elif rsi > self.overbought:
            return 'SELL', rsi, f"RSI={rsi:.2f} > {self.overbought} (surachat)"
        else:
            return 'HOLD', rsi, f"RSI={rsi:.2f} (neutre)"
EOF

# 7. MAIN.PY
cat > main.py << 'EOF'
import time
from datetime import datetime
from config.settings import settings
from data.collector import DataCollector
from strategies.rsi_strategy import RSIStrategy

def main():
    print("=" * 60)
    print("🚀 TRADING BOT DÉMARRÉ")
    print("=" * 60)
    print(f"📊 Crypto: {settings.CRYPTO_SYMBOL.upper()}")
    print(f"💱 Devise: {settings.VS_CURRENCY.upper()}")
    print(f"📈 RSI: {settings.RSI_PERIOD} / {settings.RSI_OVERSOLD} / {settings.RSI_OVERBOUGHT}")
    print(f"⏱️  Intervalle: {settings.CHECK_INTERVAL}s")
    print("=" * 60)
    
    collector = DataCollector(
        api_key=settings.COINGECKO_API_KEY,
        symbol=settings.CRYPTO_SYMBOL,
        vs_currency=settings.VS_CURRENCY
    )
    
    strategy = RSIStrategy(
        period=settings.RSI_PERIOD,
        oversold=settings.RSI_OVERSOLD,
        overbought=settings.RSI_OVERBOUGHT
    )
    
    while True:
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            price = collector.get_current_price()
            if price is None:
                print(f"\n❌ [{now}] Impossible de récupérer le prix")
                time.sleep(settings.CHECK_INTERVAL)
                continue
            
            df = collector.get_historical_data(days=30)
            if df.empty:
                print(f"\n⚠️  [{now}] Pas de données historiques")
                time.sleep(settings.CHECK_INTERVAL)
                continue
            
            signal, rsi, reason = strategy.generate_signal(df)
            
            print(f"\n{'=' * 60}")
            print(f"🕐 {now}")
            print(f"💰 Prix: ${price:,.2f}")
            
            if signal == 'BUY':
                print(f"🟢 SIGNAL: {signal} - {reason}")
            elif signal == 'SELL':
                print(f"🔴 SIGNAL: {signal} - {reason}")
            else:
                print(f"⚪ SIGNAL: {signal} - {reason}")
            
            print(f"{'=' * 60}")
            
            time.sleep(settings.CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n🛑 Arrêt du bot...")
            break
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            time.sleep(settings.CHECK_INTERVAL)

if __name__ == "__main__":
    main()
EOF

# 8. REQUIREMENTS
cat > requirements.txt << 'EOF'
requests==2.31.0
pandas==2.2.0
python-dotenv==1.0.0
numpy==1.26.3
EOF

# 9. PROCFILE
cat > Procfile << 'EOF'
worker: python main.py
EOF

# 10. RAILWAY.JSON
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

# 11. RESTAURATION .env
if [ -f .env.backup ]; then
    cp .env.backup .env
    echo -e "${GREEN}✅ .env restauré${NC}"
fi

# 12. GIT
git add .

echo ""
echo "=========================================="
echo -e "${GREEN}✅ RECONSTRUCTION TERMINÉE${NC}"
echo "=========================================="
echo "Structure créée:"
ls -la
echo ""
echo "Prochaines étapes:"
echo "  git commit -m 'fix: complete rebuild'"
echo "  git push origin main --force"

