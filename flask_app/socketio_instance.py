# /exam/flask_app/socketio_instance.py
from flask_socketio import SocketIO

# Create a socketio object that can be shared globally
socketio = SocketIO(cors_allowed_origins="*")
user_sid_map = {}
