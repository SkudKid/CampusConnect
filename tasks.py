from flask import Blueprint, request, jsonify
from auth import token_required, get_db_connection

tasks_bp = Blueprint('tasks_bp', __name__)

@tasks_bp.route('/tasks', methods=['POST'])
@token_required

def create_task(user_id):                                                                                               #CREATE TASKS
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    due_date = data.get('due_date')
    priority = data.get('priority', 0)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tasks (user_id, title, description, due_date, priority)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, title, description, due_date, priority))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Task created successfully'}), 201

@tasks_bp.route('/tasks', methods=['GET'])
@token_required
def get_tasks(user_id):                                                                                                 #GET TASKS
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks WHERE user_id = ?', (user_id,))
    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(tasks), 200

