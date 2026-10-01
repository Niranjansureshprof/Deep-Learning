import io
import pytest
from PIL import Image
from app import create_app
from app.config import TestingConfig


@pytest.fixture
def app():
    """Create application configured for testing."""
    test_app = create_app(TestingConfig)
    return test_app


@pytest.fixture
def client(app):
    """Test client fixture."""
    return app.test_client()


def create_test_image_bytes(format="PNG", size=(64, 64), color="blue"):
    """Helper to generate in-memory dummy image bytes."""
    img = Image.new("RGB", size, color=color)
    byte_arr = io.BytesIO()
    img.save(byte_arr, format=format)
    byte_arr.seek(0)
    return byte_arr


def test_index_page_success(client):
    """Test that the home page loads successfully (HTTP 200)."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"See What Your Image Is" in response.data
    assert b"AI IMAGE CLASSIFIER" in response.data


def test_health_endpoint(client):
    """Test that the health endpoint returns 200 and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["classes_count"] == 10


def test_missing_image_payload(client):
    """Test that submitting without an image returns HTTP 400."""
    response = client.post("/predict", data={}, content_type="multipart/form-data")
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "Please upload an image first" in data["error"]


def test_unsupported_file_extension(client):
    """Test that uploading a file with an unsupported extension returns HTTP 400."""
    data = {
        "image": (io.BytesIO(b"fake text content"), "test_file.txt")
    }
    response = client.post("/predict", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["success"] is False
    assert "Unsupported file format" in json_data["error"]


def test_corrupted_image_file(client):
    """Test that uploading a corrupted image file returns HTTP 400."""
    data = {
        "image": (io.BytesIO(b"\x89PNG\r\n\x1a\ncorrupted_data_not_an_image"), "corrupted.png")
    }
    response = client.post("/predict", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["success"] is False


def test_valid_image_prediction(client):
    """Test that a valid image reaches the prediction pipeline and returns valid schema."""
    image_bytes = create_test_image_bytes(format="PNG", size=(32, 32), color="red")
    data = {
        "image": (image_bytes, "sample_airplane.png")
    }
    response = client.post("/predict", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    json_data = response.get_json()

    assert json_data["success"] is True
    prediction = json_data["prediction"]

    # Verify required keys in prediction payload
    assert "predicted_class" in prediction
    assert "confidence" in prediction
    assert "top_predictions" in prediction
    assert isinstance(prediction["confidence"], float)
    assert 0.0 <= prediction["confidence"] <= 1.0

    # Verify top 3 predictions
    top_preds = prediction["top_predictions"]
    assert isinstance(top_preds, list)
    assert len(top_preds) == 3

    for item in top_preds:
        assert "class" in item
        assert "confidence" in item
        assert isinstance(item["confidence"], float)
        assert 0.0 <= item["confidence"] <= 1.0

    # Ensure the top predicted class matches rank #1
    assert top_preds[0]["class"] == prediction["predicted_class"]
