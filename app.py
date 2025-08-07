from flask import Flask
from auth import auth_bp
from tasks import tasks_bp
from events import events_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key'

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(tasks_bp, url_prefix='/api')
app.register_blueprint(events_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)
