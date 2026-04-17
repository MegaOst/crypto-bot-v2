"""
Récupération données marché avec retry et timeout
"""
import ccxt
import pandas as pd
import time
from utils.logger import setup_logger
from config import config

logger = setup_logger('market_data')

class MarketData:
    """Gestion données marché via CCXT"""
    
    def __init__(self, exchange_name='binance'):
        try:
            exchange_class = getattr(ccxt, exchange_name)
            self.exchange = exchange_class({
                'timeout': config.CCXT_TIMEOUT,
                'enableRateLimit': True
            })
            logger.info(f"✅ Exchange {exchange_name} initialisé")
        except Exception as e:
            logger.error(f"❌ Erreur init exchange: {e}")
            raise
    
    def get_ohlcv(self, symbol, timeframe='5m', limit=100):
        """
        Récupère les données OHLCV avec retry
        
        Args:
            symbol: Paire de trading
            timeframe: Intervalle
            limit: Nombre de bougies
        
        Returns:
            DataFrame avec OHLCV
        """
        for attempt in range(config.RETRY_ATTEMPTS):
            try:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                
                if not ohlcv:
                    logger.warning(f"⚠️ Données vides pour {symbol}")
                    return pd.DataFrame()
                
                df = pd.DataFrame(
                    ohlcv, 
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                
                logger.info(f"📊 {len(df)} bougies récupérées pour {symbol}")
                return df
                
            except ccxt.NetworkError as e:
                logger.warning(f"⚠️ Erreur réseau (tentative {attempt+1}/{config.RETRY_ATTEMPTS}): {e}")
                time.sleep(2 ** attempt)  # Backoff exponentiel
            except ccxt.ExchangeError as e:
                logger.error(f"❌ Erreur exchange: {e}")
                return pd.DataFrame()
            except Exception as e:
                logger.error(f"❌ Erreur inattendue: {e}")
                return pd.DataFrame()
        
        logger.error(f"❌ Échec après {config.RETRY_ATTEMPTS} tentatives")
        return pd.DataFrame()
    
    def get_current_price(self, symbol):
        """Récupère le prix actuel"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return float(ticker['last'])
        except Exception as e:
            logger.error(f"❌ Erreur prix: {e}")
            return 0.0
