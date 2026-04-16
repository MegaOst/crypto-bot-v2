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
