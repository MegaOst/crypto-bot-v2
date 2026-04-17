from flask import Flask, jsonify
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    logger.info("Health check: OK")
    return jsonify({"status": "healthy", "message": "Crypto Trading Bot"}), 200

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/api/status')
def api_status():
    return jsonify({
        "running": True,
        "message": "Bot is running"
    }), 200

if __name__ == '__main__':
    logger.info("Starting Flask app...")
    app.run(host='0.0.0.0', port=8000)
