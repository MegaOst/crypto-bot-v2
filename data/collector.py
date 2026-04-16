"""Module de collecte de données CoinGecko."""
import logging
from typing import Optional, Dict, Any, List
import pandas as pd
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CryptoDataCollector:
    """Collecteur de données crypto depuis CoinGecko."""
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(self, api_key: str):
        """
        Initialise le collecteur.
        
        Args:
            api_key: Clé API CoinGecko
        """
        if not api_key or not isinstance(api_key, str):
            raise ValueError(f"API key invalide: {type(api_key)}")
        
        self.api_key = api_key.strip()
        self.session = requests.Session()
        self.session.headers.update({
            'x-cg-pro-api-key': self.api_key,
            'User-Agent': 'CryptoBot/1.0'
        })
        logger.info(f"✅ Collecteur initialisé avec API key: {self.api_key[:10]}...")
    
    def get_current_price(self, symbol: str, vs_currency: str = 'usd') -> Optional[Dict[str, Any]]:
        """
        Récupère le prix actuel.
        
        Args:
            symbol: Symbole de la crypto (ex: 'ethereum')
            vs_currency: Devise de référence (ex: 'usd')
            
        Returns:
            Dictionnaire avec price, change_24h, etc.
        """
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
            
            if symbol not in data:
                logger.error(f"Symbole {symbol} non trouvé")
                return None
            
            return data[symbol]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération du prix: {e}")
            return None
    
    def get_historical_data(
        self,
        symbol: str,
        vs_currency: str = 'usd',
        days: int = 30
    ) -> Optional[pd.DataFrame]:
        """
        Récupère l'historique des prix.
        
        Args:
            symbol: Symbole de la crypto
            vs_currency: Devise de référence
            days: Nombre de jours d'historique
            
        Returns:
            DataFrame avec colonnes: timestamp, price, volume
        """
        try:
            url = f"{self.BASE_URL}/coins/{symbol}/market_chart"
            params = {
                'vs_currency': vs_currency,
                'days': days,
                'interval': 'daily'
            }
            
            logger.info(f"📡 Requête: {url}")
            logger.info(f"📋 Params: {params}")
            
            response = self.session.get(url, params=params, timeout=15)
            
            logger.info(f"📥 Status: {response.status_code}")
            
            response.raise_for_status()
            data = response.json()
            
            if 'prices' not in data or not data['prices']:
                logger.warning("Pas de données de prix dans la réponse")
                return None
            
            # Conversion en DataFrame
            df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Ajout des volumes si disponibles
            if 'total_volumes' in data and data['total_volumes']:
                volumes = pd.DataFrame(data['total_volumes'], columns=['timestamp', 'volume'])
                df = df.merge(volumes, on='timestamp', how='left')
            
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            logger.info(f"✅ {len(df)} lignes récupérées")
            return df
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ Erreur HTTP lors de la récupération de l'historique: {e}")
            logger.error(f"Response: {e.response.text if hasattr(e, 'response') else 'N/A'}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur réseau: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur inattendue: {e}", exc_info=True)
            return None
