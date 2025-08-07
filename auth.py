from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
import sqlite3 as sql
import jwt
import datetime
from functools import wraps
from flask import Blueprint, request, jsonify

def error_response(message, status_code):                                                                               #ERROR RESPONSE
    return jsonify({'error': message}), status_code

auth_bp = Blueprint('auth_bp', __name__)
bcrypt = Bcrypt()

SECRET_KEY = 'my_secret_key'
DATABASE = 'campusconnect.db'

def get_db_connection():                                                                                                #CONNECT TO DATABASE
    conn = sql.connect(DATABASE)
    conn.row_factory = sql.Row
    return conn

def token_required(f):                                                                                                  #REQUIRE VALID TOKEN FOR ANYTHING IN APPLICATION. IS A MUST
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

@auth_bp.route('/register', methods=['POST'])                                                                      #REGISTER USER
def register():
    data = request.get_json()

    if not data:
        return error_response("Missing request body", 400)

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username:
        return error_response("Username is required", 400)
    if not email:
        return error_response("Email is required", 400)
    if not password:
        return error_response("Password is required", 400)

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
        return error_response("Username or email already exists!", 409)


@auth_bp.route('/login', methods=['POST'])
def login():                                                                                                            #LOGIN USER
    data = request.get_json()

    if not data:
        return error_response("Missing request body", 400)

    email = data.get('email')
    password = data.get('password')

    if not email:
        return error_response("Email is required", 400)
    if not password:
        return error_response("Password is required", 400)

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
        return error_response("Invalid email or password", 401)

