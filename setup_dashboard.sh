#!/bin/bash

echo "=========================================="
echo "🌐 INSTALLATION DASHBOARD WEB"
echo "=========================================="

# 1. AJOUTER FLASK
echo -e "\n📦 Ajout de Flask..."
cat >> requirements.txt << 'EOF'
flask==3.0.0
EOF

# 2. CRÉER STRUCTURE WEB
echo -e "\n📁 Création structure web..."
mkdir -p web/templates web/static

# 3. PORTFOLIO SIMULATOR
cat > strategies/portfolio.py << 'EOF'
from datetime import datetime
import json

class PortfolioSimulator:
    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.crypto_held = 0
        self.trades = []
        self.current_price = 0
        self.current_rsi = 0
        self.last_signal = 'HOLD'
    
    def execute_signal(self, signal, price, rsi):
        self.current_price = price
        self.current_rsi = rsi
        self.last_signal = signal
        
        if signal == 'BUY' and self.cash > 0:
            amount = self.cash / price
            self.crypto_held += amount
            self.trades.append({
                'type': 'BUY',
                'price': price,
                'amount': amount,
                'date': datetime.now().isoformat()
            })
            print(f"💰 ACHAT: {amount:.6f} crypto @ ${price:,.2f}")
            self.cash = 0
            
        elif signal == 'SELL' and self.crypto_held > 0:
            self.cash = self.crypto_held * price
            self.trades.append({
                'type': 'SELL',
                'price': price,
                'amount': self.crypto_held,
                'date': datetime.now().isoformat()
            })
            print(f"💸 VENTE: {self.crypto_held:.6f} crypto @ ${price:,.2f}")
            self.crypto_held = 0
        
        self.save_stats()
        self.print_stats()
    
    def get_current_value(self):
        return self.cash + (self.crypto_held * self.current_price)
    
    def get_profit(self):
        return self.get_current_value() - self.initial_capital
    
    def get_profit_pct(self):
        return (self.get_profit() / self.initial_capital) * 100
    
    def print_stats(self):
        current_value = self.get_current_value()
        profit = self.get_profit()
        profit_pct = self.get_profit_pct()
        
        print(f"\n📊 PORTFOLIO")
        print(f"   💵 Cash: ${self.cash:,.2f}")
        print(f"   🪙  Crypto: {self.crypto_held:.6f}")
        print(f"   💎 Valeur: ${current_value:,.2f}")
        print(f"   {'📈' if profit > 0 else '📉'} P&L: ${profit:,.2f} ({profit_pct:+.2f}%)")
        print(f"   🔢 Trades: {len(self.trades)}")
    
    def save_stats(self):
        """Sauvegarde les stats pour le dashboard"""
        stats = {
            'price': self.current_price,
            'rsi': self.current_rsi,
            'signal': self.last_signal,
            'cash': self.cash,
            'crypto_held': self.crypto_held,
            'portfolio_value': self.get_current_value(),
            'profit': self.get_profit(),
            'profit_pct': self.get_profit_pct(),
            'total_trades': len(self.trades),
            'trades': self.trades[-10:],  # Derniers 10 trades
            'last_update': datetime.now().isoformat()
        }
        
        with open('web/stats.json', 'w') as f:
            json.dump(stats, f, indent=2)
EOF

# 4. DASHBOARD FLASK
cat > web/app.py << 'EOF'
from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

@app.route('/')
def dashboard():
    try:
        with open('stats.json', 'r') as f:
            data = json.load(f)
    except:
        data = {
            'price': 0,
            'rsi': 0,
            'signal': 'WAITING',
            'cash': 10000,
            'crypto_held': 0,
            'portfolio_value': 10000,
            'profit': 0,
            'profit_pct': 0,
            'total_trades': 0,
            'trades': [],
            'last_update': 'N/A'
        }
    
    return render_template('dashboard.html', **data)

@app.route('/api/stats')
def api_stats():
    """API pour rafraîchir sans recharger la page"""
    try:
        with open('stats.json', 'r') as f:
            return jsonify(json.load(f))
    except:
        return jsonify({'error': 'No data yet'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
EOF

# 5. TEMPLATE HTML
cat > web/templates/dashboard.html << 'EOF'
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Trading Bot Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .last-update {
            color: #888;
            font-size: 0.9em;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .metric {
            background: rgba(255,255,255,0.05);
            padding: 25px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .metric:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .metric-label {
            font-size: 0.9em;
            color: #888;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
        }
        
        .signal {
            padding: 8px 16px;
            border-radius: 20px;
            display: inline-block;
            font-weight: bold;
            font-size: 1.2em;
        }
        
        .signal-BUY {
            background: #00ff0033;
            color: #00ff00;
            border: 2px solid #00ff00;
        }
        
        .signal-SELL {
            background: #ff000033;
            color: #ff0000;
            border: 2px solid #ff0000;
        }
        
        .signal-HOLD {
            background: #ffaa0033;
            color: #ffaa00;
            border: 2px solid #ffaa00;
        }
        
        .profit { color: #00ff00; }
        .loss { color: #ff0000; }
        
        .trades-section {
            background: rgba(255,255,255,0.05);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .trades-section h2 {
            margin-bottom: 20px;
        }
        
        .trade-item {
            background: rgba(255,255,255,0.03);
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .trade-BUY {
            border-left: 4px solid #00ff00;
        }
        
        .trade-SELL {
            border-left: 4px solid #ff0000;
        }
        
        .loading {
            text-align: center;
            padding: 50px;
            font-size: 1.5em;
            color: #888;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .updating {
            animation: pulse 2s infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 Trading Bot Dashboard</h1>
            <div class="last-update">Dernière mise à jour: <span id="lastUpdate">{{ last_update }}</span></div>
        </header>
        
        <div class="metrics-grid">
            <div class="metric">
                <div class="metric-label">💰 Prix actuel</div>
                <div class="metric-value" id="price">${{ "%.2f"|format(price) }}</div>
            </div>
            
            <div class="metric">
                <div class="metric-label">📊 RSI</div>
                <div class="metric-value" id="rsi">{{ "%.2f"|format(rsi) }}</div>
            </div>
            
            <div class="metric">
                <div class="metric-label">🎯 Signal</div>
                <div class="metric-value">
                    <span class="signal signal-{{ signal }}" id="signal">{{ signal }}</span>
                </div>
            </div>
            
            <div class="metric">
                <div class="metric-label">💵 Cash disponible</div>
                <div class="metric-value" id="cash">${{ "%.2f"|format(cash) }}</div>
            </div>
            
            <div class="metric">
                <div class="metric-label">🪙 Crypto détenu</div>
                <div class="metric-value" id="crypto">{{ "%.6f"|format(crypto_held) }}</div>
            </div>
            
            <div class="metric">
                <div class="metric-label">💎 Valeur Portfolio</div>
                <div class="metric-value" id="portfolio">${{ "%.2f"|format(portfolio_value) }}</div>
            </div>
            
            <div class="metric">
                <div class="metric-label">📈 Profit/Loss</div>
                <div class="metric-value {{ 'profit' if profit > 0 else 'loss' }}" id="profit">
                    ${{ "%.2f"|format(profit) }} ({{ "%+.2f"|format(profit_pct) }}%)
                </div>
            </div>
            
            <div class="metric">
                <div class="metric-label">🔢 Trades exécutés</div>
                <div class="metric-value" id="totalTrades">{{ total_trades }}</div>
            </div>
        </div>
        
        <div class="trades-section">
            <h2>📜 Derniers trades</h2>
            <div id="tradesList">
                {% if trades %}
                    {% for trade in trades %}
                    <div class="trade-item trade-{{ trade.type }}">
                        <div>
                            <strong>{{ trade.type }}</strong> - 
                            {{ "%.6f"|format(trade.amount) }} @ ${{ "%.2f"|format(trade.price) }}
                        </div>
                        <div style="color: #888;">{{ trade.date[:19] }}</div>
                    </div>
                    {% endfor %}
                {% else %}
                    <div class="loading">Aucun trade pour le moment...</div>
                {% endif %}
            </div>
        </div>
    </div>
    
    <script>
        // Auto-refresh toutes les 10 secondes
        setInterval(async () => {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                // Mise à jour des métriques
                document.getElementById('price').textContent = '$' + data.price.toFixed(2);
                document.getElementById('rsi').textContent = data.rsi.toFixed(2);
                document.getElementById('signal').textContent = data.signal;
                document.getElementById('signal').className = 'signal signal-' + data.signal;
                document.getElementById('cash').textContent = '$' + data.cash.toFixed(2);
                document.getElementById('crypto').textContent = data.crypto_held.toFixed(6);
                document.getElementById('portfolio').textContent = '$' + data.portfolio_value.toFixed(2);
                
                const profitElem = document.getElementById('profit');
                profitElem.textContent = '$' + data.profit.toFixed(2) + ' (' + 
                    (data.profit_pct >= 0 ? '+' : '') + data.profit_pct.toFixed(2) + '%)';
                profitElem.className = 'metric-value ' + (data.profit >= 0 ? 'profit' : 'loss');
                
                document.getElementById('totalTrades').textContent = data.total_trades;
                document.getElementById('lastUpdate').textContent = data.last_update;
                
                // Mise à jour des trades
                if (data.trades && data.trades.length > 0) {
                    const tradesList = document.getElementById('tradesList');
                    tradesList.innerHTML = data.trades.map(trade => `
                        <div class="trade-item trade-${trade.type}">
                            <div>
                                <strong>${trade.type}</strong> - 
                                ${trade.amount.toFixed(6)} @ $${trade.price.toFixed(2)}
                            </div>
                            <div style="color: #888;">${trade.date.substring(0, 19)}</div>
                        </div>
                    `).join('');
                }
            } catch (error) {
                console.error('Erreur refresh:', error);
            }
        }, 10000);
    </script>
</body>
</html>
EOF

# 6. MODIFIER MAIN.PY
cat > main.py << 'EOF'
import time
from config.settings import settings
from data.collector import DataCollector
from strategies.rsi_strategy import RSIStrategy
from strategies.portfolio import PortfolioSimulator
from datetime import datetime

def main():
    print("\n" + "=" * 60)
    print("🚀 TRADING BOT AVEC DASHBOARD DÉMARRÉ")
    print("=" * 60)
    print(f"📊 Crypto: {settings.CRYPTO_SYMBOL.upper()}")
    print(f"💱 Devise: {settings.VS_CURRENCY.upper()}")
    print(f"📈 RSI: {settings.RSI_PERIOD} / {settings.RSI_OVERSOLD} / {settings.RSI_OVERBOUGHT}")
    print(f"⏱️  Intervalle: {settings.CHECK_INTERVAL}s")
    print(f"🌐 Dashboard: http://localhost:8080")
    print("=" * 60 + "\n")
    
    collector = DataCollector()
    strategy = RSIStrategy()
    portfolio = PortfolioSimulator(initial_capital=10000)
    
    while True:
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            df = collector.get_market_data()
            
            if df is None or df.empty:
                print(f"⚠️  Pas de données, nouvelle tentative dans {settings.CHECK_INTERVAL}s...")
                time.sleep(settings.CHECK_INTERVAL)
                continue
            
            df = strategy.calculate_indicators(df)
            signal, rsi, reason = strategy.generate_signal(df)
            price = df['price'].iloc[-1]
            
            print(f"\n{'=' * 60}")
            print(f"🕐 {now}")
            print(f"💰 Prix: ${price:,.2f}")
            print(f"📊 RSI: {rsi:.2f}")
            
            if signal == 'BUY':
                print(f"🟢 SIGNAL: {signal} - {reason}")
            elif signal == 'SELL':
                print(f"🔴 SIGNAL: {signal} - {reason}")
            else:
                print(f"⚪ SIGNAL: {signal} - {reason}")
            
            # Exécuter le signal et sauvegarder les stats
            portfolio.execute_signal(signal, price, rsi)
            
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
EOF

# 7. MODIFIER PROCFILE (2 workers)
cat > Procfile << 'EOF'
web: cd web && python app.py
worker: python main.py
EOF

echo ""
echo "=========================================="
echo "✅ DASHBOARD INSTALLÉ"
echo "=========================================="
echo ""
echo "Prochaines étapes:"
echo "  git add ."
echo "  git commit -m 'feat: add web dashboard'"
echo "  git push origin main"

