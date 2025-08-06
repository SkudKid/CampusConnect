from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
import sqlite3 as sql
import jwt
import datetime
from functools import wraps

auth_bp = Blueprint('auth_bp', __name__)
bcrypt = Bcrypt()

SECRET_KEY = 'my_secret_key'
DATABASE = 'campusconnect.db'

def get_db_connection():
    conn = sql.connect(DATABASE)
    conn.row_factory = sql.Row
    return conn

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Signature expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(user_id, *args, **kwargs)
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, hashed_password)
        )
        conn.commit()
        conn.close()
        return jsonify({'message': 'User registered successfully!'}), 201
    except sql.IntegrityError:
        return jsonify({'message': 'Username or email already exists!'}), 409

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.check_password_hash(user['password_hash'], password):
        token = jwt.encode(
            {
                'user_id': user['id'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            },
            SECRET_KEY,
            algorithm='HS256'
        )
        return jsonify({'token': token}), 200
    else:
        return jsonify({'message': 'Invalid credentials!'}), 401
