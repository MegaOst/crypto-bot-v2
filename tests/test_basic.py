import sys
sys.path.append('..')

from data.market_data import MarketDataFetcher
from strategies.simple_strategy import SimpleStrategy

def test_fetch():
    print("🧪 Test récupération données...")
    fetcher = MarketDataFetcher()
    df = fetcher.fetch_ohlc(days=7)
    assert len(df) > 0, "Aucune donnée récupérée"
    print(f"   ✅ {len(df)} points récupérés")

def test_strategy():
    print("🧪 Test stratégie...")
    fetcher = MarketDataFetcher()
    strategy = SimpleStrategy()
    df = fetcher.fetch_ohlc(days=7)
    result = strategy.analyze(df)
    assert 'signal' in result, "Pas de signal généré"
    print(f"   ✅ Signal: {result['signal']}")

if __name__ == "__main__":
    test_fetch()
    test_strategy()
    print("\n✅ TOUS LES TESTS PASSÉS\n")
