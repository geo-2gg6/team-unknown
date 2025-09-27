from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import time
from datetime import datetime, timezone
import threading
from collections import defaultdict, deque
import atexit
import json
import os

app = Flask(__name__)
CORS(app)

# Store events from multiple devices
app.device_events = defaultdict(lambda: deque(maxlen=1000))  # device_id -> events
app._events_lock = threading.Lock()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/events")
def api_events():
    """Get events from all devices or a specific device"""
    device_id = request.args.get("device_id")
    try:
        n = int(request.args.get("n", 50))
    except Exception:
        n = 50
    n = max(1, min(n, 500))
    
    with app._events_lock:
        if device_id:
            # Get events from specific device
            events = list(app.device_events.get(device_id, []))[-n:]
        else:
            # Get events from all devices, sorted by timestamp
            all_events = []
            for device_events in app.device_events.values():
                all_events.extend(device_events)
            all_events.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
            events = all_events[:n]
    
    events.reverse()  # Show newest first
    return jsonify({"events": events, "count": len(events)})

@app.route("/api/device-events", methods=["POST"])
def receive_device_events():
    """Receive events from local agents"""
    try:
        data = request.get_json()
        if not data or "events" not in data:
            return jsonify({"error": "Invalid payload"}), 400
        
        device_id = data.get("device_id", "unknown")
        events = data.get("events", [])
        
        with app._events_lock:
            for event in events:
                # Add server timestamp
                event["server_timestamp"] = time.time()
                app.device_events[device_id].append(event)
        
        print(f"📥 Received {len(events)} events from device {device_id}")
        return jsonify({"status": "success", "received": len(events)})
        
    except Exception as e:
        print(f"❌ Error receiving events: {e}")
        return jsonify({"error": "Server error"}), 500

@app.route("/api/devices")
def api_devices():
    """Get list of connected devices"""
    with app._events_lock:
        devices = []
        for device_id, events in app.device_events.items():
            if events:
                latest_event = max(events, key=lambda x: x.get("timestamp", 0))
                devices.append({
                    "device_id": device_id,
                    "last_seen": latest_event.get("timestamp", 0),
                    "event_count": len(events),
                    "latest_process": latest_event.get("process_name", "Unknown")
                })
        
        devices.sort(key=lambda x: x["last_seen"], reverse=True)
        return jsonify({"devices": devices})

if __name__ == "__main__":
    print("🌐 Privacy Scanner - Cloud Backend")
    print("=" * 40)
    print("📡 Ready to receive data from local agents")
    print("🔗 Access the dashboard at: http://localhost:5000")
    
    app.run(host="0.0.0.0", port=5000, debug=True)