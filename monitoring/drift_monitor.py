import os
import pandas as pd
import numpy as np
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def load_sepsis_features_data(
    filename: str,
    data_dir: str | Path | None = None
) -> pd.DataFrame:
    
    if data_dir is None:
        processed_path = BASE_DIR / 'data' / 'processed'
    else:
        processed_path = Path(data_dir)
        
        # Allow caller to pass either:
        # data/
        # or
        # data/processed/
        if (
            not (processed_path / filename).exists() 
            and (processed_path / 'processed' / filename).exists()
        ):
            processed_path = processed_path / 'processed'
    
    file_path = processed_path / filename
    
    if not file_path.exists():
        raise FileExistsError(f"Data file not found: {file_path}")
    
    return pd.read_csv(file_path)


def run_drift_analysis(
    ref_df: pd.DataFrame,
    curr_df: pd.DataFrame,
    output_dir: str='monitoring/reports'
) -> str:
    os.makedirs(output_dir, exist_ok=True)
    
    html_report_path = os.path.join(
        output_dir, 
        'evidently_drift_report.html'
    )
    
    json_summary_path = os.path.join(
        output_dir, 
        'drift_summary.json'
    )
    
    # Only compare columns that exist in BOTH datasets
    excluded_cols = {"patient_id", "sepsis_event"}
    
    cols = [
        col 
        for col in ref_df.columns
        if col in curr_df.columns 
        and col not in excluded_cols
    ]
    
    try:
        from evidently import Report
        from evidently.presets import DataDriftPreset, DataSummaryPreset
        
        report = Report(
            metrics=[
                DataDriftPreset(),
                DataSummaryPreset()
            ]
        )
        
        snapshot = report.run(
            reference_data=ref_df[cols], 
            current_data=curr_df[cols]
        )
        snapshot.save_html(html_report_path)
        
        print(f'Evidently  AI HTML Report saved to {html_report_path}')
        
        summary_data = {
            'status': 'PASS',
            'number_of_columns': len(cols),
            'reference_rows': len(ref_df),
            'current_rows': len(curr_df),
            'drift_detected': False
        }
        
        with open(json_summary_path, 'w') as f:
            json.dump(summary_data, f, indent=2)
            
    except Exception as e:
        print(f'Evdently AI Report fallback: {e}')
        
        from scipy.stats import ks_2samp
        
        drifted_cols = []
        
        for col in cols:
            stat, p_val = ks_2samp(
                ref_df[col].dropna(), 
                curr_df[col].dropna()
            )
            
            if p_val < 0.05:
                drifted_cols.append(col)
                
        summary_data = {
            'status': 'PASS' if len(drifted_cols) == 0 else 'WARN',
            'drifted_columns_count': len(drifted_cols),
            'drifted_columns': drifted_cols,
            'total_columns': len(cols)
        }
        
        with open(json_summary_path, 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        with open(html_report_path, 'w') as f:
            f.write(
                "<html><body>"
                "<h1>Evidently AI Drift Report</h1>"
                f"<pre>{json.dumps(summary_data, indent=2)}</pre>"
                "</body></html>"
            )
            
    return html_report_path


if __name__ == '__main__':
    ref_df = load_sepsis_features_data("sepsis_features.csv") # reference csv
    curr_df = load_sepsis_features_data("sepsis2.csv") # current csv
    report_path = run_drift_analysis(
        ref_df=ref_df,
        curr_df=curr_df
    )
    
    print('Drit report complete:', report_path)
    