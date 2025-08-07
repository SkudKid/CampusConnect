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
