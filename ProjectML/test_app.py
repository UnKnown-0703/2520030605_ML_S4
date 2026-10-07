import json
from app import app, PRESETS

def test_endpoints():
    client = app.test_client()

    # 1. Test Home page
    res = client.get("/")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert b"CardioPredict" in res.data
    print("Test 1: Home page (GET /) passed.")

    # 2. Test Presets endpoint
    res = client.get("/presets")
    assert res.status_code == 200
    presets = res.get_json()
    assert "no_disease" in presets and "disease_patient" in presets
    print("Test 2: Presets (GET /presets) passed.")

    # 3. Test Metrics endpoint
    res = client.get("/metrics")
    assert res.status_code == 200
    metrics = res.get_json()
    assert "Logistic Regression" in metrics and "Support Vector Machine (SVM)" in metrics
    print("Test 3: Metrics (GET /metrics) passed.")

    # 4. Test Predict endpoint with No Disease preset
    neg_payload = PRESETS["no_disease"].copy()
    neg_payload["model"] = "Support Vector Machine (SVM)"
    res = client.post("/predict", data=json.dumps(neg_payload), content_type="application/json")
    assert res.status_code == 200
    result_neg = res.get_json()
    assert result_neg["success"] is True
    print(f"Test 4 (No Disease Sample): Pred={result_neg['prediction']} ({result_neg['prediction_label']}), Prob={result_neg['probability']}%, Risk={result_neg['risk_category']}")
    assert result_neg["prediction"] == 0, "Expected No Heart Disease (0)"

    # 5. Test Predict endpoint with Heart Disease preset
    pos_payload = PRESETS["disease_patient"].copy()
    pos_payload["model"] = "Support Vector Machine (SVM)"
    res = client.post("/predict", data=json.dumps(pos_payload), content_type="application/json")
    assert res.status_code == 200
    result_pos = res.get_json()
    assert result_pos["success"] is True
    print(f"Test 5 (Heart Disease Sample): Pred={result_pos['prediction']} ({result_pos['prediction_label']}), Prob={result_pos['probability']}%, Risk={result_pos['risk_category']}")
    assert result_pos["prediction"] == 1, "Expected Heart Disease (1)"

    # 6. Test with Logistic Regression
    lr_payload = PRESETS["disease_patient"].copy()
    lr_payload["model"] = "Logistic Regression"
    res = client.post("/predict", data=json.dumps(lr_payload), content_type="application/json")
    assert res.status_code == 200
    result_lr = res.get_json()
    print(f"Test 6 (Logistic Regression): Pred={result_lr['prediction']}, Prob={result_lr['probability']}%")
    assert result_lr["prediction"] == 1

    # 7. Test with KNN
    knn_payload = PRESETS["no_disease"].copy()
    knn_payload["model"] = "K-Nearest Neighbors (KNN)"
    res = client.post("/predict", data=json.dumps(knn_payload), content_type="application/json")
    assert res.status_code == 200
    result_knn = res.get_json()
    print(f"Test 7 (KNN): Pred={result_knn['prediction']}, Prob={result_knn['probability']}%")
    assert result_knn["prediction"] == 0

    print("\n==========================================")
    print("ALL AUTOMATED TESTS PASSED SUCCESSFULLY! [OK]")
    print("==========================================")

if __name__ == "__main__":
    test_endpoints()
