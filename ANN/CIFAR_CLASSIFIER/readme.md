# CIFAR-10 AI Image Classifier

A production-grade, secure, modern web application for classifying images using a deep neural network trained on the CIFAR-10 dataset with Keras and TensorFlow, served via Flask.

---

## 1. Project Overview

The CIFAR-10 AI Image Classifier provides an end-to-end interface for evaluating images against 10 distinct object and animal categories. Built with an application factory design pattern, in-memory stream processing, and responsive glassmorphic UI, it delivers sub-second inference with confidence scoring and probability distributions.

### Key Highlights
- **Framework**: Flask (Application Factory architecture, Blueprint routing)
- **Deep Learning Engine**: Keras / TensorFlow (`classifier.h5`)
- **Frontend**: Clean Vanilla JavaScript, Semantic HTML5, Modern CSS3 with Design Tokens
- **Reliability & Security**: Strict file upload validation (format, dimensions, max 5 MB), Pillow image integrity verification, and no arbitrary disk writes during inference.

---

## 2. Model Architecture & Specifications

The neural network was developed and trained in `CIFAR_10_CLASSIFICATION.ipynb` using Keras:

- **Dataset**: CIFAR-10 (60,000 32x32 color images across 10 classes)
- **Input Dimensions**: `(32, 32, 3)`
- **Network Layers**:
  - `Input(shape=(32, 32, 3))`
  - `Flatten()`: Unrolls 32 × 32 × 3 into 3,072 input features
  - `Dense(100, activation="relu")`: Hidden layer with 307,300 trainable parameters
  - `Dense(10, activation="softmax")`: Output probability distribution across 10 classes
- **Optimizer**: RMSprop
- **Loss Function**: Sparse Categorical Crossentropy
- **Total Parameters**: 308,312 (1.18 MB)

### Centralized Class Mapping

The application maps output logits to the standard CIFAR-10 taxonomy:

| Index | Label | Emoji |
| :---: | :---: | :---: |
| `0` | **airplane** | ✈️ |
| `1` | **automobile** | 🚗 |
| `2` | **bird** | 🐦 |
| `3` | **cat** | 🐱 |
| `4` | **deer** | 🦌 |
| `5` | **dog** | 🐕 |
| `6` | **frog** | 🐸 |
| `7` | **horse** | 🐎 |
| `8` | **ship** | 🚢 |
| `9` | **truck** | 🚚 |

---

## 3. Project Structure

```text
cifar10-classifier/
├── app/
│   ├── __init__.py           # Flask application factory, logging & error handlers
│   ├── config.py             # Centralized configuration (paths, limits, classes)
│   ├── model.py              # Singleton thread-safe model loader & manager
│   ├── predictor.py          # Preprocessing & inference pipeline
│   ├── routes.py             # HTTP routes (GET /, POST /predict, GET /health)
│   ├── templates/
│   │   └── index.html        # Semantic, accessible HTML5 user interface
│   └── static/
│       ├── css/
│       │   └── style.css     # Dark-theme stylesheet, animations & responsive grid
│       ├── js/
│       │   └── app.js        # Drag-and-drop, client validation & async AJAX controller
│       └── images/           # Static asset images
├── models/
│   └── classifier.h5         # Trained Keras HDF5 model weights & architecture
├── uploads/
│   └── .gitkeep              # Temporary upload storage marker
├── tests/
│   ├── __init__.py
│   └── test_predictor.py     # Automated pytest suite for routes & predictions
├── run.py                    # Local development server entry point
├── wsgi.py                   # Production WSGI server entry point
├── requirements.txt          # Python package dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
└── README.md                 # Complete documentation
```

---

## 4. Image Preprocessing & Prediction Pipeline

To ensure model accuracy and numerical fidelity, uploaded images pass through the exact preprocessing pipeline used during model training:

```text
Uploaded Image (File Stream)
           │
           ▼
1. Validate format (.png, .jpg, .jpeg, .webp) & size (≤ 5 MB)
           │
           ▼
2. Pillow open & verify integrity
           │
           ▼
3. Convert to RGB (.convert("RGB"))
           │
           ▼
4. Resize to target dimension (32 × 32 px)
           │
           ▼
5. Convert to NumPy float32 array
           │
           ▼
6. Normalize pixel values: image = image / 255.0
           │
           ▼
7. Expand batch dimension: (1, 32, 32, 3)
           │
           ▼
8. Model inference: model.predict(image, verbose=0)
           │
           ▼
9. Compute argmax predicted class, confidence %, and Top-3 ranked classes
```

---

## 5. Installation & Local Setup

### Prerequisites
- Python **3.10** or higher
- Git

### 1. Clone or Open Project
```powershell
cd "e:\Niranjan_AI\Deep Learning\ANN\CIFAR_CLASSIFIER"
```

### 2. Create Virtual Environment
```powershell
python -m venv venv
```

### 3. Activate Virtual Environment
- **Windows (Command Prompt / PowerShell)**:
  ```powershell
  venv\Scripts\activate
  ```
- **Linux / macOS**:
  ```bash
  source venv/bin/activate
  ```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 5. Verify Model Placement
Ensure `classifier.h5` is present in the `models/` folder:
```text
models/classifier.h5
```

---

## 6. Running the Application

### Development Server
Start the local server using `run.py`:
```powershell
python run.py
```
Open your web browser and navigate to:
```text
http://127.0.0.1:5000
```

### Production Deployment (WSGI)

#### On Windows (using Waitress)
```powershell
waitress-serve --port=5000 wsgi:app
```

#### On Linux / macOS (using Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

---

## 7. API Endpoints

### `GET /`
Renders the interactive web application interface.

### `GET /health`
Returns system and model health status.
```json
{
  "classes_count": 10,
  "model_loaded": true,
  "status": "healthy"
}
```

### `POST /predict`
Accepts an image file via `multipart/form-data` (`image` or `file` field).

**Sample Success Response (`200 OK`)**:
```json
{
  "prediction": {
    "confidence": 0.8741,
    "confidence_percent": "87.4%",
    "emoji": "✈️",
    "predicted_class": "airplane",
    "top_predictions": [
      {
        "class": "airplane",
        "confidence": 0.8741,
        "confidence_percent": "87.4%",
        "emoji": "✈️"
      },
      {
        "class": "ship",
        "confidence": 0.0621,
        "confidence_percent": "6.2%",
        "emoji": "🚢"
      },
      {
        "class": "automobile",
        "confidence": 0.0312,
        "confidence_percent": "3.1%",
        "emoji": "🚗"
      }
    ]
  },
  "success": true
}
```

**Sample Error Response (`400 Bad Request`)**:
```json
{
  "error": "Unsupported file format. Please upload PNG, JPG, JPEG, or WEBP.",
  "success": false
}
```

---

## 8. Running Automated Tests

Run the test suite using `pytest`:
```powershell
pytest -v tests/
```
The test suite validates:
- Root page loading (HTTP 200)
- Health check diagnostic endpoint (HTTP 200)
- Missing payload handling (HTTP 400)
- Unsupported file extension rejection (HTTP 400)
- Corrupted image error handling (HTTP 400)
- End-to-end prediction pipeline and output schema compliance

---

## 9. Security & Error Handling

- **Upload Limits**: Hard limit of 5 MB enforced via Flask's `MAX_CONTENT_LENGTH`.
- **Extension Whitelist**: Only `.png`, `.jpg`, `.jpeg`, and `.webp` are permitted.
- **In-Memory Streaming**: Images are parsed in memory using Pillow without executing or saving arbitrary user files to disk.
- **Sanitized Errors**: No internal tracebacks or system paths are exposed to the client. User-friendly toast messages guide users.

---

## 10. License & Credits

- Built with **TensorFlow / Keras**, **Flask**, and **CIFAR-10**.
- Designed for production machine learning deployment and portfolio presentation.