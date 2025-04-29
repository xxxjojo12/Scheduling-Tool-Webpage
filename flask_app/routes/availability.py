# /exam/flask_app/routes/availability.py

from flask import Blueprint, request, session, jsonify
from flask_app.database import database

avail_bp = Blueprint('availability', __name__)
db = database()

@avail_bp.route('/api/availability/update', methods=['POST'])
def update_availability():
    if 'user' not in session:
        return jsonify({ 'success': False, 'message': 'Unauthorized' }), 401

    data = request.get_json()
    event_id = data.get('event_id')
    day = data.get('day')
    time_slot = data.get('time')
    status = data.get('status')

    email = session['user']
    user = db.query("SELECT user_id FROM users WHERE email = %s", (email,))
    if not user:
        return jsonify({ 'success': False, 'message': 'User not found' }), 404

    user_id = user[0]['user_id']

    db.query("""
        INSERT INTO availability (user_id, event_id, day, time_slot, status)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE status = VALUES(status)
    """, (user_id, event_id, day, time_slot, status))

    return jsonify({ 'success': True })


@avail_bp.route('/api/availability/self/<int:event_id>', methods=['GET'])
def get_user_availability(event_id):
    if 'user' not in session:
        return jsonify({ 'success': False, 'message': 'Unauthorized' }), 401

    email = session['user']
    user = db.query("SELECT user_id FROM users WHERE email = %s", (email,))
    if not user:
        return jsonify({ 'success': False, 'message': 'User not found' }), 404

    user_id = user[0]['user_id']

    rows = db.query("""
        SELECT day, time_slot, status
        FROM availability
        WHERE user_id = %s AND event_id = %s
    """, (user_id, event_id))

    return jsonify({ 'success': True, 'data': rows })


@avail_bp.route('/api/availability/all/<int:event_id>', methods=['GET'])
def get_all_availability(event_id):
    rows = db.query("""
        SELECT day, time_slot, status, COUNT(*) AS count
        FROM availability
        WHERE event_id = %s
        GROUP BY day, time_slot, status
    """, (event_id,))

    heatmap = {}
    for row in rows:
        key = f"{row['day']}_{row['time_slot']}"
        if key not in heatmap:
            heatmap[key] = { 'available': 0, 'maybe': 0, 'unavailable': 0 }
        heatmap[key][row['status'].lower()] = int(row['count'])

    return jsonify({ 'success': True, 'data': heatmap })
    
 
@avail_bp.route('/api/best_time/<int:event_id>', methods=['GET'])
def get_best_time(event_id):
    rows = db.query("""
        SELECT day, time_slot, status
        FROM availability
        WHERE event_id = %s
    """, (event_id,))

    if not rows:
        return jsonify({ 'success': False, 'message': 'No availability submitted yet' })

    score = {}
    for row in rows:
        key = (row['day'], row['time_slot'])
        if key not in score:
            score[key] = { 'available': 0, 'unavailable': 0 }
        if row['status'].lower() == 'available':
            score[key]['available'] += 1
        elif row['status'].lower() == 'unavailable':
            score[key]['unavailable'] += 1

    best = sorted(score.items(), key=lambda kv: (-kv[1]['available'], kv[1]['unavailable'], kv[0]))
    best_day, best_time = best[0][0]

    return jsonify({ 'success': True, 'day': best_day, 'time': best_time }) 