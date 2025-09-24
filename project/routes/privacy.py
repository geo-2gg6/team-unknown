
from flask import Blueprint, render_template, jsonify
from models import Event

privacy_bp = Blueprint('privacy', __name__)

@privacy_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')

# API endpoint for alert history
@privacy_bp.route('/api/alerts')
def api_alerts():
    events = Event.query.order_by(Event.timestamp.desc()).limit(50).all()
    return jsonify([
        {
            'id': e.id,
            'timestamp': e.timestamp.isoformat(),
            'event_type': e.event_type,
            'details': e.details
        } for e in events
    ])
