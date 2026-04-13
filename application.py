import os
import joblib
import numpy as np
from flask import Flask, render_template, request

app = Flask(__name__)

# =========================
# Load model + features
# =========================
MODEL_PATH = os.path.join("artifacts", "models", "lgbm_model.pkl")
FEATURE_PATH = os.path.join("artifacts", "models", "features.pkl")

model = joblib.load(MODEL_PATH)
features = joblib.load(FEATURE_PATH)

@app.route("/", methods=["GET", "POST"])
def index():

    prediction = None

    if request.method == "POST":
        try:
            # =========================
            # INPUT FROM UI (must match training order)
            # =========================
            lead_time = int(request.form["lead_time"])
            no_of_special_request = int(request.form["no_of_special_request"])
            avg_price_per_room = float(request.form["avg_price_per_room"])
            arrival_month = int(request.form["arrival_month"])
            arrival_date = int(request.form["arrival_date"])
            market_segment_type = int(request.form["market_segment_type"])
            no_of_week_nights = int(request.form["no_of_week_nights"])
            no_of_weekend_nights = int(request.form["no_of_weekend_nights"])
            type_of_meal_plan = int(request.form["type_of_meal_plan"])
            room_type_reserved = int(request.form["room_type_reserved"])

            # =========================
            # IMPORTANT: ORDER MUST MATCH TRAINING FEATURES
            # =========================
            input_data = np.array([[
                lead_time,
                no_of_special_request,
                avg_price_per_room,
                arrival_month,
                arrival_date,
                market_segment_type,
                no_of_week_nights,
                no_of_weekend_nights,
                type_of_meal_plan,
                room_type_reserved
            ]])

            prediction = model.predict(input_data)[0]

        except Exception as e:
            prediction = f"Error: {str(e)}"

    return render_template("index.html", prediction=prediction)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
