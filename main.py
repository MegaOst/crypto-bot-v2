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
