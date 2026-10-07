import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)

DATA_PATH = os.path.join(os.path.dirname(__file__), "heart.csv")
MODEL_SAVE_PATH = os.path.join(os.path.dirname(__file__), "heart_models.joblib")

def train_and_save_models():
    print(f"Loading dataset from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} rows with columns: {list(df.columns)}")

    X = df.drop(columns=["target"])
    y = df["target"]

    # Stratified 80/20 train/test split matching project report
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    models_config = {
        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(penalty="l2", C=1.0, max_iter=1000, random_state=42))
        ]),
        "Support Vector Machine (SVM)": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", SVC(kernel="rbf", C=1.0, probability=True, random_state=42))
        ]),
        "K-Nearest Neighbors (KNN)": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", KNeighborsClassifier(n_neighbors=5, weights="distance"))
        ])
    }

    trained_models = {}
    metrics = {}

    for name, pipeline in models_config.items():
        print(f"\nTraining {name}...")
        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)
        y_prob = pipeline.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)
        cm = confusion_matrix(y_test, y_pred).tolist()

        metrics[name] = {
            "accuracy": round(float(acc) * 100, 2),
            "precision": round(float(prec) * 100, 2),
            "recall": round(float(rec) * 100, 2),
            "f1_score": round(float(f1) * 100, 2),
            "roc_auc": round(float(auc) * 100, 2),
            "confusion_matrix": cm
        }
        trained_models[name] = pipeline

        print(f"  Accuracy:  {metrics[name]['accuracy']}%")
        print(f"  Precision: {metrics[name]['precision']}%")
        print(f"  Recall:    {metrics[name]['recall']}%")
        print(f"  F1 Score:  {metrics[name]['f1_score']}%")
        print(f"  ROC-AUC:   {metrics[name]['roc_auc']}%")

    payload = {
        "models": trained_models,
        "metrics": metrics,
        "feature_names": list(X.columns),
        "target_names": ["No Heart Disease", "Heart Disease Detected"]
    }

    joblib.dump(payload, MODEL_SAVE_PATH)
    print(f"\nSaved all models and metrics successfully to {MODEL_SAVE_PATH}!")

if __name__ == "__main__":
    train_and_save_models()
