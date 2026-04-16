"""Module de collecte des données de marché"""

import requests
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class CryptoDataCollector:
    """Collecteur de données depuis CoinGecko"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.coingecko.com/api/v3"
        self.cache = {}
        self.cache_duration = 180  # 3 minutes
        
    def get_price(self, symbol: str, vs_currency: str = "usd") -> Optional[float]:
        """Récupère le prix actuel"""
        cache_key = f"{symbol}_{vs_currency}_price"
        
        # Vérifier le cache
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_duration:
                return cached_data
        
        try:
            url = f"{self.base_url}/simple/price"
            params = {
                "ids": symbol,
                "vs_currencies": vs_currency
            }
            
            if self.api_key:
                params["x_cg_pro_api_key"] = self.api_key
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            price = data.get(symbol, {}).get(vs_currency)
            
            if price:
                self.cache[cache_key] = (price, time.time())
                return price
            
            return None
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération du prix: {e}")
            return None
    
    def get_historical_data(
        self, 
        symbol: str, 
        vs_currency: str = "usd",
        days: int = 7
    ) -> List[Dict]:
        """Récupère les données historiques"""
        cache_key = f"{symbol}_{vs_currency}_history_{days}"
        
        # Vérifier le cache
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_duration:
                return cached_data
        
        try:
            url = f"{self.base_url}/coins/{symbol}/market_chart"
            params = {
                "vs_currency": vs_currency,
                "days": days,
                "interval": "hourly" if days <= 7 else "daily"
            }
            
            if self.api_key:
                params["x_cg_pro_api_key"] = self.api_key
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            prices = data.get("prices", [])
            
            # Formater les données
            formatted_data = [
                {
                    "timestamp": datetime.fromtimestamp(price[0] / 1000),
                    "price": price[1]
                }
                for price in prices
            ]
            
            self.cache[cache_key] = (formatted_data, time.time())
            return formatted_data
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération de l'historique: {e}")
            return []
    
    def clear_cache(self):
        """Vide le cache"""
        self.cache = {}
