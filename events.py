from flask import Blueprint, request, jsonify
from auth import token_required, get_db_connection

events_bp = Blueprint('events_bp', __name__)

def error_response(message, status_code):                                                                               #ERROR RESPONSE
    return jsonify({'error': message}), status_code

@events_bp.route('/events', methods=['POST'])
@token_required
def create_event(user_id):                                                                                              #CREATE CALENDAR EVENT
    data = request.get_json()

    if not data:
        return error_response("Missing request body", 400)

    title = data.get('title')
    description = data.get('description', '')
    event_date = data.get('event_date')
    location = data.get('location', '')
    shared_with = data.get('shared_with', '')

    if not title:
        return error_response("Event title is required", 400)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO events (user_id, title, description, event_date, location, shared_with)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, title, description, event_date, location, shared_with))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Event created successfully'}), 201

@events_bp.route('/events', methods=['GET'])
@token_required
def get_events(user_id):                                                                                                #GET EVENTS
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM events WHERE user_id = ?', (user_id,))
    rows = cur.fetchall()
    conn.close()

    events = [dict(r) for r in rows]
    return jsonify(events), 200

@events_bp.route('/events/<int:event_id>', methods=['GET'])
@token_required
def get_event(user_id, event_id):                                                                                       #LIST SINGLE EVENT
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM events WHERE id = ? AND user_id = ?', (event_id, user_id))
    row = cur.fetchone()
    conn.close()

    if not row:
        return error_response("Event not found or not authorized", 404)

    return jsonify(dict(row)), 200

@events_bp.route('/events/<int:event_id>', methods=['DELETE'])
@token_required
def delete_event(user_id, event_id):                                                                                    #DELETE EVENT
    conn = get_db_connection()
    cur = conn.cursor()

    # verify ownership
    cur.execute('SELECT 1 FROM events WHERE id = ? AND user_id = ?', (event_id, user_id))
    if not cur.fetchone():
        conn.close()
        return error_response("Event not found or not authorized to delete", 404)

    cur.execute('DELETE FROM events WHERE id = ? AND user_id = ?', (event_id, user_id))
    conn.commit()
    conn.close()
    return jsonify({'message': f'Event {event_id} deleted successfully'}), 200
