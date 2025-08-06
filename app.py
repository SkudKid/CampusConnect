from flask import Flask
from auth import auth_bp
from tasks import tasks_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key'

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(tasks_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)
