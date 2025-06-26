# ==============================================================================
# Imports
# ==============================================================================
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import requests
import base64
from flask_mail import Mail, Message
from ultralytics import YOLO
import io
from PIL import Image
import tempfile
import os
import torch
import gc
from dotenv import load_dotenv
import time
import traceback
import concurrent.futures # Keep this for future use with Stability AI

# ==============================================================================
# Initial Setup
# ==============================================================================

# Load environment variables from .env file
load_dotenv()

# --- Limit model threads for server stability ---
# This is crucial to prevent PyTorch from hogging all CPU cores on the server
torch.set_num_threads(1)
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

# --- Flask App and CORS Setup ---
app = Flask(__name__)
CORS(app) # Simplified CORS setup, it will handle OPTIONS requests automatically

# ==============================================================================
# API Client Configurations
# ==============================================================================

# --- Gemini AI Setup ---
GEMINI_API_KEY = os.getenv("VUE_APP_GEMINI_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("Missing VUE_APP_GEMINI_KEY environment variable")
genai.configure(api_key=GEMINI_API_KEY)
Gmodel = genai.GenerativeModel("gemini-1.5-flash")

# --- Stability AI Setup ---
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")

# --- Email Setup ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
mail = Mail(app)

# ==============================================================================
# YOLO Model (Lazy Loading)
# ==============================================================================
yolo_model = None

def get_yolo_model():
    """Lazily loads the YOLO model on the first request."""
    global yolo_model
    if yolo_model is None:
        print("Loading YOLO model for the first time...")
        yolo_model = YOLO("./src/assets/best8s.pt")
        print("YOLO model loaded successfully.")
    return yolo_model

# ==============================================================================
# Helper Functions
# ==============================================================================
def generate_image(prompt):
    """Generates an image using the Stability AI API."""
    response = requests.post(
        "https://api.stability.ai/v2beta/stable-image/generate/core",
        headers={
            "authorization": f"Bearer {STABILITY_API_KEY}",
            "accept": "image/*"
        },
        files={"none": ''},
        data={ "prompt": prompt, "output_format": "jpeg" },
    )
    if response.status_code == 200:
        return base64.b64encode(response.content).decode("utf-8")
    else:
        raise Exception(str(response.json()))

# ==============================================================================
# Flask Routes (API Endpoints)
# ==============================================================================

@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint to confirm the server is running."""
    return jsonify({"status": "Server is running!", "message": "API is healthy"})

@app.route("/detect", methods=["POST"])
def detect():
    """Receives an image, detects food items using YOLO, and returns labels."""
    try:
        t_start = time.time()
        print("\n--- Received new request for /detect ---")

        if "image" in request.files:
            file = request.files["image"]
            image = Image.open(file.stream).convert("RGB")
        else:
            data = request.get_json()
            image_data = data["image"].split(",")[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        t_image_loaded = time.time()
        print(f"DEBUG: Image loading took {t_image_loaded - t_start:.2f} seconds")

        #----------- Resizing large images to improve performance and prevent crashes -----------
        MAX_RESOLUTION = (1280, 1280)
        if image.width > MAX_RESOLUTION[0] or image.height > MAX_RESOLUTION[1]:
            print(f"DEBUG: Image is large ({image.size}), resizing it down...")
            image.thumbnail(MAX_RESOLUTION, Image.Resampling.LANCZOS)
            print(f"DEBUG: Image resized to {image.size}")
        #----------- End of resizing block -----------

        model = get_yolo_model()
        t_model_got = time.time()
        print(f"DEBUG: Getting YOLO model took {t_model_got - t_image_loaded:.2f} seconds")

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp:
            image.save(temp.name)
            #----------- Running model with a fixed image size for consistent performance -----------
            results = model.predict(source=temp.name, imgsz=[640, 640])
            image.close()
            os.unlink(temp.name)

        t_prediction_done = time.time()
        print(f"DEBUG: YOLO Prediction took {t_prediction_done - t_model_got:.2f} seconds <<<<<<<<<<<<<<<<<<")

        labels = [results[0].names[int(box.cls[0])] for box in results[0].boxes]

        del results
        gc.collect()

        t_end = time.time()
        print(f"--- TOTAL DETECT TIME: {t_end - t_start:.2f} seconds ---")

        return jsonify({"labels": list(set(labels))}) # Using set to return unique labels

    except Exception as e:
        print(f"!!! ERROR in /detect: {e} !!!")
        traceback.print_exc()
        return jsonify({"error": "An error occurred during image detection."}), 500

@app.route("/generate-meals", methods=["POST", "OPTIONS"])
def generate_meals():
    # Handle CORS preflight requests
    if request.method == "OPTIONS":
        return jsonify({}), 200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
        }
    try:
        t_total_start = time.time()
        print("\n--- Received new request for /generate-meals ---")

        data = request.json
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
            
        ingredients_str = ", ".join(data.get("ingredients", []))
        dietary_preferences = data.get('dietary_preferences', '')
        user_local_time = data.get("user_local_time", "any time of day")

        # Previous prompt = f"What meal can I make with these ingredients: {ingredients_str}, considering the following dietary preferences: {dietary_preferences}. Answer in JSON format with at least 3 options including meal names and steps."
        prompt = (
            f'What meal can I make with these ingredients: {ingredients_str}, '
            f'considering the following dietary preferences: {dietary_preferences} '
            f'and that it is currently the {user_local_time} for the user. '
            f'Answer in JSON format exactly like this: '
            f'{{"meals": [{{"mealName": "", "description": "", "steps": []}}]}} '
            f'with at least 3 meal options suitable for {user_local_time}.'
        )

        t0 = time.time()
        response = Gmodel.generate_content(prompt)
        t1 = time.time()
        print(f"DEBUG: Gemini generation took {t1-t0:.2f} seconds")
        
        json_text = response.text.strip().removeprefix("```json").removesuffix("```")
        meal_data = json.loads(json_text)

        # NOTE: Image generation is currently disabled if STABILITY_API_KEY is not set.
        # If we enable it, remember to use parallel processing.
        if STABILITY_API_KEY:
             # Left here for future implementation with parallel processing
            pass
        else:
             for meal in meal_data["meals"]:
                meal["image"] = None

        t_total_end = time.time()
        print(f"--- TOTAL GENERATE-MEALS TIME: {t_total_end - t_total_start:.2f} seconds ---")

        return jsonify({"meals_res": meal_data["meals"]})

    except Exception as e:
        print(f"!!! ERROR in /generate-meals: {e} !!!")
        traceback.print_exc()
        return jsonify({"error": "An error occurred while generating meals."}), 500

@app.route('/send-email', methods=['POST'])
def send_email():
    """Handles sending a contact form email."""
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')

        if not all([name, email, message]):
            return jsonify({"error": "Missing form data"}), 400

        msg = Message(subject=f"New Contact Message from {name}",
                      recipients=['je.yo.yvc@gmail.com'],
                      body=f"From: {name}\nEmail: {email}\n\nMessage:\n{message}")
        
        mail.send(msg)
        return jsonify({"message": "Email sent successfully"}), 200
    except Exception as e:
        print(f"!!! ERROR sending email: {e} !!!")
        traceback.print_exc()
        return jsonify({"error": "An error occurred while sending the email."}), 500

# ==============================================================================
# Main Execution
# ==============================================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)    