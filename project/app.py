import eventlet
eventlet.monkey_patch()
from flask import Flask, jsonify
from flask_cors import CORS
import time, random
from datetime import datetime
from config import Config
from models import db
from threading import Thread
from services.detector import start_detection_loop
from routes.main import main_bp
from routes.privacy import privacy_bp

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
CORS(app)

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(privacy_bp)

# Simulated scan API for React frontend
@app.route('/api/scan', methods=['GET'])
def api_scan():
    time.sleep(3)  # Simulate scanning delay
    devices = [
        "Google Home",
        "Philips Hue",
        "TP-Link",
        "Amazon Echo"
    ]
    results = []
    for name in devices:
        leak = random.choice([True, False])
        results.append({
            "name": name,
            "leak": leak,
            "timestamp": datetime.now().isoformat(),
            "status": "Leaking Data ⚠" if leak else "Safe ✅"
        })
    return jsonify(results)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
