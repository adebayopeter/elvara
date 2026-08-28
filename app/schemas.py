from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class VitalObservation(BaseModel):
    timestamp: Optional[str] = Field(default=None, example="2026-08-20T09:30:00Z", description="Timestamp of the observation in ISO 8601 format")
    heart_rate: Optional[float] = Field(default=None, example=72.0, description="Heart rate in beats per minute")
    temperature: Optional[float] = Field(default=None, example=37.0, description="Body temperature in Celsius")
    oxygen_saturation: Optional[float] = Field(default=None, example=98.0, description="Oxygen saturation percentage")
    respiratory_rate: Optional[float] = Field(default=None, example=16.0, description="Respiratory rate in breaths per minute")
    blood_pressure: Optional[float] = Field(default=None, example=120.0, description="Blood pressure in mmHg")
    
    
class LabObservation(BaseModel):
    timestamp: Optional[str] = Field(default=None, example="2026-08-20T09:30:00Z", description="Timestamp of the observation in ISO 8601 format")
    white_cell_count: Optional[float] = Field(default=None, example=7.5, description="White cell count")
    crp: Optional[float] = Field(default=None, example=5.0, description="C-reactive protein level")
    lactate: Optional[float] = Field(default=None, example=1.2, description="Lactate level")
    creatinine: Optional[float] = Field(default=None, example=85.0, description="Creatinine level")
    platelet_count: Optional[float] = Field(default=None, example=250.0, description="Platelet count")


class SepsisPredictionRequest(BaseModel):
    patient_id: str = Field(..., example=201, description="Unique identifier for the patient")
    age: int = Field(..., example=65, description="Age of the patient in years")
    gender: str = Field(..., example="male", description="Gender of the patient (e.g., 'male', 'female', 'other/not specified')")
    comorbidity_count: int = Field(..., example=2, description="Number of comorbidities the patient has")
    vitals: List[VitalObservation] = Field(..., description="List of vital observations")
    labs: List[LabObservation] = Field(..., description="List of lab observations")
    
    
class SepsisPredictionResponse(BaseModel):
    patient_id: str
    sepsis_risk_score: float
    risk_category: str
    prediction_window: str
    key_risk_factors: List[str]
    

class HealthCheckResponse(BaseModel):
    status: str
    service: str
    model_loaded:bool
    version: str
    