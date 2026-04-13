import joblib
import numpy as np
import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)

# Load model + feature order
model = joblib.load("model.pkl")
feature_columns = joblib.load("features.pkl")

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None

    if request.method == "POST":
        try:
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

            # Convert to DataFrame (CRITICAL FIX)
            input_df = pd.DataFrame([input_data])

            # Ensure column order matches training
            input_df = input_df[feature_columns]

            pred = model.predict(input_df)[0]

            prediction = "Booking Confirmed" if pred == 1 else "Cancelled"

        except Exception as e:
            prediction = f"Error: {str(e)}"

    return render_template("index.html", prediction=prediction)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
