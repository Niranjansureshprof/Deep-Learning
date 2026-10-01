import logging
import os
import threading
from typing import Optional
from keras.models import load_model

logger = logging.getLogger(__name__)

_model: Optional[object] = None
_model_lock = threading.Lock()


def load_classifier_model(model_path: str):
    """
    Loads the trained Keras H5 model from the specified file path.
    Ensures the model is loaded once and cached in memory.
    """
    global _model
    with _model_lock:
        if _model is not None:
            return _model

        if not os.path.exists(model_path):
            error_msg = f"Model file not found at: {model_path}. Please place classifier.h5 in models/."
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        try:
            logger.info("Loading CIFAR-10 model from %s...", model_path)
            # Load model without compiling metrics since we only perform inference
            _model = load_model(model_path, compile=False)
            logger.info("CIFAR-10 model loaded successfully. Input shape: %s, Output shape: %s",
                        getattr(_model, "input_shape", None),
                        getattr(_model, "output_shape", None))
            return _model
        except Exception as e:
            logger.exception("Failed to load model from %s: %s", model_path, str(e))
            raise RuntimeError(f"Error loading trained model: {str(e)}") from e


def get_model(model_path: Optional[str] = None):
    """
    Returns the cached Keras model instance.
    If not yet loaded, attempts to load it using model_path.
    """
    global _model
    if _model is not None:
        return _model

    if model_path is None:
        from app.config import Config
        model_path = Config.MODEL_PATH

    return load_classifier_model(model_path)
