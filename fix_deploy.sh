#!/bin/bash

echo "🔧 Correction du déploiement..."

# 1. CORRIGER LE PROCFILE
cat > Procfile << 'EOF'
web: python web/app.py
EOF

# 2. CORRIGER LE PORT DANS app.py
cat > web/app.py << 'EOF'
from flask import Flask, render_template, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    try:
        with open('portfolio_stats.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({
            'cash': 10000,
            'crypto_held': 0,
            'total_value': 10000,
            'profit': 0,
            'profit_pct': 0,
            'current_price': 0,
            'current_rsi': 0,
            'last_signal': 'HOLD',
            'trades': [],
            'last_update': datetime.now().isoformat()
        })

if __name__ == '__main__':
    # Railway fournit la variable PORT
    port = int(os.environ.get('PORT', 8080))
    # Écoute sur 0.0.0.0 pour être accessible
    app.run(host='0.0.0.0', port=port, debug=False)
EOF

# 3. VÉRIFIER requirements.txt
if ! grep -q "flask" requirements.txt; then
    echo "flask==3.0.0" >> requirements.txt
fi

echo ""
echo "✅ Corrections appliquées"
echo ""
echo "Maintenant:"
echo "  git add ."
echo "  git commit -m 'fix: correct Flask deployment'"
echo "  git push origin main"

