import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Dict, Optional
from config import BASE_URL, COINGECKO_API_KEY, SYMBOL, VS_CURRENCY, CACHE_TTL
from utils.logger import setup_logger

logger = setup_logger(__name__)

class MarketDataFetcher:
    def __init__(self):
        self.cache: Dict = {}
        self.cache_timestamp: Optional[datetime] = None
        self.headers = {'x-cg-demo-api-key': COINGECKO_API_KEY} if COINGECKO_API_KEY else {}
    
    def fetch_ohlc(self, days: int = 30) -> pd.DataFrame:
        if self._is_cache_valid():
            logger.info("📦 Utilisation du cache")
            return self.cache['data']
        
        url = f"{BASE_URL}/coins/{SYMBOL}/ohlc"
        params = {'vs_currency': VS_CURRENCY, 'days': days}
        
        try:
            time.sleep(6)  # Rate limiting
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            self.cache = {'data': df, 'timestamp': datetime.now()}
            self.cache_timestamp = datetime.now()
            
            logger.info(f"✅ {len(df)} points récupérés")
            return df
            
        except requests.RequestException as e:
            logger.error(f"❌ Erreur API: {e}")
            if self.cache:
                logger.warning("⚠️  Utilisation ancien cache")
                return self.cache['data']
            raise
    
    def _is_cache_valid(self) -> bool:
        if not self.cache or not self.cache_timestamp:
            return False
        return (datetime.now() - self.cache_timestamp).seconds < CACHE_TTL
