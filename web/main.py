from flask import Flask, render_template, jsonify
import os

app = Flask(__name__, 
            template_folder='web/templates',
            static_folder='web/static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def status():
    return jsonify({
        'running': True,
        'message': 'Bot is running'
    })

@app.route('/api/positions')
def positions():
    return jsonify([])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)