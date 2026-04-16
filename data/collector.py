"""Module de collecte de données CoinGecko."""
import logging
from typing import Optional, Dict, Any
import pandas as pd
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

class CryptoDataCollector:
    """Collecteur de données via l'API CoinGecko."""
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(self, api_key: str):
        """Initialise le collecteur.
        
        Args:
            api_key: Clé API CoinGecko
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'x-cg-pro-api-key': self.api_key,
            'Accept': 'application/json'
        })
        logger.info(f"✅ Collecteur initialisé avec API key: {self.api_key[:11]}...")
    
    def get_historical_data(
        self,
        symbol: str,
        vs_currency: str = 'usd',
        days: int = 30
    ) -> Optional[pd.DataFrame]:
        """Récupère l'historique des prix.
        
        Args:
            symbol: Symbole de la crypto (ex: 'ethereum')
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
            
            response = self.session.get(url, params=params, timeout=10)
            logger.info(f"📥 Status: {response.status_code}")
            
            response.raise_for_status()
            data = response.json()
            
            if not data or 'prices' not in data:
                logger.error("❌ Réponse invalide de l'API")
                return None
            
            # Construction manuelle du DataFrame (évite les problèmes de merge)
            rows = []
            
            # Longueur minimale pour éviter les index out of range
            n_prices = len(data['prices'])
            n_volumes = len(data.get('total_volumes', []))
            n_rows = min(n_prices, n_volumes) if n_volumes > 0 else n_prices
            
            for i in range(n_rows):
                timestamp_ms, price = data['prices'][i]
                row = {
                    'timestamp': pd.to_datetime(timestamp_ms, unit='ms'),
                    'price': price,
                    'volume': None
                }
                
                # Ajout du volume si disponible
                if 'total_volumes' in data and i < len(data['total_volumes']):
                    _, volume = data['total_volumes'][i]
                    row['volume'] = volume
                
                rows.append(row)
            
            df = pd.DataFrame(rows)
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            logger.info(f"✅ {len(df)} points récupérés (prix + volumes)")
            logger.info(f"📊 Période: {df['timestamp'].min()} → {df['timestamp'].max()}")
            
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur HTTP: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur inattendue: {e}", exc_info=True)
            return None
    
    def get_current_price(self, symbol: str, vs_currency: str = 'usd') -> Optional[float]:
        """Récupère le prix actuel.
        
        Args:
            symbol: Symbole de la crypto
            vs_currency: Devise de référence
            
        Returns:
            Prix actuel ou None
        """
        try:
            url = f"{self.BASE_URL}/simple/price"
            params = {
                'ids': symbol,
                'vs_currencies': vs_currency
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if symbol in data and vs_currency in data[symbol]:
                price = data[symbol][vs_currency]
                logger.info(f"💰 Prix actuel {symbol}: {price} {vs_currency.upper()}")
                return price
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération prix: {e}")
            return None
