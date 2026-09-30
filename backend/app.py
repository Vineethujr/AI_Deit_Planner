"""
AI-Powered Personal Diet Planner with Cloud Storage — Backend Entry Point
===========================================================================
Run locally:
    python backend/app.py

Educational / demo project. Diet plans are general wellness examples, not
medical or clinical nutrition advice. All data used is synthetic/demo data.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify
from flask_cors import CORS

from backend.config import Config
from backend.routes.auth_routes import auth_bp
from backend.routes.profile_routes import profile_bp
from backend.routes.plan_routes import plan_bp
from backend.routes.file_routes import file_bp
from cloud.database_service import init_db


def create_app(test_config: dict = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    init_db()

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(profile_bp, url_prefix="/api")
    app.register_blueprint(plan_bp, url_prefix="/api")
    app.register_blueprint(file_bp, url_prefix="/api")

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "diet-planner-backend"}), 200

    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"error": "Resource not found."}), 404

    @app.errorhandler(500)
    def server_error(_e):
        return jsonify({"error": "Internal server error."}), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=app.config["PORT"], debug=(app.config["FLASK_ENV"] == "development"))
