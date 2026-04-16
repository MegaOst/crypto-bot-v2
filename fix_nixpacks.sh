#!/bin/bash

echo "🚀 Configuration Railway pour Flask..."
echo ""

# 1. ALLER À LA RACINE DU PROJET
cd ~/crypto-trading-bot

# 2. CRÉER nixpacks.toml
cat > nixpacks.toml << 'EOF'
[phases.setup]
nixPkgs = ['python3', 'gcc']

[phases.install]
cmds = ['python -m venv --copies /opt/venv', '. /opt/venv/bin/activate && pip install -r requirements.txt']

[start]
cmd = '. /opt/venv/bin/activate && gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 web.app:app'
EOF

# 3. CRÉER Procfile
cat > Procfile << 'EOF'
web: gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 web.app:app
EOF

# 4. CRÉER requirements.txt
cat > requirements.txt << 'EOF'
flask==3.0.0
gunicorn==21.2.0
requests==2.31.0
pandas==2.1.4
numpy==1.26.2
python-dotenv==1.0.0
EOF

# 5. CRÉER le dossier web/
mkdir -p web

# 6. CRÉER web/__init__.py (vide)
touch web/__init__.py

# 7. CRÉER web/app.py
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

# 8. AFFICHER CE QUI A ÉTÉ CRÉÉ
echo ""
echo "✅ Fichiers créés :"
echo ""
ls -la | grep -E "(nixpacks|Procfile|requirements|web)"
echo ""
echo "✅ Contenu de web/ :"
ls -la web/
echo ""

# 9. VÉRIFIER LES FICHIERS
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📄 nixpacks.toml :"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat nixpacks.toml
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📄 Procfile :"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat Procfile
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📄 requirements.txt :"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat requirements.txt
echo ""

# 10. GIT STATUS
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 Git Status :"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git status
echo ""

echo "✅ Configuration terminée !"
echo ""
echo "🚀 Pour déployer, exécute :"
echo "   git add ."
echo "   git commit -m 'fix: add nixpacks and Flask app'"
echo "   git push origin main"
