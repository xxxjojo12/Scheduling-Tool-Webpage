# /exam/app.py

from flask_app import create_app
from flask_app.socketio_instance import socketio  
from flask_app.routes.socketio_handlers import register_socketio_handlers
from flask_app.routes.socketio_handlers import socketio, user_sid_map
from flask_app.database import database
import os

app = create_app()
socketio.init_app(app) 
register_socketio_handlers(socketio)

db = database()
if os.environ.get("FLASK_ENV") == "development":
    db.createTables()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    socketio.run(app, host="0.0.0.0", port=port)
  