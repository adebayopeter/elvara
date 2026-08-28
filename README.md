# Elvara - Sepsis Risk Prediction System

**A clinical decision support system for early sepsis detection using machine learning, featuring real-time risk assessment and model monitoring.**

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-orange.svg)](https://scikit-learn.org/)

---

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/your-org/elvara.git
cd elvara

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Terminal 1: Start FastAPI backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start Streamlit frontend
streamlit run streamlit_app/app.py --server.port 8501
```

**Access:**
- **Streamlit UI:** http://localhost:8501
- **FastAPI Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Prometheus Metrics:** http://localhost:8000/metrics

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Model Information](#model-information)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Monitoring](#monitoring)
- [Testing](#testing)
- [License](#license)

---

## ✨ Features

- **Machine Learning Prediction** - HistGradientBoostingClassifier with 96% ROC-AUC
- **Multi-Observation Support** - Captures temporal patterns (2-3 vital sign observations)
- **Real-Time Risk Assessment** - Sepsis risk scores (0-100) with High/Moderate/Low categories
- **Clinical Decision Support** - Key risk factors highlighting for rapid triage
- **RESTful API** - FastAPI backend with automatic OpenAPI documentation
- **Interactive UI** - Streamlit-based clinical dashboard with calm, precise design
- **Model Monitoring** - Evidently AI for drift detection, Prometheus metrics
- **Production Ready** - Docker containerization, Render deployment blueprints
- **Feature Engineering** - Automated extraction of 46 temporal and static features
- **Health Checks** - Built-in endpoint monitoring for uptime tracking

---

## 🛠️ Tech Stack

**Backend:**
- Python 3.13
- FastAPI 0.100+
- Uvicorn (ASGI server)
- Pydantic 2.0+ (data validation)

**Machine Learning:**
- scikit-learn 1.3+ (HistGradientBoostingClassifier)
- pandas 2.0+ (data processing)
- numpy 1.24+ (numerical computing)
- joblib 1.3+ (model serialization)

**Frontend:**
- Streamlit 1.28+ (clinical UI)
- requests 2.31+ (HTTP client)

**Monitoring:**
- Prometheus Client 0.17+ (metrics)
- Evidently 0.4+ (ML monitoring, drift detection)
- matplotlib 3.7+ (visualization)
- seaborn 0.12+ (statistical plots)

**Deployment:**
- Docker & Docker Compose
- Render (cloud platform)
- Gunicorn 21.2+ (production WSGI)

**Testing:**
- pytest 7.4+
- httpx 0.24+ (async testing)

---

## 📁 Project Structure

```
elvara/
├── app/                           # FastAPI backend application
│   ├── main.py                   # FastAPI app, routes, CORS, lifespan
│   ├── schemas.py                # Pydantic models (request/response)
│   └── metrics.py                # Prometheus metrics definitions
├── src/                           # Core ML pipeline
│   ├── data_pipeline.py          # Data loading, cleaning, validation
│   ├── feature_engineering.py    # Feature extraction (vitals/labs)
│   ├── train.py                  # Model training, evaluation
│   └── predict.py                # SepsisPredictor class, inference
├── streamlit_app/                 # Streamlit frontend
│   └── app.py                    # Multi-observation clinical UI
├── models/                        # Trained model artifacts
│   ├── sepsis_model.joblib       # Trained HistGradientBoostingClassifier
│   └── model_metadata.json       # Model metrics, feature list
├── data/                          # Dataset storage
│   ├── raw/                      # Original CSV files (patients, vitals, labs, outcomes)
│   └── processed/                # Cleaned datasets, engineered features
├── monitoring/                    # ML monitoring & drift detection
│   ├── drift_monitor.py          # Evidently drift analysis
│   ├── prometheus.yml            # Prometheus scrape config
│   └── reports/                  # Generated drift reports (HTML)
├── docker/                        # Docker configuration
│   ├── Dockerfile.api            # FastAPI backend image
│   ├── Dockerfile.streamlit      # Streamlit frontend image
│   └── docker-compose.yml        # Local orchestration (API, Streamlit, Prometheus, Grafana)
├── notebooks/                     # Jupyter notebooks
│   ├── data_exploration.ipynb    # EDA, feature analysis
│   └── feature_engineering.ipynb # Feature development, testing
├── tests/                         # Test suite (empty, future)
├── .env.example                   # Environment variables template
├── .dockerignore                  # Docker build exclusions
├── requirements.txt               # Python dependencies
├── render.yaml                    # Render deployment blueprint
├── DEPLOYMENT.md                  # Deployment guide (local, Docker, Render)
└── README.md                      # This file
```

---

## 🔧 Installation

### Prerequisites

- Python 3.13+
- Docker Desktop (optional, for containerized deployment)
- Git

### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/elvara.git
cd elvara
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### Step 3: Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt
```

### Step 4: Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values (optional for local development)
nano .env  # or use your preferred editor
```

**Environment variables:**
```env
# FastAPI Backend
MODEL_PATH=models/sepsis_model.joblib
PYTHONUNBUFFERED=1

# Streamlit Frontend
FASTAPI_URL=http://localhost:8000

# Optional
LOG_LEVEL=INFO
```

### Step 5: Verify Model Exists

```bash
# Check model file
ls -lh models/sepsis_model.joblib

# Expected output: ~435KB file
# -rw-r--r--  1 user  staff   435K  sepsis_model.joblib
```

### Step 6: Start Services

**Option A: Native Python (Development)**

```bash
# Terminal 1: Start FastAPI backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start Streamlit frontend
streamlit run streamlit_app/app.py --server.port 8501
```

**Option B: Docker Compose (Production-like)**

```bash
cd docker
docker-compose up --build

# Services will start on:
# - Streamlit: http://localhost:8501
# - FastAPI: http://localhost:8000
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000
```

**Access Points:**
- **Streamlit UI:** http://localhost:8501 (clinical dashboard)
- **FastAPI Docs:** http://localhost:8000/docs (interactive API docs)
- **Health Check:** http://localhost:8000/health
- **Metrics:** http://localhost:8000/metrics (Prometheus format)

---

## ⚙️ Configuration

### Environment Variables

See `.env.example` for all available environment variables.

**Essential Variables:**

| Variable | Description | Default |
|----------|-------------|---------|
| `MODEL_PATH` | Path to trained model | `models/sepsis_model.joblib` |
| `FASTAPI_URL` | Backend URL for Streamlit | `http://localhost:8000` |
| `PYTHONUNBUFFERED` | Disable Python buffering | `1` |
| `LOG_LEVEL` | Logging level | `INFO` |

**Deployment Variables (Render):**

| Variable | Description | Example |
|----------|-------------|---------|
| `FASTAPI_URL` | Deployed API URL | `https://elvara-api.onrender.com` |

No secrets or API keys required - model is self-contained.

---

## 🧠 Model Information

### Model Architecture

**Type:** HistGradientBoostingClassifier (scikit-learn)

**Training Configuration:**
```python
max_iter=150
learning_rate=0.05
max_depth=5
min_samples_leaf=10
class_weight='balanced'
random_state=42
```

**Performance Metrics (Test Set):**
- **ROC-AUC:** 0.9582
- **Precision:** 0.9863
- **Recall:** 0.8783
- **F1 Score:** 0.9292

**Training Data:**
- Training samples: 3,750
- Test samples: 1,250
- Class distribution: Balanced via class weighting

### Features (46 total)

**Static Features (4):**
- `age`, `comorbidity_count`, `gender_Male`, `gender_Other/Not specified`

**Vital Signs (30 features, 6-hour lookback):**
- Heart rate, Temperature, Oxygen saturation, Respiratory rate, Blood pressure
- Each with: `_mean`, `_min`, `_max`, `_std`, `_last`, `_rate_per_hr`

**Laboratory Values (10 features, 24-hour lookback):**
- White cell count, CRP, Lactate, Creatinine, Platelet count
- Each with: `_mean`, `_last`

**Feature Engineering:**
- Temporal aggregation (mean, min, max, std deviation)
- Trend detection (rate of change per hour)
- Median imputation for missing values
- Automatic windowing (6hr vitals, 24hr labs)

### Risk Categories

| Score | Category | Color | Clinical Action |
|-------|----------|-------|-----------------|
| ≥70% | High | Red | Urgent evaluation, consider ICU |
| 35-69% | Moderate | Orange | Close monitoring, reassess in 2-4hrs |
| <35% | Low | Green | Standard care, routine monitoring |

---

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/openapi.json

---

### Available Endpoints

#### **Health Check** (`GET /health`)

Check API and model status.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Elvara-sepsis-cdss",
  "model_loaded": true,
  "version": "1.0.0"
}
```

---

#### **Predict Sepsis Risk** (`POST /predict-risk`)

Generate sepsis risk prediction for a patient.

**Request Body:**
```json
{
  "patient_id": "P12345",
  "age": 68,
  "gender": "male",
  "comorbidity_count": 2,
  "vitals": [
    {
      "timestamp": "2026-08-28T10:00:00Z",
      "heart_rate": 105.0,
      "temperature": 38.5,
      "oxygen_saturation": 93.0,
      "respiratory_rate": 24.0,
      "blood_pressure": 95.0
    },
    {
      "timestamp": "2026-08-28T07:00:00Z",
      "heart_rate": 108.0,
      "temperature": 38.7,
      "oxygen_saturation": 92.0,
      "respiratory_rate": 26.0,
      "blood_pressure": 90.0
    }
  ],
  "labs": [
    {
      "timestamp": "2026-08-28T09:30:00Z",
      "white_cell_count": 14.2,
      "crp": 85.0,
      "lactate": 3.1,
      "creatinine": 1.8,
      "platelet_count": 140.0
    }
  ]
}
```

**Response:**
```json
{
  "patient_id": "P12345",
  "sepsis_risk_score": 0.8542,
  "risk_category": "High",
  "prediction_window": "6-12 hours",
  "key_risk_factors": [
    "Elevated Heart Rate (108.0 bpm)",
    "Elevated Serum Lactate (3.1 mmol/L)",
    "Low Blood Pressure (90.0 mmHg)",
    "Low Oxygen Saturation (92.0%)"
  ]
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/predict-risk \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

---

#### **Prometheus Metrics** (`GET /metrics`)

Export Prometheus metrics for monitoring.

```bash
curl http://localhost:8000/metrics
```

**Metrics Exposed:**
- `elvara_sepsis_prediction_total` - Total predictions by risk category
- `elvara_sepsis_prediction_latency_seconds` - Prediction latency histogram
- `elvara_sepsis_model_load` - Model load status (1=loaded, 0=failed)

---

#### **Drift Report** (`GET|POST /monitoring/drift-report`)

Generate Evidently drift analysis report (HTML).

```bash
# Generate report
curl -X POST http://localhost:8000/monitoring/drift-report

# View report
open monitoring/reports/evidently_drift_report.html
```

**Use Case:** Detect data drift between training and production data.

---

### Request Schema

**VitalObservation:**
```json
{
  "timestamp": "ISO 8601 datetime (optional)",
  "heart_rate": "float (bpm)",
  "temperature": "float (°C)",
  "oxygen_saturation": "float (%)",
  "respiratory_rate": "float (/min)",
  "blood_pressure": "float (systolic mmHg)"
}
```

**LabObservation:**
```json
{
  "timestamp": "ISO 8601 datetime (optional)",
  "white_cell_count": "float (×10⁹/L)",
  "crp": "float (mg/L)",
  "lactate": "float (mmol/L)",
  "creatinine": "float (mg/dL)",
  "platelet_count": "float (×10⁹/L)"
}
```

**Gender Values:**
- `"male"`, `"female"`, `"other/not specified"` (lowercase)

---

### Multi-Observation Inputs

**Best Practice:** Provide **2-3 vital observations** and **1-2 lab observations** for optimal prediction quality.

**Why?** The model was trained on temporal data:
- **Median:** 2 vital observations per 6-hour window
- **Median:** 2 lab observations per 24-hour window

**Impact:**
- **Single observation:** ~43% of features used, ~10-15% ROC-AUC drop
- **Two observations:** ~70-80% of features used, minimal degradation
- **Three observations:** ~85%+ of features used, optimal performance

**Timestamps:**
- Most recent observation: Current time
- Earlier observations: 1-6 hours prior for vitals, 12-24 hours for labs
- Auto-generated if not provided

---

## 🚢 Deployment

### Local Docker Compose

```bash
# Build and start all services
cd docker
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Services:**
- `api` - FastAPI backend (http://localhost:8000)
- `streamlit` - Streamlit UI (http://localhost:8501)
- `prometheus` - Metrics scraper (http://localhost:9090)
- `grafana` - Visualization (http://localhost:3000, admin/admin)

---

### Render Deployment

**Quick Deploy (Blueprint):**

1. **Connect GitHub repo to Render:**
   - Go to https://dashboard.render.com/
   - New → Blueprint
   - Select your GitHub repository
   - Render detects `render.yaml` automatically

2. **Deploy services:**
   - Click "Apply" to create both services
   - `elvara-api` and `elvara-streamlit` will deploy

3. **Configure Streamlit backend URL:**
   - Wait for `elvara-api` to finish deploying
   - Copy the API URL (e.g., `https://elvara-api.onrender.com`)
   - Go to `elvara-streamlit` service → Environment
   - Set `FASTAPI_URL` to the API URL
   - Save (triggers redeploy)

4. **Test deployment:**
   - Visit `https://elvara-streamlit.onrender.com`
   - Submit a test prediction
   - Verify risk assessment displays

**Cost:** $14/month ($7 per service on Starter plan)

**Detailed Instructions:** See [DEPLOYMENT.md](DEPLOYMENT.md)

---

### Environment Variables (Render)

**elvara-api (FastAPI):**
```
MODEL_PATH=/app/models/sepsis_model.joblib
PYTHONUNBUFFERED=1
```

**elvara-streamlit (Streamlit):**
```
FASTAPI_URL=https://elvara-api.onrender.com  # Replace with your API URL
PYTHONUNBUFFERED=1
```

---

## 📊 Monitoring

### Prometheus Metrics

**Exposed at:** `http://localhost:8000/metrics`

**Key Metrics:**
- `elvara_sepsis_prediction_total{risk_category="High|Moderate|Low"}` - Prediction count by category
- `elvara_sepsis_prediction_latency_seconds` - Inference latency (P50, P95, P99)
- `elvara_sepsis_model_load` - Model health (1=healthy, 0=failed)

**Scrape Configuration:**
```yaml
# monitoring/prometheus.yml
scrape_configs:
  - job_name: 'elvara-api'
    static_configs:
      - targets: ['api:8000']
    scrape_interval: 15s
    metrics_path: /metrics
```

**Grafana Dashboard:**
- Access: http://localhost:3000 (admin/admin)
- Import Prometheus data source: http://prometheus:9090
- Create dashboards for prediction volume, latency, risk distribution

---

### Evidently Drift Detection

**Generate Drift Report:**
```bash
# Via API
curl -X POST http://localhost:8000/monitoring/drift-report

# Via Python
python monitoring/drift_monitor.py
```

**Output:** `monitoring/reports/evidently_drift_report.html`

**Monitors:**
- Feature distribution drift (KS test)
- Data quality (missing values, outliers)
- Target drift (prediction distribution)
- Comparison: Training data vs. recent predictions

**Use Case:** Detect model degradation, trigger retraining

---

## 🧪 Testing

### Test Patients (Real Test Set)

Three real patients from the test set with known outcomes:

**Patient 1: High Risk (True Sepsis)**
- ID: 747 | Age: 93 | Female | 3 comorbidities
- Vitals: HR 112-116, Temp 38.8°C, SpO2 90-93%, RR 23-35
- Labs: Lactate 5.3, WBC 14.9, CRP 108.2
- **Expected:** High risk (>70%), model predicted 99.96% ✓

**Patient 2: Low Risk (No Sepsis)**
- ID: 2276 | Age: 18 | Male | 2 comorbidities
- Vitals: HR 72, Temp 37.1°C, SpO2 97%, RR 18
- Labs: Lactate 1.5, WBC 8.9, CRP 6.5
- **Expected:** Low risk (<35%), model predicted 3.5% ✓

**Patient 3: Edge Case (No Sepsis)**
- ID: 187 | Age: 64 | Male | 0 comorbidities
- Vitals: HR 91-98, Temp 36.8°C, SpO2 100%, RR 18-20
- Labs: Lactate 0.7, WBC 8.9, CRP 10.4
- **Expected:** Low-moderate risk, model predicted 21.1% ✓

**Test Data:** `test_patients_full.json`

### Running Tests

```bash
# Unit tests (future)
pytest

# API integration test
curl -X POST http://localhost:8000/predict-risk \
  -H "Content-Type: application/json" \
  -d @test_request.json

# Expected: JSON response with risk_score, category, factors
```

### Manual UI Testing

1. Open http://localhost:8501
2. Enter Patient 747 data (see test patients above)
3. Click "Run risk assessment"
4. Verify: High risk badge (red), score ~100/100, key factors listed

---

## 📖 Usage Guide

### Clinical Workflow

1. **Patient Assessment**
   - Collect vital signs (2-3 observations over 6 hours)
   - Collect lab results (most recent + prior 12-24hr if available)
   - Note patient demographics and comorbidities

2. **Submit to Elvara**
   - Enter data in Streamlit UI or call API
   - Observation 1 (most recent): Current vitals/labs
   - Observation 2 (earlier): 1-6 hours prior for vitals

3. **Interpret Results**
   - **High risk (≥70%):** Urgent evaluation, consider ICU transfer
   - **Moderate risk (35-69%):** Close monitoring, reassess in 2-4 hours
   - **Low risk (<35%):** Standard care, routine monitoring
   - Review key risk factors for clinical context

4. **Documentation**
   - Risk score and category documented in EMR
   - Key factors inform clinical notes
   - Prediction window guides reassessment timing

---

## 🗺️ Roadmap

- [x] ML model training (HistGradientBoostingClassifier)
- [x] Feature engineering pipeline (46 features)
- [x] FastAPI backend with prediction endpoint
- [x] Streamlit multi-observation UI
- [x] Docker containerization
- [x] Prometheus metrics export
- [x] Evidently drift monitoring
- [x] Render deployment blueprints
- [ ] Automated retraining pipeline
- [ ] Real-time monitoring dashboard (Grafana)
- [ ] EMR integration (HL7 FHIR)
- [ ] Multi-model ensemble
- [ ] Explainability (SHAP values)
- [ ] Audit logging for clinical use
- [ ] Mobile-responsive UI

---

## ⚠️ Clinical Disclaimer

**This system is a research tool and not a validated diagnostic device.**

- Predictions are generated by a trained machine learning model
- Not a substitute for clinical judgment or local protocols
- Use alongside professional medical assessment
- Not FDA-cleared or CE-marked
- Not intended for direct clinical use without validation

**Healthcare providers must:**
- Use clinical judgment and expertise
- Follow institutional protocols
- Validate predictions against patient presentation
- Document decision-making rationale
- Report adverse events or prediction errors

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Contributors

- **ML Engineering** - Model development, feature engineering
- **Backend Engineering** - FastAPI, monitoring, deployment
- **Frontend Engineering** - Streamlit UI, clinical design
- **Clinical Advisory** - Domain expertise, validation

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/your-org/elvara/issues)
- **Documentation:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **Email:** support@elvara-health.com

---

## 🙏 Acknowledgments

- Clinical data sourced from synthetic patient records (MIMIC-inspired)
- UI design inspired by clinical monitoring systems
- Built with scikit-learn, FastAPI, Streamlit, and Evidently AI

---

**Built with precision for clinical care** 🏥
