from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import json
import requests
import base64
from flask_mail import Mail, Message
from ultralytics import YOLO
import numpy as np
import io
from PIL import Image
import os

# ------------------- Flask Setup -------------------
app = Flask(__name__)
CORS(app, origins=["https://mealvision.vercel.app"])

@app.route('/')
def index():
    return 'MealVision Backend is Running!'

# ------------------- Gemini AI Setup -------------------
genai.configure(api_key="AIzaSyA8euO3ZFVejMJ_e2_I3YqwYlzQsh6Un6Q") 
model = genai.GenerativeModel("gemini-1.5-flash")

# ------------------- Stability AI -------------------
STABILITY_API_KEY = "YOUR_STABILITY_API_KEY"  # <- Replace with env var

def generate_image(prompt):
    response = requests.post(
        "https://api.stability.ai/v2beta/stable-image/generate/core",
        headers={
            "authorization": f"Bearer {STABILITY_API_KEY}",
            "accept": "image/*"
        },
        files={"none": ''},
        data={
            "prompt": prompt,
            "output_format": "jpeg",
        },
    )
    if response.status_code == 200:
        return base64.b64encode(response.content).decode("utf-8")
    else:
        raise Exception(str(response.json()))

@app.route("/generate-meals", methods=["POST"])
def generate_meals():
    try:
        data = request.json
        ingredients = data.get("ingredients", [])
        ingredients_str = ", ".join(ingredients)

        prompt = f"What meal can I make with these ingredients: {ingredients_str}? Answer in JSON format with at least 3 options including meal names and steps."
        response = model.generate_content(prompt)
        json_text = response.text.strip()

        if json_text.startswith("```json"):
            json_text = json_text[7:]
        if json_text.endswith("```"):
            json_text = json_text[:-3]

        meal_data = json.loads(json_text)

        for meal in meal_data["meals"]:
            meal_name = meal["mealName"]
            steps = "\n".join(meal["steps"])
            image_prompt = f"A delicious meal of {meal_name}. Steps: {steps}"
            try:
                meal["image"] = generate_image(image_prompt)
            except Exception as e:
                meal["image"] = None
                print(f"Failed to generate image for {meal_name}: {str(e)}")

        return jsonify({"meals_res": meal_data["meals"]})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------- Email Setup -------------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jeries.testing@gmail.com'
app.config['MAIL_PASSWORD'] = 'usvc fiza bxyk dcwf'
app.config['MAIL_DEFAULT_SENDER'] = 'je.yo.yvc@gmail.com'

mail = Mail(app)

@app.route('/send-email', methods=['POST'])
def send_email():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    msg = Message(subject=f"New Contact Message from {name}",
                  recipients=['je.yo.yvc@gmail.com'],
                  body=f"From: {name}\nEmail: {email}\n\nMessage:\n{message}")

    try:
        mail.send(msg)
        return jsonify({"message": "Email sent successfully"}), 200
    except Exception as e:
        print("Error sending email:", e)
        return jsonify({"error": str(e)}), 500

# ------------------- YOLO Detection -------------------
yolo_model = YOLO("./src/assets/best.pt")

@app.route("/detect", methods=["POST"])
def detect():
    data = request.get_json()
    image_data = data["image"].split(",")[1]
    image_bytes = base64.b64decode(image_data)
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_np = np.array(image)

    results = yolo_model(image_np)
    labels = []

    for result in results:
        for box in result.boxes:
            label = yolo_model.names[int(box.cls[0])]
            labels.append(label)

    return jsonify({"labels": labels})

# ------------------- Run App -------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
