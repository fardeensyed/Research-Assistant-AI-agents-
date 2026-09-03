from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
from app.config import Config


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


def create_app():
    """Flask application factory."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    limiter.init_app(app)
    
    # Initialize Redis connection
    try:
        app.redis_client = redis.from_url(Config.REDIS_URL)
        app.redis_client.ping()
    except Exception as e:
        print(f"Warning: Redis connection failed: {e}")
        app.redis_client = None
    
    # Register blueprints
    from app.routes import api_bp
    app.register_blueprint(api_bp)
    
    return app
