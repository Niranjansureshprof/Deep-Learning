import logging
from typing import Dict, Any, Union
import numpy as np
from PIL import Image

from app.config import Config
from app.model import get_model

logger = logging.getLogger(__name__)


def preprocess_image(image: Image.Image) -> np.ndarray:
    """
    Preprocess PIL Image strictly matching the CIFAR-10 training notebook:
    1. Convert to RGB
    2. Resize to (32, 32)
    3. Convert to NumPy float array
    4. Normalize pixel values by dividing by 255.0
    5. Expand dimensions to shape (1, 32, 32, 3)
    """
    if not isinstance(image, Image.Image):
        raise TypeError(f"Expected PIL Image, got {type(image)}")

    # 1. Convert to RGB (handles RGBA, Grayscale, etc.)
    rgb_image = image.convert("RGB")

    # 2. Resize to 32x32 exactly as in CIFAR-10
    resized_image = rgb_image.resize((32, 32), Image.Resampling.BILINEAR)

    # 3. Convert to float32 NumPy array
    img_array = np.array(resized_image, dtype=np.float32)

    # 4. Normalize to [0.0, 1.0]
    normalized_image = img_array / 255.0

    # 5. Add batch dimension -> (1, 32, 32, 3)
    batched_image = np.expand_dims(normalized_image, axis=0)

    return batched_image


def predict_image(image: Image.Image) -> Dict[str, Any]:
    """
    Runs model inference on the provided PIL Image.

    Returns:
        dict: {
            "predicted_class": str,
            "confidence": float,
            "emoji": str,
            "confidence_percent": str,
            "top_predictions": [
                {
                    "class": str,
                    "confidence": float,
                    "confidence_percent": str,
                    "emoji": str
                },
                ...
            ]
        }
    """
    # 1. Preprocess
    preprocessed = preprocess_image(image)

    # 2. Retrieve model (singleton)
    model = get_model()

    # 3. Predict without console clutter (verbose=0)
    predictions = model.predict(preprocessed, verbose=0)
    probabilities = predictions[0]

    # 4. Top prediction
    predicted_index = int(np.argmax(probabilities))
    confidence = float(probabilities[predicted_index])
    predicted_class = Config.CLASS_NAMES[predicted_index]

    # 5. Top 3 predictions sorted by probability descending
    top_indices = np.argsort(probabilities)[::-1][:3]
    top_predictions = []
    for idx in top_indices:
        c_name = Config.CLASS_NAMES[int(idx)]
        conf_val = float(probabilities[idx])
        top_predictions.append({
            "class": c_name,
            "confidence": round(conf_val, 4),
            "confidence_percent": f"{conf_val * 100:.1f}%",
            "emoji": Config.CLASS_EMOJIS.get(c_name, "🔍")
        })

    logger.info("Prediction successful: %s (confidence: %.2f%%)",
                predicted_class, confidence * 100)

    return {
        "predicted_class": predicted_class,
        "confidence": round(confidence, 4),
        "confidence_percent": f"{confidence * 100:.1f}%",
        "emoji": Config.CLASS_EMOJIS.get(predicted_class, "🔍"),
        "top_predictions": top_predictions
    }
