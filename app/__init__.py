from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
import logging
from app.config import Config

logger = logging.getLogger(__name__)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


def create_app():
    """Flask application factory."""
    if not Config.GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is required. Set it in the runtime environment before starting the app."
        )

    app = Flask(__name__)
    app.config.from_object(Config)
    
    limiter.init_app(app)
    
    # Redis is optional; rediss:// URLs are parsed by redis-py with TLS enabled.
    app.redis_client = None
    if not Config.REDIS_URL:
        logger.warning("REDIS_URL is not set; Redis caching is disabled")
    else:
        try:
            redis_kwargs = {}
            if Config.REDIS_URL.lower().startswith("rediss://"):
                redis_kwargs["ssl"] = True
            app.redis_client = redis.from_url(Config.REDIS_URL, **redis_kwargs)
            app.redis_client.ping()
        except Exception as e:
            logger.warning("Redis connection failed; caching is disabled: %s", e)
            app.redis_client = None
    
    # Register blueprints
    from app.routes import api_bp
    app.register_blueprint(api_bp)
    
    return app
