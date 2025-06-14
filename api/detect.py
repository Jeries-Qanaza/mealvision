import base64, io, tempfile
from PIL import Image
from ultralytics import YOLO

# Load the model once when the function is initialized
model = YOLO("./src/assets/best8s.pt")

def handler(request):
    """
    Vercel Python Function
    POST /api/detect
    Accepts:
      • multipart/form-data  → request.files["image"]
      • JSON {"image": "dataURL"}
    Returns:
      • JSON {"labels": [...]}
    """
    if request.method != "POST":
        return {"statusCode": 405, "body": "Method Not Allowed"}

    # Decode incoming image (file upload or base64)
    if "image" in request.files:
        file = request.files["image"]
        image = Image.open(file.stream).convert("RGB")
    else:
        data = request.get_json()
        image_bytes = base64.b64decode(data["image"].split(",")[1])
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Run YOLO inference
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp:
        image.save(temp.name)
        results = model.predict(source=temp.name, conf=0.25)

    labels = [
        results[0].names[int(box.cls[0])]
        for box in results[0].boxes
    ]

    return {"statusCode": 200, "body": {"labels": labels}}
