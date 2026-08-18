"""브라우저 캔버스에 그린 숫자를 학습된 모델로 인식하는 Flask 웹 앱."""
import base64
import io
import os

import joblib
import numpy as np
from flask import Flask, jsonify, render_template, request
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

app = Flask(__name__)

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        "model.pkl 파일을 찾을 수 없습니다. 먼저 train_model.py를 실행해서 모델을 학습시켜 주세요."
    )

model = joblib.load(MODEL_PATH)


def preprocess(image: Image.Image) -> np.ndarray:
    """캔버스에서 받은 이미지(검정 배경/흰 선)를 MNIST와 같은 28x28 벡터로 변환한다."""
    bbox = image.getbbox()
    if bbox is None:
        return None

    cropped = image.crop(bbox)
    size = max(cropped.size)
    padded = Image.new("L", (size, size), color=0)
    padded.paste(cropped, ((size - cropped.width) // 2, (size - cropped.height) // 2))

    margin = size // 5
    padded_with_margin = Image.new("L", (size + margin * 2, size + margin * 2), color=0)
    padded_with_margin.paste(padded, (margin, margin))

    small = padded_with_margin.resize((28, 28), Image.LANCZOS)

    arr = np.array(small, dtype=np.float32) / 255.0
    return arr.reshape(1, -1)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}
    data_url = data.get("image", "")
    if "," not in data_url:
        return jsonify({"error": "이미지 데이터가 없습니다."}), 400

    header, encoded = data_url.split(",", 1)
    png_bytes = base64.b64decode(encoded)
    image = Image.open(io.BytesIO(png_bytes)).convert("L")

    flat = preprocess(image)
    if flat is None:
        return jsonify({"error": "먼저 숫자를 그려주세요."}), 400

    pred = int(model.predict(flat)[0])
    confidence = None
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(flat)[0]
        confidence = round(float(proba[pred]) * 100, 1)

    return jsonify({"digit": pred, "confidence": confidence})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
