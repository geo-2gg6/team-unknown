from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import random
import time
from datetime import datetime, timezone
import threading
from collections import deque
import atexit
import json
import os

try:
    from .monitor import sample_connections
except Exception:  # Fallback when running as a script (no package context)
    from monitor import sample_connections

app = Flask(__name__)
CORS(app)  # allows API calls from same origin / other local dev ports if needed

# Device pool (mock)
DEVICE_POOL = [
    {"name": "Google Home", "manufacturer": "Google"},
    {"name": "Amazon Echo", "manufacturer": "Amazon"},
    {"name": "Philips Hue", "manufacturer": "Philips"},
    {"name": "Ring Camera", "manufacturer": "Ring"},
    {"name": "TP-Link Smart Plug", "manufacturer": "TP-LINK"},
    {"name": "Samsung TV", "manufacturer": "Samsung Electronics"},
    {"name": "Netgear Router", "manufacturer": "Netgear"},
    {"name": "Raspberry Pi", "manufacturer": "Raspberry Pi Foundation"}
]

DEST_POOL = [
    "analytics.google.com",
    "ads.amazon.com",
    "updates.philips.com",
    "s3.amazonaws.com",
    "unknown-xyz.net",
    "tracker.example.org",
    "cloud.ring.com",
    "iot.tp-link.com"
]

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/scan")
def api_scan():
    # Simulate scanning delay
    time.sleep(3)

    # Randomly choose number of devices (0..5)
    n = random.randint(0, 5)
    devices = []
    for i in range(n):
        d = random.choice(DEVICE_POOL)
        # Leak probability - tweak as you like
        leak = random.random() < 0.35
        dest = random.choice(DEST_POOL)
        status = "Leaking Data ⚠" if leak else "Safe ✅"
        devices.append({
            "id": i + 1,
            "name": d["name"],
            "manufacturer": d["manufacturer"],
            "leak": leak,
            "destination": dest,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    return jsonify({"devices": devices})


# --- Background monitoring thread setup ---
app.monitor_events = deque(maxlen=1000)  # type: ignore[attr-defined]
app._monitor_lock = threading.Lock()  # type: ignore[attr-defined]
app._monitor_stop = threading.Event()  # type: ignore[attr-defined]
app._monitor_thread = None  # type: ignore[attr-defined]


def _monitor_loop():
    while not app._monitor_stop.is_set():  # type: ignore[attr-defined]
        try:
            events = sample_connections()
            if events:
                with app._monitor_lock:  # type: ignore[attr-defined]
                    app.monitor_events.extend(events)  # type: ignore[attr-defined]
        except Exception:
            pass
        # Small sleep to avoid tight loop; adjust as needed
        app._monitor_stop.wait(2.0)  # type: ignore[attr-defined]


def _start_monitor_thread_once():
    if getattr(app, "_monitor_thread", None) is None:  # type: ignore[attr-defined]
        app._monitor_stop.clear()  # type: ignore[attr-defined]
        app._monitor_thread = threading.Thread(target=_monitor_loop, name="monitor-thread", daemon=True)  # type: ignore[attr-defined]
        app._monitor_thread.start()  # type: ignore[attr-defined]


def _stop_monitor_thread():
    try:
        app._monitor_stop.set()  # type: ignore[attr-defined]
        t = getattr(app, "_monitor_thread", None)
        if t is not None:
            t.join(timeout=3.0)
    except Exception:
        pass


@app.before_request
def _ensure_monitor_running():
    # Compatible starter for a wide range of Flask versions
    if getattr(app, "_monitor_thread", None) is None:  # type: ignore[attr-defined]
        _start_monitor_thread_once()


atexit.register(_stop_monitor_thread)


@app.route("/api/events")
def api_events():
    try:
        n = int(request.args.get("n", 50))
    except Exception:
        n = 50
    n = max(1, min(n, 500))
    with app._monitor_lock:  # type: ignore[attr-defined]
        # Take the newest N events, return newest-first
        items = list(app.monitor_events)[-n:]  # type: ignore[attr-defined]

    # Trust configuration (destination-based) loaded from JSON if present
    DEFAULT_TRUST_CONFIG = {
        "trusted": [
            "google.com", "gstatic.com", "googleapis.com", "microsoft.com", "windowsupdate.com",
            "live.com", "github.com", "githubusercontent.com", "amazonaws.com", "cloudflare.com",
            "akadns.net", "office365.com", "office.com"
        ],
        "risky": [
            "doubleclick.net", "adservice.google.com", "adsystem.com", "tracking", "tracker", "pixel",
            "coinhive", "cryptominer", "malware", "phishing"
        ]
    }

    def load_trust_config():
        cfg_path = os.path.join(os.path.dirname(__file__), "trust_config.json")
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                t = data.get("trusted", []) or []
                r = data.get("risky", []) or []
                return {"trusted": list(map(str, t)), "risky": list(map(str, r))}
        except Exception:
            return DEFAULT_TRUST_CONFIG

    trust_cfg = load_trust_config()

    # Classify each event into Safe / Caution / Risk
    risky_ports = {21, 23, 25, 135, 139, 445, 3389}
    common_web_ports = {80, 443}

    def classify(ev):
        status = str(ev.get("status", "")).upper()
        raddr = ev.get("raddr") or ""
        try:
            host = str(raddr).rsplit(":", 1)[0] if ":" in str(raddr) else str(raddr)
            port = int(str(raddr).rsplit(":", 1)[-1]) if ":" in str(raddr) else None
        except Exception:
            host, port = str(raddr), None

        # Destination-based rules first
        host_l = host.lower()
        try:
            if any(pat.lower() in host_l for pat in trust_cfg.get("trusted", [])):
                if status in {"ESTABLISHED", "CONNECTED"}:
                    return "Safe"
                return "Caution"
            if any(pat.lower() in host_l for pat in trust_cfg.get("risky", [])):
                return "Risk"
        except Exception:
            pass
        if status not in {"ESTABLISHED", "CONNECTED"}:
            return "Caution"
        if port in risky_ports:
            return "Risk"
        if port in common_web_ports:
            return "Safe"
        return "Caution"

    for ev in items:
        try:
            ev["verdict"] = classify(ev)
        except Exception:
            ev["verdict"] = "Caution"

    items.reverse()
    return jsonify({"events": items, "count": len(items)})


if __name__ == "__main__":
    # Development server
    # Avoid duplicate threads from the reloader by disabling it here.
    _start_monitor_thread_once()
    try:
        app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
    finally:
        _stop_monitor_thread()
