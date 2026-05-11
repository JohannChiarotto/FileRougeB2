from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db      = SQLAlchemy()
migrate = Migrate()
jwt     = JWTManager()


def create_app(env: str = "default") -> Flask:
    app = Flask(__name__, static_folder=None)

    # ── Config ──────────────────────────────────────────────────
    from app.config import config
    app.config.from_object(config[env])

    # ── Extensions ──────────────────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ── Import des modèles (nécessaire pour Flask-Migrate) ──────
    from app.models import utilisateur, vehicule, agence, message, rendez_vous, estimation  # noqa

    # ── Blueprints ──────────────────────────────────────────────
    from app.routes.vehicules  import bp as bp_vehicules
    from app.routes.auth       import bp as bp_auth
    from app.routes.messages   import bp as bp_messages
    from app.routes.agences    import bp as bp_agences
    from app.routes.rdv        import bp as bp_rdv

    app.register_blueprint(bp_vehicules, url_prefix="/api/vehicules")
    app.register_blueprint(bp_auth,      url_prefix="/api/auth")
    app.register_blueprint(bp_messages,  url_prefix="/api/messages")
    app.register_blueprint(bp_agences,   url_prefix="/api/agences")
    app.register_blueprint(bp_rdv,       url_prefix="/api/rdv")

    # ── Health check ────────────────────────────────────────────
    @app.route("/api/health")
    def health():
        return {"status": "ok", "service": "darri-bolide-api"}

    return app
