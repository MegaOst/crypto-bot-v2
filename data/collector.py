"""
Module de collecte des données depuis l'API CoinGecko
"""

import requests
import logging
from datetime import datetime
from typing import Optional
import pandas as pd

logger = logging.getLogger(__name__)

class CryptoDataCollector:
    """Collecteur de données crypto via CoinGecko API"""
    
    def __init__(self, api_key: str):
        """
        Initialise le collecteur
        
        Args:
            api_key: Clé API CoinGecko Pro
        """
        self.api_key = api_key
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = requests.Session()
        self.session.headers.update({
            'x-cg-pro-api-key': api_key,
            'Accept': 'application/json'
        })
        logger.info(f"✅ Collecteur initialisé avec API key: {api_key[:10]}...")
    
    def get_market_data(
        self,
        symbol: str,
        vs_currency: str = 'usd',
        days: int = 30
    ) -> Optional[pd.DataFrame]:
        """
        Récupère l'historique de prix
        
        Args:
            symbol: Symbole crypto (ex: 'bitcoin', 'ethereum')
            vs_currency: Devise de référence (ex: 'usd', 'eur')
            days: Nombre de jours d'historique
            
        Returns:
            DataFrame avec colonnes [timestamp, price, volume]
        """
        endpoint = f"{self.base_url}/coins/{symbol}/market_chart"
        
        params = {
            'vs_currency': vs_currency,
            'days': days
        }
        
        try:
            logger.info(f"📡 Requête: {endpoint}")
            logger.info(f"📋 Params: {params}")
            
            response = self.session.get(
                endpoint,
                params=params,
                timeout=30
            )
            
            logger.info(f"📥 Status: {response.status_code}")
            response.raise_for_status()
            
            data = response.json()
            
            # Extraction des prix et volumes
            prices = data.get('prices', [])
            volumes = data.get('total_volumes', [])
            
            if not prices:
                logger.error("❌ Aucune donnée de prix reçue")
                return None
            
            # Conversion en DataFrame
            df_prices = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df_volumes = pd.DataFrame(volumes, columns=['timestamp', 'volume'])
            
            # Fusion des deux DataFrames
            df = pd.merge(df_prices, df_volumes, on='timestamp', how='left')
            
            # Conversion timestamp en datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Tri par date
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            logger.info(f"✅ {len(df)} points récupérés (prix + volumes)")
            logger.info(f"📊 Période: {df['timestamp'].min()} → {df['timestamp'].max()}")
            
            return df
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ Erreur HTTP: {e}")
            return None
        except requests.exceptions.Timeout:
            logger.error("❌ Timeout de la requête")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur réseau: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur inattendue: {e}")
            return None
    
    def get_current_price(self, symbol: str, vs_currency: str = 'usd') -> Optional[float]:
        """
        Récupère le prix actuel
        
        Args:
            symbol: Symbole crypto
            vs_currency: Devise de référence
            
        Returns:
            Prix actuel ou None
        """
        endpoint = f"{self.base_url}/simple/price"
        
        params = {
            'ids': symbol,
            'vs_currencies': vs_currency
        }
        
        try:
            response = self.session.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            price = data.get(symbol, {}).get(vs_currency)
            
            if price:
                logger.info(f"💰 Prix actuel {symbol}: {price} {vs_currency.upper()}")
                return float(price)
            else:
                logger.warning(f"⚠️ Prix non trouvé pour {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erreur récupération prix: {e}")
            return None
