"""Module de collecte de données CoinGecko."""
import logging
from typing import Optional, Dict, Any
import pandas as pd
import requests
from datetime import datetime, timedelta
from config.settings import config

logger = logging.getLogger(__name__)

class CryptoDataCollector:
    """Collecteur de données crypto depuis CoinGecko."""
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialise le collecteur."""
        self.api_key = api_key or config.COINGECKO_API_KEY
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({'x-cg-pro-api-key': self.api_key})
    
    def get_current_price(self, symbol: str, vs_currency: str = 'usd') -> Optional[Dict[str, Any]]:
        """Récupère le prix actuel."""
        try:
            url = f"{self.BASE_URL}/simple/price"
            params = {
                'ids': symbol,
                'vs_currencies': vs_currency,
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_market_cap': 'true'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if symbol in data:
                return data[symbol]
            
            logger.warning(f"Symbole {symbol} non trouvé")
            return None
            
        except Exception as e:
            logger.error(f"Erreur récupération prix: {e}")
            return None
    
    def get_historical_data(
        self, 
        symbol: str, 
        vs_currency: str = 'usd',
        days: int = 30
    ) -> Optional[pd.DataFrame]:
        """Récupère les données historiques."""
        try:
            url = f"{self.BASE_URL}/coins/{symbol}/market_chart"
            params = {
                'vs_currency': vs_currency,
                'days': days,
                'interval': 'daily'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if 'prices' not in data:
                logger.warning("Pas de données de prix")
                return None
            
            # Conversion en DataFrame
            df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Ajout des volumes si disponibles
            if 'total_volumes' in data:
                volumes = pd.DataFrame(data['total_volumes'], columns=['timestamp', 'volume'])
                volumes['timestamp'] = pd.to_datetime(volumes['timestamp'], unit='ms')
                volumes.set_index('timestamp', inplace=True)
                df = df.join(volumes)
            
            return df
            
        except Exception as e:
            logger.error(f"Erreur récupération historique: {e}")
            return None
