import time
import os
import sys
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from contextlib import asynccontextmanager


BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
    
try:
    from app.schemas import HealthCheckResponse, SepsisPredictionRequest, SepsisPredictionResponse
    from src.predict import SepsisPredictor
    from app.metrics import PREDICTION_REQUESTS_TOTAL, PREDICTION_LATENCY_SECONDS, MODEL_LOAD_GAUGE
except ImportError:
    from schemas import HealthCheckResponse, SepsisPredictionRequest, SepsisPredictionResponse
    from predict import SepsisPredictor
    from metrics import PREDICTION_REQUESTS_TOTAL, PREDICTION_LATENCY_SECONDS, MODEL_LOAD_GAUGE

predictor: SepsisPredictor | None = None

def get_or_load_predictor() -> SepsisPredictor | None:
    global predictor
    if predictor is None:
        try:
            default_model_path = str(BASE_DIR / 'models' / 'sepsis_model.joblib')
            model_path = os.getenv('MODEL_PATH', default_model_path)
            predictor = SepsisPredictor(model_path=model_path)
            MODEL_LOAD_GAUGE.set(1)
            print(f"SepsisPredictor loaded successfully from: {model_path}")
        except Exception as e:
            MODEL_LOAD_GAUGE.set(0)
            print(f"Error loading model: {e}")
    return predictor

@asynccontextmanager
async def lifespan(app: FastAPI):
    get_or_load_predictor()
    yield
    
app = FastAPI(
    title="Elvara Health | Early Sepsis warning and deterioration system",
    description="Machine Learning Operations (MLOps) & Clinical Decisions Support System",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware to allow Streamlit frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "https://*.onrender.com",
        "*"  # Allow all origins for development/demo - restrict in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def load_model():
    global predictor
    try:
        model_path = os.getenv("MODEL_PATH", "/models/sepsis_model.pkl")
        predictor = SepsisPredictor(model_path)
        MODEL_LOAD_GAUGE.set(1)
    except Exception as e:
        MODEL_LOAD_GAUGE.set(0)
        print(f"Error loading model: {e}")

@app.get("/health", response_model=HealthCheckResponse, summary="Health Check Endpoint", description="Check the health status of the API and model.")
def health_check():
    is_loaded = predictor is not None
    return HealthCheckResponse(
        status="healthy" if is_loaded else "degraded",
        service="Elvara-sepsis-cdss",
        model_loaded=is_loaded,
        version="1.0.0",
    )
    
@app.post("/predict-risk", response_model=SepsisPredictionResponse, summary="Sepsis Risk Prediction", description="Predict the risk of sepsis for a patient based on vital and lab observations.")
def predict_risk(request: SepsisPredictionRequest):
    current_predictor = get_or_load_predictor()
    if current_predictor is None:
        raise HTTPException(status_code=503, detail="Sepsis ML Model is not loaded.")
    
    start_time = time.time()

    try:
        patient_dict = request.model_dump() if hasattr(request, 'model_dump') else request.dict()
        result = current_predictor.predict_patient(patient_dict)
        
        latency = time.time() - start_time
        PREDICTION_LATENCY_SECONDS.observe(latency)
        PREDICTION_REQUESTS_TOTAL.labels(risk_category=result['risk_category']).inc()
        
        return SepsisPredictionResponse(
            patient_id=result['patient_id'],
            sepsis_risk_score=result['sepsis_risk_score'],
            risk_category=result['risk_category'],
            prediction_window=result['prediction_window'],
            key_risk_factors=result['key_risk_factors']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
    

@app.get("/metrics", summary="Prometheus Metrics Endpoint", description="Expose Prometheus metrics for monitoring.")
def metrics():
    try:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics error: {str(e)}")
    
    
@app.api_route("/monitoring/drift-report", 
    methods=['GET', 'POST'],
    summary="Generate Data Drift Report", 
    description="Generate and retrieve a data drift analysis report using Evidently to detect model performance degradation."
)
def generate_drift_report():
    try:
        from monitoring.drift_monitor import run_drift_analysis, load_sepsis_features_data
        curr_df = load_sepsis_features_data("sepsis2.csv")
        ref_df = load_sepsis_features_data("sepsis_features.csv")
        report_path = run_drift_analysis(ref_df=ref_df, curr_df=curr_df)
        return FileResponse(report_path, media_type="text/html")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to generate evidently report: {str(e)}')
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)   
    