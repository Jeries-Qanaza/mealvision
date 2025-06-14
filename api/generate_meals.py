import json, base64, requests
from flask import Request  # type hint for editors
import google.generativeai as genai

# Initialize Gemini
genai.configure(api_key="AIzaSyA8euO3ZFVejMJ_e2_I3YqwYlzQsh6Un6Q")      # move to env later
model = genai.GenerativeModel("gemini-1.5-flash")

STABILITY_API_KEY = "YOUR_STABILITY_API_KEY"        # move to env later

def _generate_image(prompt: str) -> str | None:
    """Call Stability AI and return base64-encoded jpeg (or None on error)."""
    res = requests.post(
        "https://api.stability.ai/v2beta/stable-image/generate/core",
        headers={
            "authorization": f"Bearer {STABILITY_API_KEY}",
            "accept": "image/*"
        },
        data={"prompt": prompt, "output_format": "jpeg"},
        files={"none": ''}
    )
    return base64.b64encode(res.content).decode() if res.status_code == 200 else None

def handler(request: "Request"):
    """POST /api/generate_meals  →  JSON with generated meals."""
    if request.method != "POST":
        return {"statusCode": 405, "body": "Method Not Allowed"}

    data = request.get_json() or {}
    ingredients = ", ".join(data.get("ingredients", []))
    prefs       = data.get("dietary_preferences", "")

    prompt = (
        f"What meal can I make with: {ingredients} "
        f"given these dietary preferences: {prefs}. "
        "Return JSON with key 'meals' and at least 3 meal objects "
        "(mealName, steps)."
    )

    try:
        raw = model.generate_content(prompt).text.strip()
        # Remove ```json fences if present
        if raw.startswith("```json"): raw = raw[7:]
        if raw.endswith("```"):       raw = raw[:-3]
        meals = json.loads(raw)["meals"]

        # Add images
        for meal in meals:
            name  = meal.get("mealName") or meal.get("name")
            steps = "\n".join(meal["steps"])
            prompt_img = f"A delicious meal of {name}. Steps: {steps}"
            meal["image"] = _generate_image(prompt_img)

        return {"statusCode": 200, "body": {"meals_res": meals}}

    except Exception as exc:
        return {"statusCode": 500, "body": {"error": str(exc)}}
