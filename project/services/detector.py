import time
import pickle
import numpy as np
from models import db, Event

MODEL_PATH = 'models/anomaly_detection.pkl'

def detect_anomaly(model, data):
    try:
        prediction = model.predict(data)[0]
        return prediction == 1
    except Exception as e:
        print(f"Detection error: {e}")
        return False

def start_detection_loop(socketio):
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
    except Exception as e:
        print(f"Model load error: {e}")
        model = None

    demo_events = [
        {'event_type': 'data_leak', 'details': 'Device Google Home sent data to suspicious server. Status: risky'},
        {'event_type': 'data_leak', 'details': 'Device Amazon Echo sent data to advertising partner. Status: warning'},
        {'event_type': 'data_leak', 'details': 'Device Philips Hue sent only core data. Status: secure'},
        {'event_type': 'data_leak', 'details': 'Device TP-LINK sent generic cloud communication. Status: unknown'},
    ]
    idx = 0
    while True:
        # Simulate incoming data
        data = np.random.rand(1, 5)
        if model and detect_anomaly(model, data):
            details = f"Anomaly detected: {data.tolist()}"
            event_type = "anomaly"
        else:
            demo = demo_events[idx % len(demo_events)]
            event_type = demo['event_type']
            details = demo['details']
            idx += 1
        event = Event(event_type=event_type, details=details)
        db.session.add(event)
        db.session.commit()
        socketio.emit('new_alert', {
            'timestamp': str(event.timestamp),
            'event_type': event.event_type,
            'details': event.details
        })
        time.sleep(3)
