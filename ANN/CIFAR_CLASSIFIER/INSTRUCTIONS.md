I have a trained Keras deep learning image classification model that I want to deploy as a production-quality Flask web application.

IMPORTANT:
Use the uploaded Jupyter notebook as the source of truth for the model architecture, preprocessing, input dimensions, and prediction logic.

The uploaded notebook is a CIFAR-10 image classification project, NOT MNIST.

Model details from the notebook:

Dataset:
- CIFAR-10
- Input images: 32x32 RGB
- Input shape: (32, 32, 3)
- 10 output classes

Preprocessing:
- Training images are normalized using:
  image = image / 255.0
- Uploaded prediction images must undergo the same normalization.
- Uploaded images must be converted to RGB.
- Resize uploaded images to exactly 32x32.

Model architecture:
- Sequential model
- Input(shape=(32,32,3))
- Flatten()
- Dense(100, activation="relu")
- Dense(10, activation="softmax")

Compilation:
- optimizer="rmsprop"
- loss="sparse_categorical_crossentropy"
- metrics=["accuracy"]

Training:
- batch_size=50
- epochs=10

The notebook saves the trained model using:
model.save("classifier.h5")

The notebook prediction logic is essentially:
image = image / 255.0
image = np.expand_dims(image, axis=0)
prediction = prediction_model.predict(image)
predicted_class = np.argmax(prediction)

Build a Flask web application around this trained model.

==================================================
1. PROJECT OBJECTIVE
==================================================

Build an elegant, modern, premium-looking web application where a user can:

1. Open the website.
2. Upload an image.
3. See a preview of the uploaded image.
4. Click a "Predict Image" button.
5. Send the image to the Flask backend.
6. Preprocess the image exactly as required by the trained model.
7. Run inference using classifier.h5.
8. Display:
   - Predicted CIFAR-10 class
   - Confidence percentage
   - Top 3 predictions with confidence percentages
   - Uploaded image preview
9. Allow the user to upload another image and predict again.

The application should feel like a polished AI product rather than a basic machine-learning demo.

==================================================
2. CIFAR-10 CLASS LABELS
==================================================

Use the standard CIFAR-10 class mapping:

0 = airplane
1 = automobile
2 = bird
3 = cat
4 = deer
5 = dog
6 = frog
7 = horse
8 = ship
9 = truck

Create this mapping in the backend as a constant, for example:

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

Do not hard-code class names throughout the application.
Keep the mapping centralized.

==================================================
3. TECH STACK
==================================================

Backend:
- Python
- Flask
- TensorFlow / Keras
- NumPy
- Pillow

Frontend:
- HTML5
- CSS3
- Vanilla JavaScript

Do NOT use React, Vue, Angular, or other frontend frameworks unless absolutely necessary.

Keep the application lightweight and easy to understand.

==================================================
4. PRODUCTION-GRADE PROJECT STRUCTURE
==================================================

Create the project using this structure:

cifar10-classifier/
│
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── model.py
│   ├── predictor.py
│   ├── config.py
│   │
│   ├── templates/
│   │   └── index.html
│   │
│   └── static/
│       ├── css/
│       │   └── style.css
│       │
│       ├── js/
│       │   └── app.js
│       │
│       └── images/
│
├── models/
│   └── classifier.h5
│
├── uploads/
│   └── .gitkeep
│
├── tests/
│   ├── __init__.py
│   └── test_predictor.py
│
├── run.py
├── requirements.txt
├── .gitignore
├── .env.example
├── README.md
└── wsgi.py

Keep responsibilities separated.

Do not put the entire application inside app.py.

==================================================
5. MODEL LOADING
==================================================

Create a dedicated model.py.

Load the Keras model only once when the Flask application starts.

Do NOT load classifier.h5 every time a user uploads an image.

Use something conceptually similar to:

MODEL_PATH = "models/classifier.h5"

model = load_model(MODEL_PATH)

Provide a clean function such as:

get_model()

that returns the already-loaded model.

Handle model-loading failures gracefully and provide a useful server-side error.

==================================================
6. PREDICTION SERVICE
==================================================

Create predictor.py.

Create a clean prediction function:

predict_image(image)

Responsibilities:

1. Accept a PIL image.
2. Convert it to RGB.
3. Resize to (32, 32).
4. Convert it to NumPy array.
5. Convert pixel values from 0-255 to 0-1.
6. Add batch dimension.
7. Pass it to the loaded Keras model.
8. Get the 10 probability values.
9. Calculate predicted class using argmax.
10. Calculate confidence.
11. Sort probabilities and return top 3 predictions.

Expected preprocessing:

image = image.convert("RGB")
image = image.resize((32, 32))
image = np.array(image)
image = image / 255.0
image = np.expand_dims(image, axis=0)

prediction = model.predict(image, verbose=0)

predicted_index = np.argmax(prediction[0])
confidence = float(prediction[0][predicted_index])

Do not change the model preprocessing.

Return a clean dictionary such as:

{
    "predicted_class": "airplane",
    "confidence": 0.87,
    "top_predictions": [
        {
            "class": "airplane",
            "confidence": 0.87
        },
        {
            "class": "ship",
            "confidence": 0.06
        },
        {
            "class": "automobile",
            "confidence": 0.03
        }
    ]
}

==================================================
7. FLASK ROUTES
==================================================

Create routes.py.

Routes:

GET /
- Render the main application page.

POST /predict
- Accept uploaded image.
- Validate the upload.
- Run prediction.
- Return JSON.

Example:

{
    "success": true,
    "prediction": {
        "predicted_class": "airplane",
        "confidence": 0.87,
        "top_predictions": [...]
    }
}

If something goes wrong:

{
    "success": false,
    "error": "Human-readable error message"
}

Use appropriate HTTP status codes.

==================================================
8. FILE UPLOAD SECURITY
==================================================

Implement proper upload validation.

Allowed extensions:

- png
- jpg
- jpeg
- webp

Do not trust the filename.

Use secure_filename where appropriate.

Limit upload size.

Configure Flask:

MAX_CONTENT_LENGTH

to something reasonable such as 5 MB.

Validate that the uploaded file is actually an image.

Handle:
- Empty upload
- Unsupported file type
- Corrupted image
- Oversized image
- Missing file

Do not allow arbitrary file execution.

==================================================
9. FRONTEND DESIGN
==================================================

Create a premium AI product interface.

Design direction:

- Minimal
- Elegant
- Modern
- Premium
- Professional
- Clean typography
- Strong visual hierarchy
- Smooth animations
- Excellent spacing
- Responsive design

Use a sophisticated color palette.

Suggested palette:

Background:
#080B12

Secondary background:
#101522

Card:
#141A28

Primary accent:
#7C5CFC

Secondary accent:
#23C6FF

Text:
#F8FAFC

Muted text:
#94A3B8

Success:
#34D399

Do not make the interface look like a generic Bootstrap template.

Use CSS variables for the color system.

==================================================
10. LANDING PAGE
==================================================

Create a hero section.

Heading:

"See What Your Image Is."

Subtitle:

"Upload an image and let our CIFAR-10 AI classifier identify what it sees."

Include a small badge:

"AI IMAGE CLASSIFIER"

Main upload card should be the visual focus.

Include subtle background gradients or glow effects.

Avoid excessive animations.

==================================================
11. IMAGE UPLOAD EXPERIENCE
==================================================

Create a large drag-and-drop upload area.

The upload area should support:

- Click to upload
- Drag and drop
- PNG
- JPG
- JPEG
- WEBP

Display:

"Drop your image here"

and:

"or click to browse"

Also show:

"Maximum file size: 5 MB"

Once uploaded:

- Show image preview.
- Show filename.
- Show image dimensions if useful.
- Show a remove button.
- Enable the Predict button.

==================================================
12. PREDICT BUTTON
==================================================

Create a premium CTA:

"Analyze Image"

When clicked:

- Disable button.
- Show loading animation.
- Display text:

"Analyzing image..."

Do not allow multiple simultaneous requests.

When prediction completes:

- Restore button.
- Show results with animation.

==================================================
13. RESULTS UI
==================================================

Create a beautiful result card.

Show:

Prediction

AIRPLANE

Confidence

87.4%

Use a large visual representation of the predicted class.

If suitable, use simple icons/emojis or CSS-based visual elements, but don't depend on external image APIs.

Show a confidence progress bar.

Example:

Airplane
█████████████████░░░ 87.4%

Then show:

"Top Predictions"

1. Airplane — 87.4%
2. Ship — 6.2%
3. Automobile — 3.1%

Use horizontal confidence bars.

The predicted class should be visually emphasized.

==================================================
14. IMAGE PREVIEW
==================================================

Show the uploaded image alongside or above the result.

On desktop:

LEFT:
Uploaded Image

RIGHT:
AI Prediction

On mobile:

Image
↓
Prediction

Make the result layout responsive.

==================================================
15. JAVASCRIPT
==================================================

Use vanilla JavaScript.

Implement:

- Drag and drop
- File selection
- Preview
- Upload validation
- AJAX/fetch request
- Loading state
- Error handling
- Result rendering
- Reset functionality

Do not reload the page after prediction.

Use:

fetch("/predict", {
    method: "POST",
    body: formData
})

Handle JSON responses cleanly.

==================================================
16. ERROR UX
==================================================

Never expose Python stack traces to the user.

Show friendly messages such as:

"Please upload an image first."

"Unsupported file format. Please upload PNG, JPG, JPEG, or WEBP."

"The image could not be processed. Please try another image."

"Something went wrong while analyzing the image. Please try again."

Use an elegant toast/alert component.

==================================================
17. RESPONSIVENESS
==================================================

The webapp must work properly on:

- Desktop
- Laptop
- Tablet
- Mobile

Use responsive CSS.

Do not allow horizontal scrolling.

The upload card should adapt to smaller screens.

==================================================
18. ACCESSIBILITY
==================================================

Follow good accessibility practices.

Include:

- Proper labels
- Alt text
- Keyboard-accessible upload controls
- Visible focus states
- Semantic HTML
- Sufficient color contrast
- aria attributes where appropriate

The drag-and-drop area must still be usable without drag-and-drop.

==================================================
19. BACKEND CONFIGURATION
==================================================

Create config.py.

Centralize:

- MODEL_PATH
- MAX_CONTENT_LENGTH
- ALLOWED_EXTENSIONS
- DEBUG configuration
- Secret key

Use environment variables where appropriate.

Create:

.env.example

Do NOT commit actual secrets.

==================================================
20. REQUIREMENTS.TXT
==================================================

Create requirements.txt containing appropriate dependencies.

At minimum include:

Flask
tensorflow
numpy
Pillow
python-dotenv

Use versions compatible with the trained model environment.

Do not randomly upgrade TensorFlow/Keras.

==================================================
21. GITIGNORE
==================================================

Create a production-quality .gitignore.

Include:

__pycache__/
*.pyc
.venv/
venv/
.env
.ipynb_checkpoints/
uploads/*
!uploads/.gitkeep

If classifier.h5 is intentionally included in the project, do NOT ignore it.

==================================================
22. TESTING
==================================================

Create basic tests.

At minimum test:

1. Home page returns HTTP 200.
2. Missing image returns appropriate error.
3. Unsupported file returns appropriate error.
4. Valid image reaches prediction pipeline.
5. Prediction result contains:
   - predicted_class
   - confidence
   - top_predictions

Do not require a GPU.

==================================================
23. LOGGING
==================================================

Add basic production-friendly logging.

Log:

- Application startup
- Model loading
- Prediction requests
- Prediction success
- Prediction failures

Do NOT log image contents.

Do NOT log sensitive information.

==================================================
24. PERFORMANCE
==================================================

Optimize the application reasonably.

Important:

- Load the model once.
- Do not reload the model per request.
- Avoid unnecessary image conversions.
- Use verbose=0 during prediction.
- Keep uploaded files controlled.
- Avoid unnecessary disk writes.

==================================================
25. FLASK APP FACTORY
==================================================

Use an application factory pattern.

For example:

create_app()

The project should be structured so that it can eventually be deployed using:

Gunicorn

or another WSGI server.

Do not use:

app.run(debug=True)

as the production deployment mechanism.

It is fine to provide a development command separately.

==================================================
26. WSGI
==================================================

Create:

wsgi.py

which exposes:

app = create_app()

This should allow deployment through a WSGI server.

==================================================
27. README
==================================================

Create a comprehensive README.md containing:

Project overview

Features

Model architecture

CIFAR-10 classes

Project structure

Python version

Virtual environment setup

Installation:

python -m venv venv

Windows activation:

venv\Scripts\activate

Install:

pip install -r requirements.txt

How to place the model:

models/classifier.h5

How to run:

python run.py

Development URL:

http://127.0.0.1:5000

Explain how prediction works.

Explain image preprocessing:

RGB
→ resize 32x32
→ NumPy
→ divide by 255
→ add batch dimension
→ model prediction

Also explain production deployment using a WSGI server.

==================================================
28. IMPORTANT MODEL COMPATIBILITY
==================================================

Do NOT modify the trained model architecture.

Do NOT retrain the model.

Do NOT change the preprocessing.

Do NOT convert the model to another framework unless explicitly requested.

The application must use:

classifier.h5

The model expects:

(32,32,3)

and preprocessing must remain:

image / 255.0

The output has 10 classes corresponding to CIFAR-10.

==================================================
29. UI DETAILS
==================================================

Make the UI feel like a modern AI SaaS product.

Include:

- Premium dark theme
- Glass-like cards
- Soft gradients
- Subtle shadows
- Rounded corners
- Modern typography
- Smooth hover states
- Elegant upload zone
- Animated prediction result
- Progress bars
- Loading spinner
- Toast notifications

Do not overuse gradients.

Do not make it flashy or childish.

The design should look suitable for a portfolio project that could be shown to recruiters or clients.

Add a small footer:

"Powered by TensorFlow • Flask • CIFAR-10"

==================================================
30. OPTIONAL CLASS VISUALIZATION
==================================================

If appropriate, show a small badge/icon representing the predicted class.

For example:

✈ Airplane
🚗 Automobile
🐦 Bird
🐱 Cat
🦌 Deer
🐕 Dog
🐸 Frog
🐎 Horse
🚢 Ship
🚚 Truck

Keep this subtle and professional.

==================================================
31. FINAL REQUIREMENT
==================================================

After generating the project:

1. Verify all imports.
2. Verify Flask starts.
3. Verify classifier.h5 loads.
4. Verify the prediction endpoint works.
5. Verify an actual CIFAR-10-sized image can be processed.
6. Verify the output contains the predicted class and confidence.
7. Verify the frontend communicates correctly with the backend.
8. Verify the UI works on desktop and mobile.
9. Fix any runtime errors you encounter.
10. Provide exact commands for local execution.

Do not merely generate mock code.

Create a functional end-to-end application.

If classifier.h5 is not physically available in the project directory, clearly indicate where I need to place it:

models/classifier.h5

Do not create a fake model or fake prediction results.