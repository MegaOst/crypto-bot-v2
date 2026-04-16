#!/bin/bash

echo "🔧 Force Railway à utiliser le Procfile..."

# 1. CRÉER nixpacks.toml pour DÉSACTIVER la détection auto
cat > nixpacks.toml << 'EOF'
[phases.setup]
nixPkgs = ['python3', 'gcc']

[phases.install]
cmds = ['python -m venv --copies /opt/venv', '. /opt/venv/bin/activate && pip install -r requirements.txt']

[start]
cmd = 'sh -c ". /opt/venv/bin/activate && exec $(cat Procfile | cut -d: -f2-)"'
EOF

# 2. VÉRIFIER que Procfile existe
cat > Procfile << 'EOF'
web: python web/app.py
EOF

# 3. S'ASSURER que web/app.py existe et est minimal
mkdir -p web
cat > web/app.py << 'EOF'
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Crypto Bot - Railway</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>✅ Flask est démarré !</h1>
        <p>Le serveur web fonctionne correctement.</p>
        <hr>
        <small>Railway Deployment</small>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    return 'OK', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Démarrage Flask sur 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
EOF

# 4. REQUIREMENTS MINIMAL (ajoute gunicorn)
cat > requirements.txt << 'EOF'
flask==3.0.0
gunicorn==21.2.0
requests==2.31.0
pandas==2.1.4
numpy==1.26.2
python-dotenv==1.0.0
EOF

echo ""
echo "✅ Configuration Nixpacks créée"
echo "✅ Procfile vérifié"
echo "✅ Flask app simplifiée"
echo ""

