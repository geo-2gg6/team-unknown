from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import time
from datetime import datetime, timezone
import threading
from collections import defaultdict, deque
import atexit
import json
import os
import hashlib
import re

app = Flask(__name__)
CORS(app)

# Store events from browser sessions
app.session_events = defaultdict(lambda: deque(maxlen=1000))  # session_id -> events
app._events_lock = threading.Lock()

# Trust configuration for domain classification
TRUST_CONFIG = {
    "trusted": [
        "google.com", "gstatic.com", "googleapis.com", "microsoft.com", "windowsupdate.com",
        "live.com", "github.com", "githubusercontent.com", "amazonaws.com", "cloudflare.com",
        "akadns.net", "office365.com", "office.com", "facebook.com", "instagram.com",
        "twitter.com", "linkedin.com", "youtube.com", "netflix.com", "spotify.com"
    ],
    "risky": [
        "doubleclick.net", "adservice.google.com", "adsystem.com", "googlesyndication.com",
        "googletagmanager.com", "facebook.com/tr", "analytics", "tracking", "tracker", 
        "pixel", "coinhive", "cryptominer", "malware", "phishing", "ads", "adnxs.com"
    ]
}

def classify_domain(domain):
    """Classify domain as Safe/Risk/Caution"""
    if not domain:
        return "Caution"
    
    domain_lower = domain.lower()
    
    # Check trusted patterns
    for pattern in TRUST_CONFIG["trusted"]:
        if pattern in domain_lower:
            return "Safe"
    
    # Check risky patterns  
    for pattern in TRUST_CONFIG["risky"]:
        if pattern in domain_lower:
            return "Risk"
    
    return "Caution"

def extract_domain(url):
    """Extract domain from URL"""
    try:
        # Remove protocol
        if "://" in url:
            url = url.split("://", 1)[1]
        # Remove path and query
        domain = url.split("/")[0].split("?")[0]
        # Remove port
        domain = domain.split(":")[0]
        return domain
    except:
        return url

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/events")
def api_events():
    """Get events from current session"""
    session_id = request.args.get("session_id", "default")
    try:
        n = int(request.args.get("n", 50))
    except Exception:
        n = 50
    n = max(1, min(n, 500))
    
    with app._events_lock:
        events = list(app.session_events.get(session_id, []))[-n:]
    
    events.reverse()  # Show newest first
    return jsonify({"events": events, "count": len(events)})

@app.route("/api/browser-events", methods=["POST"])
def receive_browser_events():
    """Receive network events from browser"""
    try:
        data = request.get_json()
        if not data or "events" not in data:
            return jsonify({"error": "Invalid payload"}), 400
        
        session_id = data.get("session_id", "default")
        events = data.get("events", [])
        
        with app._events_lock:
            for event in events:
                # Add server timestamp and classification
                event["server_timestamp"] = time.time()
                event["timestamp"] = event.get("timestamp", time.time())
                
                # Extract domain and classify
                url = event.get("url", "")
                domain = extract_domain(url)
                event["domain"] = domain
                event["verdict"] = classify_domain(domain)
                
                # Add session info
                event["session_id"] = session_id
                event["type"] = "browser_request"
                
                app.session_events[session_id].append(event)
        
        return jsonify({"status": "success", "received": len(events)})
        
    except Exception as e:
        print(f"❌ Error receiving browser events: {e}")
        return jsonify({"error": "Server error"}), 500

@app.route("/api/session-stats")
def api_session_stats():
    """Get statistics for current session"""
    session_id = request.args.get("session_id", "default")
    
    with app._events_lock:
        events = list(app.session_events.get(session_id, []))
    
    stats = {
        "total_requests": len(events),
        "safe_count": sum(1 for e in events if e.get("verdict") == "Safe"),
        "risk_count": sum(1 for e in events if e.get("verdict") == "Risk"),
        "caution_count": sum(1 for e in events if e.get("verdict") == "Caution"),
        "unique_domains": len(set(e.get("domain", "") for e in events if e.get("domain"))),
        "last_activity": max((e.get("timestamp", 0) for e in events), default=0)
    }
    
    return jsonify(stats)

if __name__ == "__main__":
    print("🌐 Privacy Scanner - Global Web App")
    print("=" * 40)
    print("📡 Ready to monitor browser network activity")
    print("🔗 Access the dashboard at: http://localhost:5000")
    
    app.run(host="0.0.0.0", port=5000, debug=True)