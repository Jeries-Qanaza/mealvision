# Apply gevent monkey patching at the very top to prevent conflicts with libraries like torch
from gevent import monkey
monkey.patch_all()
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

        # Loop through each image and run prediction
        for image_path in test_image_paths:
            if not os.path.exists(image_path):
                print(f"!!! Health Check Error: Test image not found at path: {image_path}")
                return False # Fail the check if any image is missing

            # Run prediction with verbose=False to keep the main logs clean
            results = model.predict(source=image_path, imgsz=[640, 640], verbose=False)

            # Check for a valid result. If any prediction fails, the whole check fails.
            if not results or len(results) == 0:
                print(f"!!! Health Check Error: Model returned an invalid result for {image_path}")
                return False
        
        # If the loop completes without returning False, all checks passed.
        return True

    except Exception as e:
        print(f"!!! Health Check Error (YOLO): An exception occurred: {e} !!!")
        return False

# Gemini api check (of the genreate meals)
def check_gemini_health():
    """
    Sends a prompt to Gemini to check its health and API key.
    Returns True on success, False on failure.
    """
    try:
        # Simple prompt with a timeout
        response = Gmodel.generate_content(
            "Are you operational? Respond with only the word: ok", 
            request_options={'timeout': 15}
        )
        # Check if the expected word is in the response
        return "ok" in response.text.lower()
    except Exception as e:
        print(f"!!! Health Check Error (Gemini): {e} !!!")
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
            print("!!! Health Check Error (Hugging Face): Client not initialized, token might be missing.")
            return False
            
        url = f"https://huggingface.co/api/models/{model_id}"
        # Simple GET request to the model's API endpoint with a timeout
        response = requests.get(url, timeout=15)
        
        # Status 200 means the model exists and is accessible
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"!!! Health Check Error (Hugging Face): {e} !!!")
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
        print(f"!!! ERROR generating image for {meal.get('mealName')}: {img_e} !!!")
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
    # UptimeRobot and other services look for this status code to determine if the service is "up" or "down".
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
        print(f"!!! ERROR in /detect: {e} !!!")
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
            print(f"!!! FFmpeg ERROR: {e.stderr} !!!")
            return jsonify({"error": "Failed to process video with FFmpeg."}), 500

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

                # Run YOLO prediction on the (potentially resized) frame
                results = model.predict(source=frame_path, imgsz=[640, 640])
                frame_labels = {results[0].names[int(box.cls[0])] for box in results[0].boxes}
                all_detected_labels.update(frame_labels)
            except Exception as e:
                print(f"!!! Could not process frame {frame_filename}: {e} !!!")
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
            return jsonify({"Error": "No JSON data received"}), 400
            
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

        # --- Start of new image generation ---
        # Check if the Hugging Face client is configured
        if hf_client:
            # DEBUG: Check if this block is being entered
            print("DEBUG: Condition 'if hf_client' is TRUE. Entering image generation block.")

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
        # --- End of new image generation ---

        t_total_end = time.time()
        print(f"--- TOTAL GENERATE-MEALS TIME: {t_total_end - t_total_start:.2f} seconds ---")

        return jsonify({"meals_res": meal_data["meals"]})

    except Exception as e:
        print(f"!!! ERROR in /generate-meals: {e} !!!")
        traceback.print_exc()
        return jsonify({"Error": "An error occurred while generating meals."}), 500

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
