from flask import Flask
from app.config import load_configurations, configure_logging
from .views import webhook_blueprint


def create_app():
    app = Flask(__name__)

    # Load configurations and logging settings
    print("yes------------")
    load_configurations(app)
    configure_logging()
    print("yowww------------")
    # Import and register blueprints, if any
    app.register_blueprint(webhook_blueprint)

    return app
