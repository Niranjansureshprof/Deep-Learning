import logging
import os
import sys
from flask import Flask, jsonify

from app.config import Config
from app.model import get_model


def configure_logging(app: Flask):
    """Sets up structured production logging."""
    log_level = logging.DEBUG if app.config.get("DEBUG") else logging.INFO

    # Remove any existing handlers to prevent duplicate lines
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)

    root_logger.setLevel(log_level)
    app.logger.setLevel(log_level)


def create_app(config_class=Config) -> Flask:
    """
    Application factory for the CIFAR-10 classification service.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure logging
    configure_logging(app)
    app.logger.info("Initializing CIFAR-10 Classification Application...")

    # Register blueprints
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    # Global error handlers
    @app.errorhandler(413)
    def request_entity_too_large(error):
        app.logger.warning("Upload rejected: File size exceeded MAX_CONTENT_LENGTH")
        return jsonify({
            "success": False,
            "error": "File size exceeds the 5 MB limit. Please upload a smaller image."
        }), 413

    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify({
            "success": False,
            "error": "The requested resource was not found."
        }), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error("Internal Server Error: %s", str(error))
        return jsonify({
            "success": False,
            "error": "An internal server error occurred. Please try again later."
        }), 500

    # Ensure uploads folder exists
    upload_dir = app.config.get("UPLOAD_FOLDER")
    if upload_dir:
        os.makedirs(upload_dir, exist_ok=True)

    # Preload the model once during application startup if not in testing mode
    if not app.config.get("TESTING"):
        try:
            model_path = app.config.get("MODEL_PATH")
            app.logger.info("Pre-loading neural network model from: %s", model_path)
            get_model(model_path)
            app.logger.info("Model warm-up and initialization complete.")
        except Exception as e:
            app.logger.error("Initial model loading failed: %s", str(e))
            # Continue running so health check or diagnostics can report status

    app.logger.info("Application ready to accept requests.")
    return app
