import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Application configuration settings."""

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "cifar10-deep-learning-secret-key-2026")

    # Model Configuration
    MODEL_PATH = os.getenv(
        "MODEL_PATH",
        str(BASE_DIR / "models" / "classifier.h5")
    )

    # Upload Configuration
    UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER",
        str(BASE_DIR / "uploads")
    )
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 5 * 1024 * 1024))  # 5 MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

    # Debug flag
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")

    # CIFAR-10 Class Names and Visual Metadata
    CLASS_NAMES = [
        "airplane",
        "automobile",
        "bird",
        "cat",
        "deer",
        "dog",
        "frog",
        "horse",
        "ship",
        "truck"
    ]

    CLASS_EMOJIS = {
        "airplane": "✈️",
        "automobile": "🚗",
        "bird": "🐦",
        "cat": "🐱",
        "deer": "🦌",
        "dog": "🐕",
        "frog": "🐸",
        "horse": "🐎",
        "ship": "🚢",
        "truck": "🚚"
    }


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = False
