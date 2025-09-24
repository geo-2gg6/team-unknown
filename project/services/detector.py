import time
import pickle
import numpy as np
from flask_socketio import SocketIO
from models import db, Event

MODEL_PATH = 'models/anomaly_detection.pkl'

class Detector:
    def __init__(self, socketio):
        self.socketio = socketio
        with open(MODEL_PATH, 'rb') as f:
            self.model = pickle.load(f)

    def run(self):
        while True:
            # Simulate incoming data
            data = np.random.rand(1, 5)
            prediction = self.model.predict(data)[0]
            if prediction == 1:  # 1 = anomaly
                event = Event(event_type='anomaly', details=f'Detected anomaly: {data.tolist()}')
                db.session.add(event)
                db.session.commit()
                self.socketio.emit('new_event', {
                    'timestamp': str(event.timestamp),
                    'event_type': event.event_type,
                    'details': event.details
                })
            time.sleep(3)  # Simulate periodic check
