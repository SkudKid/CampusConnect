from flask import Blueprint, request, jsonify
from auth import token_required, get_db_connection

def error_response(message, status_code): return jsonify({'error': message}), status_code                               #ERROR RESPONDER

tasks_bp = Blueprint('tasks_bp', __name__)

@tasks_bp.route('/tasks', methods=['POST'])
@token_required
def create_task(user_id):                                                                                               #CREATE TASKS
    data = request.get_json()

    if not data:
        return error_response("Missing request body", 400)

    title = data.get('title')
    description = data.get('description', '')
    due_date = data.get('due_date')
    priority = data.get('priority', 0)

    # Validate required fields
    if not title:
        return error_response("Task title is required", 400)

    if not isinstance(priority, int):
        return error_response("Priority must be an integer", 400)

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

@tasks_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@token_required
def delete_task(user_id, task_id):                                                                                     #DELETE TASKS
    conn = get_db_connection()
    cursor = conn.cursor()

    #Make sure task exists & belongs to user
    cursor.execute('SELECT * FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id,))
    task = cursor.fetchone()

    if not task:
        conn.close()
        return jsonify({'message': 'Task not found or not authorized to delete'}), 404

    #DELETE IT!
    cursor.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id))
    conn.commit()
    conn.close()

    return jsonify({'message': f'Task {task_id} deleted successfully'}), 200

@tasks_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@token_required
def update_task(user_id, task_id):                                                                                      #EDIT TASKS
    data = request.get_json()

    if not data:
        return error_response("Missing request body", 400)

    # Connect and verify task belongs to user
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id))
    task = cursor.fetchone()

    if not task:
        conn.close()
        return jsonify({'message': 'Task not found or not authorized'}), 404

    # Convert task row to a dict so we can merge updates
    task_dict = dict(task)

    # Only update fields that were included in the request
    updated_title = data.get('title', task_dict['title'])
    updated_description = data.get('description', task_dict['description'])
    updated_due_date = data.get('due_date', task_dict['due_date'])
    updated_priority = data.get('priority', task_dict['priority'])

    if 'priority' in data and not isinstance(updated_priority, int):
        return error_response("Priority must be an integer", 400)

    # Update in database
    cursor.execute('''
        UPDATE tasks
        SET title = ?, description = ?, due_date = ?, priority = ?
        WHERE id = ? AND user_id = ?
    ''', (updated_title, updated_description, updated_due_date, updated_priority, task_id, user_id))

    conn.commit()
    conn.close()

    return jsonify({'message': f'Task {task_id} updated successfully'}), 200

