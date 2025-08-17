# ==============================================================================
# Imports
# ==============================================================================
import json
import subprocess
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
from huggingface_hub import HfApi, InferenceClient
from huggingface_hub.utils import HfHubHTTPError
import concurrent.futures
from google.api_core.exceptions import ResourceExhausted

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
# Allowing the app to accept requests from different origins
CORS(app) 

# ==============================================================================
# API Client Configurations
# ==============================================================================

# --- Gemini AI Setup ---
GEMINI_API_KEY = os.getenv("VUE_APP_GEMINI_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("Missing Gemini API key.")
genai.configure(api_key=GEMINI_API_KEY)
Gmodel = genai.GenerativeModel("gemini-2.5-flash-lite")

try:
    # Validate the key and connection
    Gmodel.count_tokens("validate") 
    print("INFO: Gemini client initialized and validated successfully.")
except Exception as e:
    # If this fails, the key is likely invalid or there's a connection issue.
    print("ERROR: Failed to validate Gemini API key. The server will not start!")
    raise RuntimeError(f"Gemini API key validation failed: {e}") from e

# --- Hugging Face Setup ---
HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN") 

hf_client = None

if HUGGING_FACE_TOKEN:
  try:
    # Validate the token using HfApi
    HfApi().whoami(token=HUGGING_FACE_TOKEN)
    # If validation is successful, initialize the InferenceClient
    hf_client = InferenceClient(token=HUGGING_FACE_TOKEN)
    print("INFO: Hugging Face token validated successfully. Client initialized.")
  except HfHubHTTPError as e:
    # Catch authentication errors 
    hf_client = None
    print(f"WARNING: Hugging Face token is invalid. Image generation will be disabled. Error: {e}")
  except Exception as e:
    # Catch other potential errors during initialization
    hf_client = None
    print(f"WARNING: Could not initialize Hugging Face client. Image generation will be disabled. Error: {e}")
else:
  print("WARNING: Hugging Face token not found. Image generation will be disabled.")

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

# YOLO health
def check_yolo_health():
    """
    Runs prediction on multiple test images to check YOLO model health.
    Returns True only if all images are processed successfully, False otherwise.
    """
    try:
        model = get_yolo_model()
        
        # Images path
        test_image_paths = [
            "./src/assets/health_check_images/apple.jpg",
            "./src/assets/health_check_images/salmon.jpg",
            "./src/assets/health_check_images/spaghetti.jpg",
            "./src/assets/health_check_images/tomato.jpg"
        ]

        for image_path in test_image_paths:
            if not os.path.exists(image_path):
                print(f"Health Check Error: Test image not found at path: {image_path}")
                return False # Fail the check if any image is missing

            # verbose=False to keep the main logs clean
            results = model.predict(source=image_path, imgsz=[640, 640], verbose=False)

            # Check for a valid result. If any prediction fails, the whole check fails
            if not results or len(results) == 0:
                print(f"Health Check Error: Model returned an invalid result for {image_path}")
                return False
        
        # All checks passed
        return True

    except Exception as e:
        print(f"Health Check Error (YOLO): An exception occurred: {e}.")
        return False

# Gemini api check (of the genreate meals)
def check_gemini_health():
    """
    Sends a prompt to Gemini to check its health and API key.
    Returns True on success, False on failure.
    """
    try:
        # Simple prompt 
        response = Gmodel.generate_content(
            "Are you operational? Respond with only the word: ok", 
            request_options={'timeout': 15}
        )
        # Check if the expected word is in the response
        return "ok" in response.text.lower()
    except Exception as e:
        print(f"Health Check Error (Gemini): {e}.")
        return False

# Check if the model available on Hugging Face
def check_hf_model_health(model_id="stabilityai/stable-diffusion-xl-base-1.0"):
    """
    Checks the Hugging Face Hub API to see if the model repository is accessible.
    Returns True on success, False on failure.
    """
    try:
        # Check if the client was initialized in the first place
        if not hf_client:
            print("Health Check Error (Hugging Face): Client not initialized, token might be missing.")
            return False
            
        url = f"https://huggingface.co/api/models/{model_id}"
        # Simple GET request to the model's API endpoint
        response = requests.get(url, timeout=15)
        
        # Status 200 means the model exists and is accessible
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Health Check Error (Hugging Face): {e}.")
        return False
    
# Generate meal image
def generate_meal_image(meal):
    """This function generates a single image for a given meal.
        It will be called in parallel for efficiency."""
    try:
        meal_name = meal.get("mealName")
        # Create a high-quality, descriptive prompt for better results
        image_prompt = f"Professional food photography of {meal_name}, high detail. Each image should have a unique and different artistic theme or style. Make the image square with dimensions 512x512 pixels."
        
        print(f"DEBUG: Generating image for '{meal_name}'...")
        
        # Call the HF Inference API
        generated_image = hf_client.text_to_image(
            image_prompt,
            model="stabilityai/stable-diffusion-xl-base-1.0",
            negative_prompt="cartoon, drawing, anime, ugly, deformed, blurry",
            height=512,
            width=512,
            num_inference_steps=30
        )
        
        # Convert the PIL image to a base64 string
        buffered = io.BytesIO()
        generated_image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        # Return the meal name and the generated image string
        return meal_name, img_str
    except Exception as img_e:
        print(f"ERROR generating image for {meal.get('mealName')}: {img_e}.")
        # Return None on failure
        return meal.get("mealName"), None
    
# ==============================================================================
# Flask Routes (API Endpoints)
# ==============================================================================

# Server Health
@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint to confirm the server is running."""
    return jsonify({"status": "Server is running!", "message": "API is healthy"})

# API's and YOLO model Health
@app.route("/health")
def full_health_check():
    """
    Runs an health check on all critical external dependencies (YOLO, Gemini, HF).
    Returns a detailed JSON status report.
    """
    print("\n--- Running full health check ---")
    
    # Run all checks in parallel for efficiency
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_yolo = executor.submit(check_yolo_health)
        future_gemini = executor.submit(check_gemini_health)
        future_hf = executor.submit(check_hf_model_health)

        checks = {
            "yolo_model": future_yolo.result(),
            "gemini_api": future_gemini.result(),
            "huggingface_model_api": future_hf.result()
        }
    
    overall_status = "ok"
    # If any check failed, the overall status is 'error'
    if not all(checks.values()):
        overall_status = "error"
        
    # Prepare a detailed JSON response
    response_body = {
        "overall_status": overall_status,
        "details": {
            "yolo_model": "ok" if checks["yolo_model"] else "error",
            "gemini_api": "ok" if checks["gemini_api"] else "error",
            "huggingface_model_api": "ok" if checks["huggingface_model_api"] else "error"
        }
    }
    
    # Return a 200 status code if all checks passed, otherwise 503 (Service Unavailable)
    # UptimeRobot service look for this status code to determine if the service is "up" or "down".
    http_status = 200 if overall_status == "ok" else 503
    
    print(f"--- Health check finished with status: {overall_status} ---")
    return jsonify(response_body), http_status

# Detect (By YOLOv10s)
@app.route("/detect", methods=["POST"])
def detect():
    """Receives an image, detects food items using YOLO, and returns labels."""
    try:
        t_start = time.time()
        print("\n--- Received new request for /detect ---")

        # Load image from request
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

        # Resize large images to improve performance
        MAX_RESOLUTION = (1280, 1280)
        if image.width > MAX_RESOLUTION[0] or image.height > MAX_RESOLUTION[1]:
            print(f"DEBUG: Image is large ({image.size}), resizing it down...")
            image.thumbnail(MAX_RESOLUTION, Image.Resampling.LANCZOS)
            print(f"DEBUG: Image resized to {image.size}")

        # Load YOLO model
        model = get_yolo_model()
        t_model_got = time.time()
        print(f"DEBUG: Getting YOLO model took {t_model_got - t_image_loaded:.2f} seconds")

        # --- Use mkstemp for Windows-safe temporary file ---
        fd, temp_name = tempfile.mkstemp(suffix=".jpg")
        os.close(fd)  # Close OS handle immediately
        image.save(temp_name)
        image.close()  # Close PIL handle

        try:
            # Run YOLO prediction
            results = model.predict(source=temp_name, imgsz=[640, 640])
        finally:
            # Cleanup temp file safely
            if os.path.exists(temp_name):
                os.unlink(temp_name)

        # Extract detected labels
        labels = [results[0].names[int(box.cls[0])] for box in results[0].boxes]

        # Clean up
        del results
        gc.collect()

        t_end = time.time()
        print(f"--- TOTAL DETECT TIME: {t_end - t_start:.2f} seconds ---")

        return jsonify({"labels": list(set(labels))})  # Return unique labels

    except Exception as e:
        print(f"ERROR in /detect: {e}.")
        traceback.print_exc()
        return jsonify({"Error": "An error occurred during image detection."}), 500

# Processing videos
@app.route("/process-video", methods=["POST"])
def process_video():
    """Receives a video, extracts frames, resizes them, detects items, and returns labels AND a thumbnail."""
    if 'video' not in request.files:
        return jsonify({"Error": "No video file provided"}), 400
    
    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({"Error": "No file selected"}), 400

    t_start = time.time()
    print("\n--- Received new request for /process-video ---")

    with tempfile.TemporaryDirectory() as temp_dir:
        video_path = os.path.join(temp_dir, "input_video")
        video_file.save(video_path)
        
        t_uploaded = time.time()
        print(f"DEBUG: Video saved to temp path in {t_uploaded - t_start:.2f} seconds")

        frames_output_pattern = os.path.join(temp_dir, 'frame-%03d.jpg')
        thumbnail_path = os.path.join(temp_dir, 'thumbnail.jpg')
        
        try:
            subprocess.run(['ffmpeg', '-i', video_path, '-vf', 'fps=1', frames_output_pattern], check=True, capture_output=True, text=True)
            subprocess.run(['ffmpeg', '-i', video_path, '-ss', '00:00:01.000', '-vframes', '1', thumbnail_path], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg ERROR: {e.stderr}.")
            return jsonify({"Error": "Failed to process video with FFmpeg."}), 500

        model = get_yolo_model()
        all_detected_labels = set()
        extracted_frames = sorted([f for f in os.listdir(temp_dir) if f.startswith('frame-')])
        
        # --- RESIZING ---
        MAX_RESOLUTION = (1280, 1280)

        for frame_filename in extracted_frames:
            frame_path = os.path.join(temp_dir, frame_filename)
            try:
                # Open the frame image with PIL
                with Image.open(frame_path) as img:
                    # Check if resizing is needed
                    if img.width > MAX_RESOLUTION[0] or img.height > MAX_RESOLUTION[1]:
                        img.thumbnail(MAX_RESOLUTION, Image.Resampling.LANCZOS)
                        # Overwrite the original frame with the resized version
                        img.save(frame_path)

                # Run YOLO prediction on the frame
                results = model.predict(source=frame_path, imgsz=[640, 640])
                frame_labels = {results[0].names[int(box.cls[0])] for box in results[0].boxes}
                all_detected_labels.update(frame_labels)
            except Exception as e:
                print(f"Could not process frame {frame_filename}: {e}.")
                continue
        # --- END OF RESIZING ---

        thumbnail_base64 = None
        if os.path.exists(thumbnail_path):
            with open(thumbnail_path, "rb") as image_file:
                thumbnail_base64 = base64.b64encode(image_file.read()).decode('utf-8')

        t_end = time.time()
        print(f"--- TOTAL PROCESS-VIDEO TIME: {t_end - t_start:.2f} seconds ---")

        return jsonify({
            "labels": list(all_detected_labels),
            "thumbnail": f"data:image/jpeg;base64,{thumbnail_base64}" if thumbnail_base64 else None
        })

# Generate meals
@app.route("/generate-meals", methods=["POST"])
def generate_meals():
    try:
        t_total_start = time.time()
        print("\n--- Received new request for /generate-meals ---")

        data = request.json
        if not data or not data.get("ingredients"):
            return jsonify({"Error": "No ingredients provided."}), 400
            
        ingredients_str = ", ".join(data.get("ingredients", []))
        dietary_preferences = data.get('dietary_preferences', '')
        meal_type = data.get("meal_type")

        # --- Prompt Engineering ---
        """ Previous prompt = 
            f"What meal can I make with these ingredients: {ingredients_str}, considering the following dietary preferences: {dietary_preferences}. 
            Answer in JSON format with at least 3 options including meal names and steps."""
        
        prompt_parts = [
            f'What meal can I make with these ingredients: {ingredients_str}.'
        ]
        if dietary_preferences:
            prompt_parts.append(f'Considering the following dietary preferences: {dietary_preferences}.')
        if meal_type:
            prompt_parts.append(f'The meal should be suitable for {meal_type}.')
        prompt_parts.append(
            'Answer in JSON format exactly like this: '
            '{"meals": [{"mealName": "", "description": "", "steps": []}]} '
            'with at least 3 meal options.'
        )
        if meal_type:
            prompt_parts[-1] += f' suitable for {meal_type}.'
        else:
            prompt_parts[-1] += '.'
        prompt = " ".join(prompt_parts)
        
        print(f"DEBUG: Final prompt sent to Gemini: {prompt}")

        t0 = time.time()
        response = Gmodel.generate_content(prompt)
        t1 = time.time()
        print(f"DEBUG: Gemini generation took {t1-t0:.2f} seconds")
        
        # Safely parse the JSON response from the model
        json_text = response.text.strip().removeprefix("```json").removesuffix("```")
        meal_data = json.loads(json_text)

        # --- Image generation ---
        print("---------- CHECK HF CLIENT -----------")
        print(hf_client, meal_data.get("meals"))
        if hf_client and meal_data.get("meals"):
            print("DEBUG: Entering image generation block.")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_meal = {executor.submit(generate_meal_image, meal): meal for meal in meal_data["meals"]}
                image_map = {}
                for future in concurrent.futures.as_completed(future_to_meal):
                    meal_name, img_str = future.result()
                    if img_str:
                        image_map[meal_name] = img_str
                
                for meal in meal_data["meals"]:
                    meal["image"] = image_map.get(meal.get("mealName"))

            print("--- Finished parallel image generation ---")
        else:
            print("DEBUG: Skipping image generation.")
            if meal_data.get("meals"):
                for meal in meal_data["meals"]:
                    meal["image"] = None
        # --- End of image generation ---

        t_total_end = time.time()
        print(f"--- TOTAL GENERATE-MEALS TIME: {t_total_end - t_total_start:.2f} seconds ---")
        return jsonify({"meals_res": meal_data.get("meals", [])})

    except Exception as e:
        # CATCH ALL errors, then inspect the error message to decide the response
        error_message_str = str(e).lower()
        print(f"ERROR in /generate-meals: {e}.")
        traceback.print_exc()

        # Check for keywords related to quota/rate limit errors
        if "rate limit" in error_message_str or "resource has been exhausted" in error_message_str or "too many requests" in error_message_str:
            user_message = "You have exceeded the daily request limit for the AI model. Please try again tomorrow."
            print("QUOTA/RATE LIMIT EXCEEDED for Gemini API.")
            return jsonify({"error": user_message}), 429
        
        # Check for JSON decoding error specifically
        elif "json" in error_message_str or isinstance(e, json.JSONDecodeError):
            user_message = "The AI model returned an invalid response format. Please try again."
            print("ERROR: Failed to decode JSON from Gemini response.")
            return jsonify({"error": user_message}), 500

        # For all other errors, return a generic server error
        else:
            user_message = "An unexpected error occurred while generating meals."
            return jsonify({"error": user_message}), 500
       
# Emails 
@app.route('/send-email', methods=['POST'])
def send_email():
    """Handles sending a contact form email."""
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')

        if not all([name, email, message]):
            return jsonify({"Error": "Missing form data"}), 400

        msg = Message(subject=f"New Contact Message from {name}",
                      recipients=['je.yo.yvc@gmail.com'],
                      body=f"From: {name}\nEmail: {email}\n\nMessage:\n{message}")
        
        mail.send(msg)
        return jsonify({"message": "Email sent successfully"}), 200
    except Exception as e:
        print(f"ERROR sending email: {e}.")
        traceback.print_exc()
        return jsonify({"Error": "An error occurred while sending the email."}), 500

# ==============================================================================
# Main Execution
# ==============================================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
