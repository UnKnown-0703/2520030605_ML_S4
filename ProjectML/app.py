import os
import joblib
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

MODEL_FILE = os.path.join(os.path.dirname(__file__), "heart_models.joblib")

# Ensure models are loaded
if not os.path.exists(MODEL_FILE):
    import train_models
    train_models.train_and_save_models()

saved_data = joblib.load(MODEL_FILE)
models = saved_data["models"]
metrics = saved_data["metrics"]
feature_names = saved_data["feature_names"]

# Presets for 1-click patient testing
PRESETS = {
    "no_disease": {
        "title": "No Heart Disease Profile (Row #1)",
        "age": 53,
        "sex": 1,          # Male
        "cp": 0,           # Typical angina
        "trestbps": 140,   # Resting BP
        "chol": 203,       # Serum cholesterol
        "fbs": 1,          # Fasting sugar > 120
        "restecg": 0,      # Normal ECG
        "thalach": 155,    # Max heart rate
        "exang": 1,        # Exercise induced angina
        "oldpeak": 3.1,    # ST depression
        "slope": 0,        # Upsloping
        "ca": 0,           # 0 vessels
        "thal": 3          # Reversible defect
    },
    "disease_patient": {
        "title": "Heart Disease Profile (Notebook Patient)",
        "age": 58,
        "sex": 1,          # Male
        "cp": 2,           # Non-anginal pain
        "trestbps": 130,   # Blood pressure
        "chol": 246,       # Cholesterol
        "fbs": 0,          # Normal sugar
        "restecg": 1,      # ST-T wave abnormality
        "thalach": 152,    # Max heart rate
        "exang": 0,        # No exercise angina
        "oldpeak": 1.0,    # ST depression
        "slope": 2,        # Downsloping
        "ca": 0,           # 0 vessels
        "thal": 2          # Thalassemia 2
    },
    "borderline": {
        "title": "Patient Record #0 (No Disease)",
        "age": 52,
        "sex": 1,
        "cp": 0,
        "trestbps": 125,
        "chol": 212,
        "fbs": 0,
        "restecg": 1,
        "thalach": 168,
        "exang": 0,
        "oldpeak": 1.0,
        "slope": 2,
        "ca": 2,
        "thal": 3
    },
    "young_disease": {
        "title": "Young Patient (Heart Disease Present)",
        "age": 34,
        "sex": 0,          # Female
        "cp": 1,           # Atypical angina
        "trestbps": 118,   # Normal BP
        "chol": 210,       # 210 mg/dL
        "fbs": 0,          # Normal sugar
        "restecg": 1,      # ST-T abnormality
        "thalach": 192,    # High max HR
        "exang": 0,        # No exercise angina
        "oldpeak": 0.7,    # Low ST depression
        "slope": 2,        # Downsloping
        "ca": 0,           # 0 vessels
        "thal": 2          # Thalassemia 2
    }
}

def analyze_risk_factors(data):
    """Generate medical risk factor observations based on entered patient parameters."""
    factors = []

    # Age & Gender
    age = float(data.get("age", 0))
    sex = int(data.get("sex", 0))
    if age >= 55:
        factors.append({"type": "warning", "text": f"Age {int(age)}: Increased cardiovascular vulnerability (age >= 55)."})

    # Blood Pressure (AHA Guidelines)
    bp = float(data.get("trestbps", 0))
    if bp >= 140:
        factors.append({"type": "danger", "text": f"Resting Blood Pressure ({int(bp)} mm Hg): Stage 2 Hypertension detected."})
    elif bp >= 130:
        factors.append({"type": "warning", "text": f"Resting Blood Pressure ({int(bp)} mm Hg): Stage 1 Hypertension."})
    else:
        factors.append({"type": "good", "text": f"Resting Blood Pressure ({int(bp)} mm Hg): Within normal limits (<120-129 mm Hg)."})

    # Cholesterol
    chol = float(data.get("chol", 0))
    if chol >= 240:
        factors.append({"type": "danger", "text": f"Serum Cholesterol ({int(chol)} mg/dL): High risk hypercholesterolemia (>=240 mg/dL)."})
    elif chol >= 200:
        factors.append({"type": "warning", "text": f"Serum Cholesterol ({int(chol)} mg/dL): Borderline high level."})
    else:
        factors.append({"type": "good", "text": f"Serum Cholesterol ({int(chol)} mg/dL): Optimal range (<200 mg/dL)."})

    # Fasting Sugar
    fbs = int(data.get("fbs", 0))
    if fbs == 1:
        factors.append({"type": "warning", "text": "Fasting Blood Sugar > 120 mg/dL: Elevated blood glucose / diabetic indicator."})

    # Angina & Chest Pain
    exang = int(data.get("exang", 0))
    if exang == 1:
        factors.append({"type": "danger", "text": "Exercise-Induced Angina: Patient experiences cardiac chest pain during exertion."})

    # ST Depression (oldpeak)
    oldpeak = float(data.get("oldpeak", 0.0))
    if oldpeak >= 2.0:
        factors.append({"type": "danger", "text": f"ST Depression ({oldpeak:.1f} mm): Severe myocardial ischemia indicator."})
    elif oldpeak >= 1.0:
        factors.append({"type": "warning", "text": f"ST Depression ({oldpeak:.1f} mm): Moderate ST segment change detected."})

    # Fluoroscopy vessels
    ca = int(data.get("ca", 0))
    if ca > 0:
        factors.append({"type": "danger", "text": f"Fluoroscopy: {ca} major cardiac vessels showing narrowing/calcification."})

    # Thalassemia
    thal = int(data.get("thal", 2))
    if thal == 3:
        factors.append({"type": "warning", "text": "Thalassemia: Reversible perfusion defect noted on cardiac scan."})
    elif thal == 1:
        factors.append({"type": "warning", "text": "Thalassemia: Fixed defect observed."})

    return factors

@app.route("/")
def home():
    return render_template("index.html", metrics=metrics)

@app.route("/presets", methods=["GET"])
def get_presets():
    return jsonify(PRESETS)

@app.route("/metrics", methods=["GET"])
def get_metrics():
    return jsonify(metrics)

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"success": False, "error": "No input patient data provided"}), 400

        # Extract features in required order
        try:
            features = {
                "age": float(data["age"]),
                "sex": int(data["sex"]),
                "cp": int(data["cp"]),
                "trestbps": float(data["trestbps"]),
                "chol": float(data["chol"]),
                "fbs": int(data["fbs"]),
                "restecg": int(data["restecg"]),
                "thalach": float(data["thalach"]),
                "exang": int(data["exang"]),
                "oldpeak": float(data["oldpeak"]),
                "slope": int(data["slope"]),
                "ca": int(data["ca"]),
                "thal": int(data["thal"])
            }
        except KeyError as ke:
            return jsonify({"success": False, "error": f"Missing clinical parameter: {str(ke)}"}), 400
        except ValueError as ve:
            return jsonify({"success": False, "error": f"Invalid numerical format: {str(ve)}"}), 400

        input_df = pd.DataFrame([features], columns=feature_names)

        chosen_model_name = data.get("model", "Support Vector Machine (SVM)")
        if chosen_model_name not in models:
            chosen_model_name = "Support Vector Machine (SVM)"

        # Run primary model
        primary_model = models[chosen_model_name]
        primary_pred = int(primary_model.predict(input_df)[0])
        primary_prob = float(primary_model.predict_proba(input_df)[0, 1])

        # Run all models for multi-model consensus
        all_results = {}
        votes = []
        for name, pipe in models.items():
            pred = int(pipe.predict(input_df)[0])
            prob = float(pipe.predict_proba(input_df)[0, 1])
            votes.append(pred)
            all_results[name] = {
                "prediction": pred,
                "label": "Heart Disease" if pred == 1 else "No Disease",
                "probability": round(prob * 100, 1),
                "accuracy": metrics[name]["accuracy"]
            }

        # Consensus score
        consensus_score = sum(votes) / len(votes)
        consensus_label = "Heart Disease Likely" if consensus_score >= 0.5 else "Heart Disease Unlikely"

        # Risk categorization based on probability
        if primary_prob < 0.35:
            risk_category = "Low Risk"
            risk_class = "risk-low"
            guidance = "Patient clinical indicators currently show low probability of cardiovascular disease. Maintain regular physical activity, balanced diet, and periodic health checkups."
        elif primary_prob < 0.65:
            risk_category = "Moderate Risk"
            risk_class = "risk-moderate"
            guidance = "Patient exhibits intermediate cardiovascular risk markers. Consult a cardiologist for an in-depth cardiac stress echocardiogram and dietary modifications."
        else:
            risk_category = "High Risk"
            risk_class = "risk-high"
            guidance = "Significant clinical markers associated with heart disease detected. Immediate medical consultation with a cardiologist is strongly recommended for diagnostic angiogram and targeted therapy."

        # Risk factor highlights
        risk_factors = analyze_risk_factors(features)

        response = {
            "success": True,
            "selected_model": chosen_model_name,
            "prediction": primary_pred,
            "prediction_label": "Heart Disease Indicated" if primary_pred == 1 else "No Heart Disease Detected",
            "probability": round(primary_prob * 100, 1),
            "risk_category": risk_category,
            "risk_class": risk_class,
            "guidance": guidance,
            "risk_factors": risk_factors,
            "models_comparison": all_results,
            "consensus": {
                "label": consensus_label,
                "score_percent": round(consensus_score * 100, 1),
                "agreeing_models": f"{sum(votes)} of {len(votes)} models predict presence of disease"
            }
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    print("Starting Heart Disease Prediction Server on http://127.0.0.1:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=True)
