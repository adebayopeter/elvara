import os
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def load_raw_data(data_dir: str | Path | None = None):
    if data_dir is None:
        raw_path = BASE_DIR / 'data' / 'raw'
    else:
        raw_path = Path(data_dir)
        if not (raw_path / 'patients.csv').exists() and (raw_path / 'raw' / 'patients.csv').exists():
            raw_path = raw_path / 'raw'
        
    patients = pd.read_csv(raw_path / 'patients.csv', parse_dates=['registration_date'])
    vitals = pd.read_csv(raw_path / 'vital_signs.csv', parse_dates=['timestamp'])
    history = pd.read_csv(raw_path / 'clinical_history.csv')
    labs = pd.read_csv(raw_path / 'laboratory_results.csv', parse_dates=['timestamp'])
    outcomes = pd.read_csv(raw_path / 'sepsis_outcomes.csv', parse_dates=['diagnosis_time'])
    
    return patients, vitals, history, labs, outcomes


def clean_data(
    patients: pd.DataFrame,
    vitals: pd.DataFrame,
    history: pd.DataFrame,
    labs: pd.DataFrame,
    outcomes: pd.DataFrame,
):
    patients_clean = patients.copy()
    vitals_clean = vitals.copy()
    history_clean = history.copy()
    labs_clean = labs.copy()
    outcomes_clean = outcomes.copy()
    
    vitals_clean = vitals_clean.drop_duplicates(subset=['patient_id', 'timestamp']).reset_index(drop=True)
    labs_clean = labs_clean.drop_duplicates(subset=['patient_id', 'timestamp']).reset_index(drop=True)
    
    # Sort by timestamp for chronological forward fill
    vitals_clean = vitals_clean.sort_values(['patient_id', 'timestamp']).reset_index(drop=True)
    labs_clean = labs_clean.sort_values(['patient_id', 'timestamp']).reset_index(drop=True)
    
    vitals_clean['heart_rate'] = vitals_clean['heart_rate'].clip(30, 200)
    vitals_clean['temperature'] = vitals_clean['temperature'].clip(32, 43)
    vitals_clean['oxygen_saturation'] = vitals_clean['oxygen_saturation'].clip(50, 100)
    vitals_clean['respiratory_rate'] = vitals_clean['respiratory_rate'].clip(5, 60)
    vitals_clean['blood_pressure'] = vitals_clean['blood_pressure'].clip(40, 220)
        
    labs_clean['white_cell_count'] = labs_clean['white_cell_count'].clip(0.1, 50.0)
    labs_clean['crp'] = labs_clean['crp'].clip(0.0, 500.0)
    labs_clean['lactate'] = labs_clean['lactate'].clip(1.0, 20.0)
    labs_clean['creatinine'] = labs_clean['creatinine'].clip(0.1, 10.0)
    labs_clean['platelet_count'] = labs_clean['platelet_count'].clip(5.0, 700.0)
    
    # Check for out of range values in labs
    vital_cols = [
        'heart_rate', 
        'temperature', 
        'oxygen_saturation', 
        'respiratory_rate', 
        'blood_pressure'
    ]

    labs_cols = [
        'white_cell_count', 
        'crp',
        'lactate', 
        'creatinine', 
        'platelet_count'
    ]

    vitals_clean[vital_cols] = vitals_clean.groupby('patient_id')[vital_cols].ffill()
    vitals_clean[vital_cols] = vitals_clean[vital_cols].fillna(vitals_clean[vital_cols].median())
    
    labs_clean[labs_cols] = labs_clean.groupby('patient_id')[labs_cols].ffill()
    labs_clean[labs_cols] = labs_clean[labs_cols].fillna(labs_clean[labs_cols].median())
    
    return patients_clean, vitals_clean, history_clean, labs_clean, outcomes_clean


if __name__ == "__main__":
    patients, vitals, history, labs, outcomes = load_raw_data()
    p_clean, v_clean, h_clean, l_clean, o_clean = clean_data(patients, vitals, history, labs, outcomes)
    print("Data loaded and cleaned successfully.")
    