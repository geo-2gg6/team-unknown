from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    event_type = db.Column(db.String(64))
    details = db.Column(db.String(256))

    def __repr__(self):
        return f'<Event {self.event_type} at {self.timestamp}>'
