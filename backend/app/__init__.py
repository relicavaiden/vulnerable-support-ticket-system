import os

from flask import Flask

from app.routes.health import health_bp
from app.routes.auth import auth_bp

def create_app():
    app = Flask(__name__)
    app.config["DATABASE"] = os.path.join(app.instance_path, "vulnerable_ticket_system.db")

    os.makedirs(app.instance_path, exist_ok=True)

    from . import db
    db.init_app(app)
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)

    from . import seed
    seed.init_app(app)

    return app