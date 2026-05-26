import os
from ultralytics import YOLO

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Prefer the custom face model; fall back to the standard YOLOv8n if not found.
_FACE_MODEL_PATH = os.path.join(BASE_DIR, "saved_models", "yolov8n-face.pt")
if os.path.exists(_FACE_MODEL_PATH):
    MODEL_PATH = _FACE_MODEL_PATH
else:
    MODEL_PATH = "yolov8n.pt"   # ultralytics auto-downloads this on first run

model = YOLO(MODEL_PATH)

def detect_faces(frame):
    results = model(frame, conf=0.5, verbose=False)
    boxes_out = []

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            boxes_out.append((x1, y1, x2, y2))

    return boxes_out
