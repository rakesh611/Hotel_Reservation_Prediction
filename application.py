import os
import joblib
import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)

# =========================
# Correct paths (IMPORTANT FIX)
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "artifacts", "models", "lgbm_model.pkl")
FEATURE_PATH = os.path.join(BASE_DIR, "artifacts", "models", "features.pkl")

# Load model + features
model = joblib.load(MODEL_PATH)
features = joblib.load(FEATURE_PATH)

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None

    if request.method == "POST":
        input_data = {
            "lead_time": int(request.form["lead_time"]),
            "no_of_special_request": int(request.form["no_of_special_request"]),
            "avg_price_per_room": float(request.form["avg_price_per_room"]),
            "arrival_month": int(request.form["arrival_month"]),
            "arrival_date": int(request.form["arrival_date"]),
            "market_segment_type": int(request.form["market_segment_type"]),
            "no_of_week_nights": int(request.form["no_of_week_nights"]),
            "no_of_weekend_nights": int(request.form["no_of_weekend_nights"]),
            "type_of_meal_plan": int(request.form["type_of_meal_plan"]),
            "room_type_reserved": int(request.form["room_type_reserved"]),
        }

        df = pd.DataFrame([input_data])

        # enforce training feature order (CRITICAL FIX)
        df = df[features]

        pred = model.predict(df)[0]

        prediction = "Booking Confirmed" if pred == 1 else "Cancelled"

    return render_template("index.html", prediction=prediction)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
