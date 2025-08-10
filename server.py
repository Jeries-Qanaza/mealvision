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
from huggingface_hub import InferenceClient
import concurrent.futures

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

# --- Hugging Face Setup ---
HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")
# DEBUG: Check if the environment variable was loaded
print(f"DEBUG: Reading HUGGING_FACE_TOKEN. Found token: {HUGGING_FACE_TOKEN is not None}")

hf_client = None
if HUGGING_FACE_TOKEN:
    hf_client = InferenceClient(token=HUGGING_FACE_TOKEN)
    # DEBUG: Confirm client initialization
    print("DEBUG: Hugging Face client has been initialized.")
else:
    # DEBUG: Report that the client was NOT initialized
    print("DEBUG: Hugging Face token NOT found. Client was not initialized.")


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
        # Get the meal type from the request, will be None if not provided
        meal_type = data.get("meal_type")

        # --- Prompt Engineering ---
        # Previous prompt = f"What meal can I make with these ingredients: {ingredients_str}, considering the following dietary preferences: {dietary_preferences}. Answer in JSON format with at least 3 options including meal names and steps."

        # Start with the base prompt
        prompt_parts = [
            f'What meal can I make with these ingredients: {ingredients_str}.'
        ]

        # Add dietary preferences if they exist
        if dietary_preferences:
            prompt_parts.append(f'Considering the following dietary preferences: {dietary_preferences}.')

        # Add meal type context ONLY if it was selected by the user
        if meal_type:
            prompt_parts.append(f'The meal should be suitable for {meal_type}.')

        # Add formatting instructions and specify the number of options
        prompt_parts.append(
            'Answer in JSON format exactly like this: '
            '{"meals": [{"mealName": "", "description": "", "steps": []}]} '
            'with at least 3 meal options'
        )
        
        # Add meal type suitability to the final instruction part, if applicable
        if meal_type:
            prompt_parts[-1] += f' suitable for {meal_type}.'
        else:
            prompt_parts[-1] += '.'

        # Join all parts to form the final prompt
        prompt = " ".join(prompt_parts)
        
        print(f"DEBUG: Final prompt sent to Gemini: {prompt}")

        t0 = time.time()
        response = Gmodel.generate_content(prompt)
        t1 = time.time()
        print(f"DEBUG: Gemini generation took {t1-t0:.2f} seconds")
        
        json_text = response.text.strip().removeprefix("```json").removesuffix("```")
        meal_data = json.loads(json_text)

        # --- Start of new image generation logic ---
        # Check if the Hugging Face client is configured
        if hf_client:
            # DEBUG: Check if this block is being entered
            print("DEBUG: Condition 'if hf_client' is TRUE. Entering image generation block.")
            
            def generate_meal_image(meal):
                # This function generates a single image for a given meal.
                # It will be called in parallel for efficiency.
                try:
                    meal_name = meal.get("mealName")
                    # Create a high-quality, descriptive prompt for better results
                    image_prompt = f"Professional food photography of {meal_name}, cinematic lighting, high detail, on a rustic wooden table"
                    
                    print(f"DEBUG: Generating image for '{meal_name}'...")
                    
                    # Call the HF Inference API
                    generated_image = hf_client.text_to_image(
                        image_prompt,
                        model="stabilityai/stable-diffusion-xl-base-1.0",
                        negative_prompt="cartoon, drawing, anime, ugly, deformed, blurry",
                        height=1024,
                        width=1024,
                        num_inference_steps=30
                    )
                    
                    # Convert the PIL image to a base64 string
                    buffered = io.BytesIO()
                    generated_image.save(buffered, format="JPEG")
                    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                    
                    # Return the meal name and the generated image string
                    return meal_name, img_str
                except Exception as img_e:
                    print(f"!!! ERROR generating image for {meal.get('mealName')}: {img_e} !!!")
                    # Return None on failure
                    return meal.get("mealName"), None

            # Use a ThreadPoolExecutor to generate images for all meals in parallel
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Create a future for each meal's image generation
                future_to_meal = {executor.submit(generate_meal_image, meal): meal for meal in meal_data["meals"]}
                
                # Create a mapping from mealName to the generated image string
                image_map = {}
                for future in concurrent.futures.as_completed(future_to_meal):
                    meal_name, img_str = future.result()
                    if img_str:
                        image_map[meal_name] = img_str
                
                # Add the generated image to each meal object
                for meal in meal_data["meals"]:
                    meal["image"] = image_map.get(meal.get("mealName")) # get() safely returns None if not found

            print("--- Finished parallel image generation ---")
        else:
            # DEBUG: Report that the image generation block was skipped
            print("DEBUG: Condition 'if hf_client' is FALSE. Skipping image generation.")
            # If no HF token is set, do not generate images
            for meal in meal_data["meals"]:
                meal["image"] = None
        # --- End of new image generation logic ---

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