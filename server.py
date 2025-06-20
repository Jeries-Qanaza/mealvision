from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import json
import requests
import base64
from flask_mail import Mail, Message
from ultralytics import YOLO
import io
from PIL import Image
import tempfile
import os
import torch
import gc                       # garbage collection
from dotenv import load_dotenv  # load .env variables

# ------------------- Load environment variables -------------------
load_dotenv()

# ------------------- Limit model threads --------------------------
torch.set_num_threads(1)
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

# ------------------- Flask Setup ----------------------------------
app = Flask(__name__)
CORS(
    app,
    resources={
        r"/*": {
            "origins": ["*", "https://mealvision.vercel.app"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    },
)

# ------------------- AI Setup ------------------------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
Gmodel = genai.GenerativeModel("gemini-1.5-flash")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")

# ------------------- generate_image  ---------------------------------
def generate_image(prompt: str) -> str | None:
    """Call Stability API and return base-64 image string (or raise error)."""
    response = requests.post(
        "https://api.stability.ai/v2beta/stable-image/generate/core",
        headers={
            "authorization": f"Bearer {STABILITY_API_KEY}",
            "accept": "image/*",
        },
        files={"none": ""},
        data={
            "prompt": prompt,
            "output_format": "jpeg",
        },
    )
    if response.status_code == 200:
        return base64.b64encode(response.content).decode("utf-8")
    raise Exception(str(response.json()))


# ------------------- /generate-meals ------------------------------
@app.route("/generate-meals", methods=["POST", "OPTIONS"])
def generate_meals():
    # CORS pre-flight
    if request.method == "OPTIONS":
        resp = jsonify({})
        resp.headers.add("Access-Control-Allow-Origin", "*")
        resp.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        resp.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        return resp

    # --- random salt so Gemini returns different meals each call ---
    salt = os.urandom(4).hex()   # 8-character hex string

    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        ingredients_str = ", ".join(data.get("ingredients", []))
        dietary_preferences = data.get("dietary_preferences", "")

        prompt = (
            f"What meal can I make with these ingredients: {ingredients_str}, "
            f"considering the following dietary preferences: {dietary_preferences}. "
            f"Give completely different options than any previous answer. id={salt}. "
            "Answer in JSON format with at least 3 options including meal names and steps."
        )

        gemini_resp = Gmodel.generate_content(prompt)
        json_text = gemini_resp.text.strip()

        # strip ```json fences if present
        if json_text.startswith("```json"):
            json_text = json_text[7:]
        if json_text.endswith("```"):
            json_text = json_text[:-3]

        meal_data = json.loads(json_text)

        # ---------- ensure key "meals" exists and is a list ----------
        meals_list = meal_data.get("meals")
        if not isinstance(meals_list, list):
            # unexpected format – return 400
            return jsonify({"error": "AI response format error"}), 400
        # --------------------------------------------------------------------

        for meal in meals_list:
            meal_name = meal.get("mealName") or meal.get("name")
            meal["mealName"] = meal_name  # ensure title always

            steps = "\n".join(meal["steps"])
            img_prompt = f"A delicious meal of {meal_name}. Steps: {steps}"
            try:
                meal["image"] = generate_image(img_prompt)
            except Exception:
                meal["image"] = None

        return jsonify({"meals_res": meals_list})

    except Exception as e:
        print("Error in generate_meals:", e)
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ------------------- Email Setup ----------------------------------
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")

mail = Mail(app)

@app.route("/send-email", methods=["POST"])
def send_email():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    msg = Message(
        subject=f"New Contact Message from {name}",
        recipients=["je.yo.yvc@gmail.com"],
        body=f"From: {name}\nEmail: {email}\n\nMessage:\n{message}",
    )

    try:
        mail.send(msg)
        return jsonify({"message": "Email sent successfully"}), 200
    except Exception as e:
        print("Error sending email:", e)
        return jsonify({"error": str(e)}), 500

# ------------------- YOLO Detection (Lazy Loading) ----------------
yolo_model = None

def get_yolo_model():
    """Load YOLO weights once on first request."""
    global yolo_model
    if yolo_model is None:
        print("Loading YOLO model...")
        yolo_model = YOLO("./src/assets/best8s.pt")
        print("YOLO model loaded successfully")
    return yolo_model


@app.route("/detect", methods=["POST"])
def detect():
    try:
        # read image from request (FormData or Base64)
        if "image" in request.files:
            file = request.files["image"]
            image = Image.open(file.stream).convert("RGB")
        else:
            data = request.get_json()
            image_data = data["image"].split(",")[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        model = get_yolo_model()

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp:
            image.save(temp.name)
            results = model.predict(source=temp.name, conf=0.25)
            image.close()

            # attempt to delete temp file; ignore Windows lock error
            try:
                os.unlink(temp.name)
            except PermissionError:
                # file is still locked; Windows will clean temp dir later
                pass

        labels = []
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            label = results[0].names[cls_id]
            labels.append(label)

        del results
        gc.collect()

        return jsonify({"labels": labels})

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ------------------- Health Check ---------------------------------
@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "Server is running!", "message": "API is healthy"})


# ------------------- Run App --------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)