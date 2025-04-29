# /exam/flask_app/routes/events.py

from flask import Blueprint, request, render_template, redirect, session, url_for, abort
from flask_app.database import database
from flask_app.routes.socketio_handlers import socketio, user_sid_map 
from datetime import datetime, timedelta
import time


events_bp = Blueprint('events', __name__)
db = database()

@events_bp.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    email = session['user']
    user = db.query("SELECT user_id FROM users WHERE email = %s", (email,))
    if not user:
        return "User not found", 404

    user_id = user[0]['user_id']
        
    created_events = db.query("""
        SELECT * FROM events WHERE creator_id = %s
    """, (user_id,))

    invited_events = db.query("""
        SELECT e.* FROM events e
        JOIN participants p ON e.event_id = p.event_id
        JOIN users u ON u.user_id = p.user_id
        WHERE u.email = %s
    """, (email,))       

    return render_template('dashboard.html', created=created_events, invited=invited_events)

@events_bp.route('/create_event', methods=['GET', 'POST'])
def create_event():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        title = request.form['title']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        invitees = request.form['invitees'].split(',')

        creator_email = session['user']
        creator_rows = db.query("SELECT user_id FROM users WHERE email = %s", (creator_email,))
        if not creator_rows:
            return "Creator not found in database", 400

        creator_id = creator_rows[0]['user_id']

        db.query("""
            INSERT INTO events (title, start_date, end_date, start_time, end_time, creator_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (title, start_date, end_date, start_time, end_time, creator_id))

        event_id = db.query("SELECT LAST_INSERT_ID() AS id")[0]['id']

        existing = db.query("SELECT * FROM participants WHERE user_id = %s AND event_id = %s", (creator_id, event_id))
        if not existing:
            db.insertRows('participants', ['user_id', 'event_id'], [[creator_id, event_id]])

        for email in invitees:
            email = email.strip()
            if email:
                rows = db.query("SELECT user_id FROM users WHERE email = %s", (email,))
                if rows:
                    user_id = rows[0]['user_id']
                    existing = db.query("SELECT * FROM participants WHERE user_id = %s AND event_id = %s", (user_id, event_id))
                    if not existing:
                        db.insertRows('participants', ['user_id', 'event_id'], [[user_id, event_id]])

        # Send real-time notifications
        event_data = {
        "event_id": event_id,
        "title": title,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "creator_email": creator_email
        }
        time.sleep(0.2) 
        socketio.emit("event_created", event_data, include_self=True)        
        for email in invitees:
            email = email.strip()
            if not email:
                continue
            rows = db.query("SELECT user_id FROM users WHERE email = %s", (email,))
            if rows:
                invitee_id = rows[0]["user_id"]
                if invitee_id in user_sid_map:
                    sid = user_sid_map[invitee_id]
                    socketio.emit("event_created", event_data, to=sid)
                    print(f"Sent event_created to {email} (user_id={invitee_id})")
                else:
                    print(f"Not in user_sid_map: {email} (user_id={invitee_id})")


        return redirect(f"/event/{event_id}")

    return render_template('create_event.html')

@events_bp.route('/event/<int:event_id>')
def view_event(event_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    email = session['user']
    user_rows = db.query("SELECT user_id FROM users WHERE email = %s", (email,))
    if not user_rows:
        return "User not found", 404

    user_id = user_rows[0]['user_id']

    access = db.query("SELECT * FROM participants WHERE user_id = %s AND event_id = %s", (user_id, event_id))
    if not access:
        return "Access Denied", 403

    event = db.query("SELECT * FROM events WHERE event_id = %s", (event_id,))
    if not event:
        return "Event not found", 404

    event = event[0]

    # Convert timedelta object to string
    def time_str(td):
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02}:{minutes:02}"

    event['start_time_str'] = time_str(event['start_time'])
    event['end_time_str'] = time_str(event['end_time'])

    return render_template('event.html', event=event)
    
 
@events_bp.route('/join_event')
def join_event():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    email = session['user']
    invited_events = db.query("""
        SELECT e.* FROM events e
        JOIN participants p ON e.event_id = p.event_id
        JOIN users u ON u.user_id = p.user_id
        WHERE u.email = %s
    """, (email,))

    return render_template('join_event.html', events=invited_events)
    
    
@events_bp.route('/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    email = session['user']
    user = db.query("SELECT user_id FROM users WHERE email = %s", (email,))
    if not user:
        return "Unauthorized", 403

    user_id = user[0]['user_id']

    # Check permissions
    event = db.query("SELECT * FROM events WHERE event_id = %s", (event_id,))
    if not event or event[0]['creator_id'] != user_id:
        return "Forbidden", 403

    # Delete associated data first
    db.query("DELETE FROM availability WHERE event_id = %s", (event_id,))
    db.query("DELETE FROM participants WHERE event_id = %s", (event_id,))
    db.query("DELETE FROM events WHERE event_id = %s", (event_id,))
    
    room = f"event_{event_id}"
    socketio.emit('event_deleted', {'event_id': event_id})
    print(f"Sent event_deleted for {event_id} to {room}")

    return redirect(url_for('events.dashboard'))