from flask import Flask

def create_app():
    app = Flask(__name__)
    app.secret_key = "change-this-secret-key"

    from .auth import auth_bp
    from .routes import main_bp
    from .live_ingest import start_ingestion
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    start_ingestion()
    return app