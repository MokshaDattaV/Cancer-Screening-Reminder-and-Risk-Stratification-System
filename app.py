from flask import Flask, render_template, request, redirect, url_for
import joblib
import csv
import os
from datetime import datetime
import pandas as pd

app = Flask(__name__)
model = joblib.load("model.pkl")
log_file = "prediction_log.csv"

# Create CSV log file with header if not exists
if not os.path.exists(log_file):
    with open(log_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            "Timestamp", "Age", "Sex", "Smoking", "Alcohol", "Exercise", "Family", "BMI", "Diet", "Chemo",
            "Cancer", "Breast", "Cervix", "Colorectal", "Urgency"
        ])

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            input_data = [float(request.form[f"f{i}"]) for i in range(1, 10)]
            age, sex, smoking, alcohol, exercise, family, bmi, diet, chemo = input_data

            prediction = model.predict_proba([input_data])[0][1] * 100
            breast = cervix = colorectal = 0

            if sex == 0:  # Female
    # Breast cancer: mild effect from family and BMI
                breast = prediction + 0.1 * prediction * family + 0.05 * prediction * (bmi > 25)
    # Cervical cancer: modest increase with age and diet
                cervix = prediction + 0.08 * prediction * (age > 30) + 0.1 * prediction * (diet == 0)
            else:
                    breast = cervix = 0  # Not applicable to males

# Colorectal cancer: affects both sexes
            colorectal = prediction
            colorectal += 0.05 * prediction * (age > 50)
            colorectal += 0.05 * prediction * (smoking + alcohol)
            colorectal += 0.05 * prediction * (bmi > 25)

            result = {
            "cancer": round(min(prediction, 100), 2),
            "breast": round(min(breast, 100), 2),
            "cervix": round(min(cervix, 100), 2),
            "colorectal": round(min(colorectal, 100), 2)
        }


            urgency = "Low"
            if any(p > 90 for p in [prediction, breast, cervix, colorectal]):
                urgency = "Very Urgent"
            elif any(p > 60 for p in [prediction, breast, cervix, colorectal]):
                urgency = "Urgent"
            elif any(p > 30 for p in [prediction, breast, cervix, colorectal]):
                urgency = "High Risk"

            # Log prediction
            with open(log_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    age, sex, smoking, alcohol, exercise, family, bmi, diet, chemo,
                    round(prediction, 2), round(breast, 2), round(cervix, 2), round(colorectal, 2), urgency
                ])

            result = {
                "cancer": round(prediction, 2),
                "breast": round(breast, 2),
                "cervix": round(cervix, 2),
                "colorectal": round(colorectal, 2),
                "urgency": urgency
            }

            return render_template("index.html", result=result)

        except Exception as e:
            return render_template("index.html", error=str(e))

    return render_template("index.html")

@app.route("/calendar")
def calendar():
    return render_template("calendar.html")

@app.route("/logs")
def logs():
    try:
        df = pd.read_csv(log_file)
        records = df.to_dict(orient='records')
        return render_template("logs.html", records=records)
    except Exception as e:
        return f"Error loading logs: {e}"

if __name__ == "__main__":
    app.run(debug=True)
