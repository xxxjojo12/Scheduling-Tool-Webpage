# /exam/flask_app/routes/socketio_handlers.py

from flask_socketio import emit, join_room, SocketIO
from flask import request, session
from flask_app.database import database

# Socket server and user map global declaration
socketio = SocketIO(cors_allowed_origins="*")
user_sid_map = {}
db = database()

def register_socketio_handlers(app_socketio):
    @app_socketio.on('connect')
    def handle_connect():
        email = session.get("user")
        if not email:
            print("No user in session during socket connect")
            return

        rows = db.query("SELECT user_id FROM users WHERE email = %s", (email,))
        if rows:
            user_id = rows[0]['user_id']
            user_sid_map[user_id] = request.sid
            print(f"Socket connected: user_id {user_id}, SID {request.sid}")
            join_room(f"event_{user_id}")
        else:
            print(f"Could not resolve user_id for {email}")

    @app_socketio.on('disconnect')
    def handle_disconnect():
        for uid, sid in list(user_sid_map.items()):
            if sid == request.sid:
                del user_sid_map[uid]
                print(f"Socket disconnected for user_id {uid}")
                break

    @app_socketio.on('join_event')
    def handle_join_event(event_id):
        room = f"event_{event_id}"
        join_room(room)
        print(f"User joined room {room}")        

    @app_socketio.on('availability_update')
    def handle_availability_update(data):
        event_id = data.get('event_id')
        room = f"event_{event_id}"
        socketio.emit('availability_update', data, room=room, include_self=False)
        socketio.emit('best_time_update', room=room)
        print(f"Broadcasted availability update to room {room} with data {data}")
        print(f"Triggered best time update broadcast to room {room}")
