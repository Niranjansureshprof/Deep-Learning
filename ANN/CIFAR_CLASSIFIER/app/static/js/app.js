/**
 * CIFAR-10 AI Image Classifier - Client Controller
 * Handles drag-and-drop, client-side validation, AJAX inference, and dynamic UI rendering.
 */

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    
    // Panels
    const uploadPanel = document.getElementById("upload-panel");
    const previewPanel = document.getElementById("preview-panel");
    const resultsPanel = document.getElementById("results-panel");
    
    // Staged Preview Elements
    const stagedImage = document.getElementById("staged-image");
    const stagedFilename = document.getElementById("staged-filename");
    const stagedDimensions = document.getElementById("staged-dimensions");
    const stagedFilesize = document.getElementById("staged-filesize");
    const removeBtn = document.getElementById("remove-btn");
    const analyzeBtn = document.getElementById("analyze-btn");
    const btnSpinner = document.getElementById("btn-spinner");
    const btnText = document.getElementById("btn-text");
    
    // Results Elements
    const resultImage = document.getElementById("result-image");
    const resultFilenameDisplay = document.getElementById("result-filename-display");
    const mainPredictionEmoji = document.getElementById("main-prediction-emoji");
    const mainPredictedClass = document.getElementById("main-predicted-class");
    const mainConfidenceVal = document.getElementById("main-confidence-val");
    const mainProgressBar = document.getElementById("main-progress-bar");
    const topPredictionsList = document.getElementById("top-predictions-list");
    const resetBtn = document.getElementById("reset-btn");
    
    // Toast Container
    const toastContainer = document.getElementById("toast-container");

    // Constants
    const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB
    const ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "webp"];

    // App State
    let currentFile = null;
    let isAnalyzing = false;

    // =========================================================================
    // Toast Notifications
    // =========================================================================
    function showToast(message, type = "error", duration = 4500) {
        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;
        
        const iconSvg = type === "error" 
            ? `<svg class="toast-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`
            : `<svg class="toast-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`;

        toast.innerHTML = `
            ${iconSvg}
            <div class="toast-message">${escapeHtml(message)}</div>
            <button class="toast-close" aria-label="Close notification">&times;</button>
        `;

        toast.querySelector(".toast-close").addEventListener("click", () => {
            toast.remove();
        });

        toastContainer.appendChild(toast);

        setTimeout(() => {
            if (toast.parentElement) {
                toast.style.opacity = "0";
                toast.style.transform = "translateY(-10px)";
                setTimeout(() => toast.remove(), 250);
            }
        }, duration);
    }

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }

    // =========================================================================
    // File Validation & Handling
    // =========================================================================
    function validateFile(file) {
        if (!file) {
            showToast("Please upload an image first.");
            return false;
        }

        const extension = file.name.split(".").pop().toLowerCase();
        if (!ALLOWED_EXTENSIONS.includes(extension)) {
            showToast("Unsupported file format. Please upload PNG, JPG, JPEG, or WEBP.");
            return false;
        }

        if (file.size > MAX_FILE_SIZE) {
            showToast("File size exceeds 5 MB. Please upload a smaller image.");
            return false;
        }

        return true;
    }

    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + " B";
        const kb = bytes / 1024;
        if (kb < 1024) return kb.toFixed(1) + " KB";
        return (kb / 1024).toFixed(2) + " MB";
    }

    function handleSelectedFile(file) {
        if (!validateFile(file)) return;

        currentFile = file;

        // Read image for preview and metadata
        const reader = new FileReader();
        reader.onload = (e) => {
            const dataUrl = e.target.result;
            stagedImage.src = dataUrl;
            stagedFilename.textContent = file.name;
            stagedFilename.title = file.name;
            stagedFilesize.textContent = formatFileSize(file.size);

            // Compute dimensions
            const tempImg = new Image();
            tempImg.onload = () => {
                stagedDimensions.textContent = `${tempImg.naturalWidth} × ${tempImg.naturalHeight} px`;
            };
            tempImg.src = dataUrl;

            // Switch to staged preview panel
            uploadPanel.classList.add("hidden");
            resultsPanel.classList.add("hidden");
            previewPanel.classList.remove("hidden");
        };

        reader.onerror = () => {
            showToast("Failed to read the selected file. Please try another image.");
        };

        reader.readAsDataURL(file);
    }

    // =========================================================================
    // Drag & Drop Listeners
    // =========================================================================
    ["dragenter", "dragover"].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add("dragover");
        });
    });

    ["dragleave", "drop"].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove("dragover");
        });
    });

    dropZone.addEventListener("drop", (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files && files.length > 0) {
            handleSelectedFile(files[0]);
        }
    });

    // Click & Keyboard triggers on Drop Zone
    dropZone.addEventListener("click", () => {
        fileInput.click();
    });

    dropZone.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            fileInput.click();
        }
    });

    fileInput.addEventListener("change", (e) => {
        if (fileInput.files && fileInput.files.length > 0) {
            handleSelectedFile(fileInput.files[0]);
        }
    });

    // Remove / Clear staged image
    removeBtn.addEventListener("click", () => {
        resetWorkspace();
    });

    // =========================================================================
    // Prediction Request Execution
    // =========================================================================
    analyzeBtn.addEventListener("click", async () => {
        if (isAnalyzing || !currentFile) return;

        setLoadingState(true);

        const formData = new FormData();
        formData.append("image", currentFile);

        try {
            const response = await fetch("/predict", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                const errorMsg = data.error || "Something went wrong while analyzing the image. Please try again.";
                showToast(errorMsg);
                setLoadingState(false);
                return;
            }

            // Render prediction output
            renderPredictionResults(data.prediction);

        } catch (err) {
            console.error("Inference request failed:", err);
            showToast("Network error or server unavailable. Please try again.");
            setLoadingState(false);
        }
    });

    function setLoadingState(loading) {
        isAnalyzing = loading;
        analyzeBtn.disabled = loading;
        removeBtn.disabled = loading;

        if (loading) {
            btnSpinner.classList.remove("hidden");
            btnText.textContent = "Analyzing image...";
        } else {
            btnSpinner.classList.add("hidden");
            btnText.textContent = "Analyze Image";
        }
    }

    // =========================================================================
    // Render Results View
    // =========================================================================
    function renderPredictionResults(prediction) {
        // Set image in result card
        resultImage.src = stagedImage.src;
        resultFilenameDisplay.textContent = currentFile ? currentFile.name : "Uploaded Image";

        // Main prediction data
        mainPredictionEmoji.textContent = prediction.emoji || "🔍";
        mainPredictedClass.textContent = prediction.predicted_class.toUpperCase();
        mainConfidenceVal.textContent = prediction.confidence_percent || `${(prediction.confidence * 100).toFixed(1)}%`;
        
        // Animate hero progress bar
        const confidencePct = (prediction.confidence * 100);
        mainProgressBar.style.width = "0%";
        setTimeout(() => {
            mainProgressBar.style.width = `${Math.min(confidencePct, 100)}%`;
        }, 80);

        // Render top 3 predictions
        topPredictionsList.innerHTML = "";
        if (Array.isArray(prediction.top_predictions)) {
            prediction.top_predictions.forEach((item, index) => {
                const itemConfidencePct = (item.confidence * 100).toFixed(1);
                const row = document.createElement("div");
                row.className = "prediction-row";
                row.innerHTML = `
                    <div class="prediction-row-header">
                        <div class="prediction-row-left">
                            <span class="prediction-rank">#${index + 1}</span>
                            <span class="prediction-row-emoji">${item.emoji || "•"}</span>
                            <span class="prediction-row-label">${escapeHtml(item.class)}</span>
                        </div>
                        <span class="prediction-row-pct">${itemConfidencePct}%</span>
                    </div>
                    <div class="mini-progress-track">
                        <div class="mini-progress-fill" style="width: 0%"></div>
                    </div>
                `;
                topPredictionsList.appendChild(row);

                setTimeout(() => {
                    const fill = row.querySelector(".mini-progress-fill");
                    if (fill) {
                        fill.style.width = `${Math.min(itemConfidencePct, 100)}%`;
                    }
                }, 100 + index * 60);
            });
        }

        // Transition panels
        setLoadingState(false);
        previewPanel.classList.add("hidden");
        uploadPanel.classList.add("hidden");
        resultsPanel.classList.remove("hidden");

        // Scroll gracefully to results if on mobile
        if (window.innerWidth < 768) {
            resultsPanel.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    }

    // Reset button on Results View
    resetBtn.addEventListener("click", () => {
        resetWorkspace();
    });

    function resetWorkspace() {
        currentFile = null;
        fileInput.value = "";
        stagedImage.src = "";
        resultImage.src = "";
        mainProgressBar.style.width = "0%";
        topPredictionsList.innerHTML = "";

        setLoadingState(false);

        resultsPanel.classList.add("hidden");
        previewPanel.classList.add("hidden");
        uploadPanel.classList.remove("hidden");
    }
});
