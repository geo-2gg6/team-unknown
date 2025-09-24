from flask import Flask, jsonify
from flask_cors import CORS
import time, random
from datetime import datetime

app = Flask(__name__)
CORS(app)



@app.route('/scan')
def scan():
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
            "status": "Leaking Data ⚠" if leak else "Safe ✅",
            "timestamp": datetime.now().isoformat()
        })
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
