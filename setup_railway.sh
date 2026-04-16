#!/bin/bash

echo "🚀 Configuration Railway pour Flask..."
echo ""

# Aller à la racine du projet
cd ~/crypto-trading-bot

# Créer nixpacks.toml
cat > nixpacks.toml << 'ENDFILE'
[phases.setup]
nixPkgs = ['python3', 'gcc']

[phases.install]
cmds = ['python -m venv --copies /opt/venv', '. /opt/venv/bin/activate && pip install -r requirements.txt']

[start]
cmd = '. /opt/venv/bin/activate && gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 web.app:app'
ENDFILE

# Créer Procfile
cat > Procfile << 'ENDFILE'
web: gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 web.app:app
ENDFILE

# Créer requirements.txt
cat > requirements.txt << 'ENDFILE'
flask==3.0.0
gunicorn==21.2.0
requests==2.31.0
pandas==2.1.4
numpy==1.26.2
python-dotenv==1.0.0
ENDFILE

# Créer le dossier web
mkdir -p web
touch web/__init__.py

# Créer web/app.py
cat > web/app.py << 'ENDFILE'
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Flask OK</h1><p>Server running</p>'

@app.route('/health')
def health():
    return 'OK', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
ENDFILE

# Afficher les résultats
echo ""
echo "✅ Fichiers créés :"
ls -la | grep -E "nixpacks|Procfile|requirements|web"
echo ""
echo "✅ Contenu web/ :"
ls -la web/
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📄 nixpacks.toml :"
cat nixpacks.toml
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📄 Procfile :"
cat Procfile
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Configuration terminée !"
echo ""
echo "🚀 Pour déployer :"
echo "   git add ."
echo "   git commit -m 'fix: railway config'"
echo "   git push origin main"
