import joblib
import numpy as np
import pandas as pd
from flask import Flask, render_template, request
from config.paths_config import MODEL_OUTPUT_PATH

app = Flask(__name__)

# ✅ Load model
model = joblib.load(MODEL_OUTPUT_PATH)

# ✅ Load feature order
feature_order = joblib.load("artifacts/models/features.pkl")


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # ✅ Collect form data
            input_data = {
                "lead_time": float(request.form.get("lead_time")),
                "no_of_special_requests": float(request.form.get("no_of_special_requests")),
                "avg_price_per_room": float(request.form.get("avg_price_per_room")),
                "arrival_month": float(request.form.get("arrival_month")),
                "arrival_date": float(request.form.get("arrival_date")),
                "market_segment_type": float(request.form.get("market_segment_type")),
                "no_of_week_nights": float(request.form.get("no_of_week_nights")),
                "no_of_weekend_nights": float(request.form.get("no_of_weekend_nights")),
                "type_of_meal_plan": float(request.form.get("type_of_meal_plan")),
                "room_type_reserved": float(request.form.get("room_type_reserved")),
            }

            # ✅ Convert to DataFrame
            input_df = pd.DataFrame([input_data])

            # ✅ Reorder columns EXACTLY like training
            input_df = input_df.reindex(columns=feature_order, fill_value=0)

            # ✅ Prediction
            prediction = model.predict(input_df)[0]

            result = "Booking Confirmed" if prediction == 1 else "Booking Cancelled"

            return render_template('index.html', prediction=result)

        except Exception as e:
            return render_template('index.html', prediction=f"Error: {str(e)}")

    return render_template("index.html", prediction=None)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)