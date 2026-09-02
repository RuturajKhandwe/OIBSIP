import logging
import os
from flask import Flask, render_template, redirect, url_for
from flask_socketio import SocketIO
from config import config
from database.db import close_db, init_db
from auth.routes import auth_bp
from chat.events import register_socket_events
from utils.security import is_authenticated, get_current_username

socketio = SocketIO()

def create_app(config_name='default'):
    """Application factory for Flask & Socket.IO server."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Configure structured logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    app.logger.info("Initializing Real-Time Chat Application backend...")

    # Database teardown registration
    app.teardown_appcontext(close_db)

    # Initialize SQLite database schema & default General room
    with app.app_context():
        init_db(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Main Chat View Route
    @app.route('/')
    @app.route('/chat')
    def chat_view():
        if not is_authenticated():
            return redirect(url_for('auth.login'))
        return render_template('chat.html', username=get_current_username())

    # Healthcheck Route
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'service': 'real-time-chat'}, 200

    # Initialize SocketIO with Flask app
    # Use threading mode for broad cross-platform support without native C compile issues
    socketio.init_app(
        app,
        cors_allowed_origins="*",
        async_mode="threading",
        manage_session=True
    )

    # Register SocketIO events
    register_socket_events(socketio)

    return app

app = create_app(os.getenv('FLASK_CONFIG', 'default'))

if __name__ == '__main__':
    host = app.config['HOST']
    port = app.config['PORT']
    debug = app.config['DEBUG']
    app.logger.info(f"Starting server on http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug)
