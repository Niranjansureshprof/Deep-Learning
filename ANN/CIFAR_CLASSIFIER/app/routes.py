import io
import logging
from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError

from app.config import Config
from app.predictor import predict_image

logger = logging.getLogger(__name__)

bp = Blueprint("main", __name__)


def allowed_file(filename: str) -> bool:
    """Check if the uploaded file has a permitted extension."""
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in Config.ALLOWED_EXTENSIONS


@bp.route("/", methods=["GET"])
def index():
    """Renders the main application page."""
    return render_template(
        "index.html",
        class_names=Config.CLASS_NAMES,
        class_emojis=Config.CLASS_EMOJIS
    )


@bp.route("/predict", methods=["POST"])
def predict():
    """
    Handles image upload and classification.
    Validates file format, opens via Pillow safely in memory,
    and returns predictions.
    """
    logger.info("Received prediction request from %s", request.remote_addr)

    # 1. Check if a file part is present
    file_key = None
    if "image" in request.files:
        file_key = "image"
    elif "file" in request.files:
        file_key = "file"

    if not file_key:
        logger.warning("Prediction rejected: No image field in request")
        return jsonify({
            "success": False,
            "error": "Please upload an image first."
        }), 400

    file = request.files[file_key]

    # 2. Check for empty filename
    if not file or file.filename.strip() == "":
        logger.warning("Prediction rejected: Empty filename provided")
        return jsonify({
            "success": False,
            "error": "Please select a valid image file to upload."
        }), 400

    # 3. Secure and validate extension
    filename = secure_filename(file.filename)
    if not allowed_file(filename):
        logger.warning("Prediction rejected: Unsupported extension for %s", filename)
        return jsonify({
            "success": False,
            "error": "Unsupported file format. Please upload PNG, JPG, JPEG, or WEBP."
        }), 400

    # 4. Read file content safely in memory and validate image content
    try:
        file_bytes = file.read()
        if len(file_bytes) == 0:
            return jsonify({
                "success": False,
                "error": "The uploaded file is empty. Please upload a valid image."
            }), 400

        # Attempt to open image with Pillow
        image_stream = io.BytesIO(file_bytes)
        pil_image = Image.open(image_stream)

        # Verify image integrity (catches corrupted image files)
        pil_image.verify()

        # Re-open image because verify() modifies file pointer state
        pil_image = Image.open(io.BytesIO(file_bytes))

    except UnidentifiedImageError:
        logger.warning("Prediction rejected: Unidentified or corrupted image")
        return jsonify({
            "success": False,
            "error": "The image could not be processed. Please try another image."
        }), 400
    except Exception as e:
        logger.warning("Prediction rejected: Image parsing error: %s", str(e))
        return jsonify({
            "success": False,
            "error": "The uploaded image is corrupted or invalid. Please try another image."
        }), 400

    # 5. Run prediction through the pipeline
    try:
        result = predict_image(pil_image)
        return jsonify({
            "success": True,
            "prediction": result
        }), 200

    except Exception as e:
        logger.exception("Inference failed during predict_image: %s", str(e))
        return jsonify({
            "success": False,
            "error": "Something went wrong while analyzing the image. Please try again."
        }), 500


@bp.route("/health", methods=["GET"])
def health():
    """Health check endpoint for deployment monitoring."""
    from app.model import get_model
    try:
        model = get_model()
        model_ready = model is not None
    except Exception:
        model_ready = False

    return jsonify({
        "status": "healthy" if model_ready else "degraded",
        "model_loaded": model_ready,
        "classes_count": len(Config.CLASS_NAMES)
    }), 200 if model_ready else 503
