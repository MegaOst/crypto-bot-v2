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
