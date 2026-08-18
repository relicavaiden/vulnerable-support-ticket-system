import os

from flask import Flask
from flask_cors import CORS

from app.routes.health import health_bp
from app.routes.auth import auth_bp
from app.routes.tickets import tickets_bp

def create_app(test_config=None):
    app = Flask(__name__)

    app.config["DATABASE"] = os.path.join(
        app.instance_path,
        "vulnerable_ticket_system.db"
    )

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

    if test_config is not None:
        app.config.update(test_config)

    if not app.config["SECRET_KEY"]:
        raise RuntimeError("SECRET_KEY must be configured")

    CORS(
        app,
        origins=["http://localhost:3000"],
        supports_credentials=True,
    )

    os.makedirs(app.instance_path, exist_ok=True)

    from . import db
    db.init_app(app)

    from . import seed
    seed.init_app(app)

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(tickets_bp)

    return app