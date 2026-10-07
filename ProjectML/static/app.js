// Preset clinical profiles
const PRESETS = {
    no_disease: {
        age: 53,
        sex: "1",
        cp: "0",
        trestbps: 140,
        chol: 203,
        fbs: "1",
        restecg: "0",
        thalach: 155,
        exang: "1",
        oldpeak: 3.1,
        slope: "0",
        ca: "0",
        thal: "3"
    },
    disease_patient: {
        age: 58,
        sex: "1",
        cp: "2",
        trestbps: 130,
        chol: 246,
        fbs: "0",
        restecg: "1",
        thalach: 152,
        exang: "0",
        oldpeak: 1.0,
        slope: "2",
        ca: "0",
        thal: "2"
    },
    borderline: {
        age: 52,
        sex: "1",
        cp: "0",
        trestbps: 125,
        chol: 212,
        fbs: "0",
        restecg: "1",
        thalach: 168,
        exang: "0",
        oldpeak: 1.0,
        slope: "2",
        ca: "2",
        thal: "3"
    },
    young_disease: {
        age: 34,
        sex: "0",
        cp: "1",
        trestbps: 118,
        chol: 210,
        fbs: "0",
        restecg: "1",
        thalach: 192,
        exang: "0",
        oldpeak: 0.7,
        slope: "2",
        ca: "0",
        thal: "2"
    }
};

// Populate form fields with a given preset
function loadPreset(presetKey) {
    const data = PRESETS[presetKey];
    if (!data) return;

    for (const [key, value] of Object.entries(data)) {
        const input = document.getElementById(key);
        if (input) {
            input.value = value;
            // Brief highlight effect
            input.style.transition = 'background-color 0.3s ease';
            input.style.backgroundColor = '#ecfdf5';
            setTimeout(() => {
                input.style.backgroundColor = '';
            }, 450);
        }
    }

    // Auto-trigger prediction for immediate interactive demonstration
    triggerPrediction();
}

// Reset form to blank state
function resetForm() {
    document.getElementById("patientForm").reset();
    document.getElementById("resultsPlaceholder").style.display = "block";
    document.getElementById("resultsContainer").style.display = "none";
}

// Extract form data into object
function getFormData() {
    return {
        age: parseFloat(document.getElementById("age").value),
        sex: parseInt(document.getElementById("sex").value),
        cp: parseInt(document.getElementById("cp").value),
        trestbps: parseFloat(document.getElementById("trestbps").value),
        chol: parseFloat(document.getElementById("chol").value),
        fbs: parseInt(document.getElementById("fbs").value),
        restecg: parseInt(document.getElementById("restecg").value),
        thalach: parseFloat(document.getElementById("thalach").value),
        exang: parseInt(document.getElementById("exang").value),
        oldpeak: parseFloat(document.getElementById("oldpeak").value),
        slope: parseInt(document.getElementById("slope").value),
        ca: parseInt(document.getElementById("ca").value),
        thal: parseInt(document.getElementById("thal").value),
        model: document.getElementById("modelSelect").value
    };
}

// Handle Form Submission
async function handleFormSubmit(e) {
    if (e) e.preventDefault();
    await triggerPrediction();
}

// Perform Prediction via API
async function triggerPrediction() {
    const submitBtn = document.getElementById("submitBtn");
    const originalBtnHtml = submitBtn.innerHTML;

    try {
        const payload = getFormData();

        // Basic client validation
        for (const [key, val] of Object.entries(payload)) {
            if (key !== 'model' && (isNaN(val) || val === null || val === undefined)) {
                alert(`Please enter a valid value for ${key}.`);
                return;
            }
        }

        // Show spinner / loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = `
            <svg class="spin" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle>
                <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"></path>
            </svg>
            <span>Analyzing Clinical Vitals...</span>
        `;

        const response = await fetch("/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (!result.success) {
            alert("Error in prediction: " + (result.error || "Unknown server error"));
            return;
        }

        renderPredictionResults(result);

    } catch (err) {
        console.error("Prediction error:", err);
        alert("Failed to connect to the prediction server. Please ensure the backend is running.");
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnHtml;
    }
}

// Render dynamic prediction outcome
function renderPredictionResults(data) {
    const placeholder = document.getElementById("resultsPlaceholder");
    const container = document.getElementById("resultsContainer");
    
    placeholder.style.display = "none";
    container.style.display = "flex";

    // 1. Banner & Status
    const banner = document.getElementById("resultBanner");
    const title = document.getElementById("resultTitle");
    const icon = document.getElementById("statusIcon");
    const modelTag = document.getElementById("activeModelTag");

    banner.className = `result-banner ${data.risk_class}`;
    title.textContent = data.prediction_label;
    modelTag.textContent = data.selected_model;

    if (data.prediction === 0) {
        // Safe / No disease
        icon.innerHTML = `
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
        `;
    } else {
        // High Risk / Disease Indicated
        icon.innerHTML = `
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
        `;
    }

    // 2. Probability & Progress Bar
    const probNumber = document.getElementById("probNumber");
    const progressBar = document.getElementById("progressBar");
    const prob = data.probability;

    probNumber.textContent = `${prob}%`;
    progressBar.style.width = `${prob}%`;

    if (prob < 35) {
        progressBar.style.backgroundColor = "var(--safe-green)";
    } else if (prob < 65) {
        progressBar.style.backgroundColor = "var(--warn-amber)";
    } else {
        progressBar.style.backgroundColor = "var(--danger-red)";
    }

    // 3. Clinical Guidance
    document.getElementById("guidanceText").textContent = data.guidance;

    // 4. Risk Factors Checklist
    const factorsList = document.getElementById("riskFactorsList");
    factorsList.innerHTML = "";

    if (data.risk_factors && data.risk_factors.length > 0) {
        data.risk_factors.forEach(f => {
            const li = document.createElement("li");
            li.className = `factor-item factor-${f.type}`;
            
            let iconSvg = '';
            if (f.type === 'good') {
                iconSvg = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
            } else if (f.type === 'warning') {
                iconSvg = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`;
            } else {
                iconSvg = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"></polygon><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`;
            }

            li.innerHTML = `<span>${iconSvg}</span><span>${f.text}</span>`;
            factorsList.appendChild(li);
        });
    }

    // 5. Multi-Model Breakdown Cards
    const modelsBreakdown = document.getElementById("modelsBreakdown");
    modelsBreakdown.innerHTML = "";

    for (const [name, info] of Object.entries(data.models_comparison)) {
        const isSelected = name === data.selected_model;
        const card = document.createElement("div");
        card.className = `model-card ${isSelected ? 'active-selected' : ''}`;
        
        const badgeColor = info.prediction === 1 ? '#dc2626' : '#16a34a';
        card.innerHTML = `
            <div class="mc-name" title="${name}">${name}</div>
            <div class="mc-pred" style="color: ${badgeColor};">${info.label}</div>
            <div class="mc-prob">Prob: <strong>${info.probability}%</strong></div>
        `;
        modelsBreakdown.appendChild(card);
    }

    // Consensus footer
    document.getElementById("consensusSummary").textContent = 
        `Ensemble Consensus: ${data.consensus.agreeing_models} (${data.consensus.label})`;

    // Mobile scroll smoothly into view
    if (window.innerWidth <= 1024) {
        container.scrollIntoView({ behavior: "smooth", block: "start" });
    }
}

// Initial load: populate with negative sample on first visit
window.addEventListener("DOMContentLoaded", () => {
    loadPreset("no_disease");
});
