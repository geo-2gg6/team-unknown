from flask import Flask, render_template
from flask_socketio import SocketIO
from config import Config
from models import db, Event
from threading import Thread
from services.detector import Detector
import eventlet

eventlet.monkey_patch()

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
socketio = SocketIO(app, async_mode='eventlet')

def start_detector():
    with app.app_context():
        detector = Detector(socketio)
        detector.run()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/privacy')
def privacy():
    events = Event.query.order_by(Event.timestamp.desc()).all()
    return render_template('privacy.html', events=events)

if __name__ == '__main__':
    # Create DB tables if not exist
    with app.app_context():
        db.create_all()
    # Start background detector thread
    Thread(target=start_detector, daemon=True).start()
    socketio.run(app, debug=True)
