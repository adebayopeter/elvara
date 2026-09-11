"""Elvara — Gradio version for comparison with Streamlit UI."""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any

import gradio as gr
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BACKEND_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

# Color scheme matching Streamlit version
COLORS = {
    "high": "#D64545",
    "moderate": "#E0A030",
    "low": "#3FA66D",
}


def validate_inputs(vitals_t1: dict, vitals_t2: dict, vitals_t3: dict | None,
                   labs_t1: dict, labs_t2: dict | None) -> list[str]:
    """Validate clinical inputs across all timepoints."""
    issues = []

    # Validate vitals
    for time_key, vitals in [("t1", vitals_t1), ("t2", vitals_t2), ("t3", vitals_t3)]:
        if vitals:
            if not 34.0 <= vitals["temperature"] <= 42.0:
                issues.append(f"Temperature is outside plausible range (34.0–42.0 °C) in vital observation {time_key}.")
            if not 70 <= vitals["spo2"] <= 100:
                issues.append(f"Oxygen saturation is outside plausible range (70–100%) in vital observation {time_key}.")
            if not 40 <= vitals["systolic_bp"] <= 220:
                issues.append(f"Systolic BP is outside plausible range (40–220 mmHg) in vital observation {time_key}.")

    # Validate labs
    for time_key, labs in [("t1", labs_t1), ("t2", labs_t2)]:
        if labs:
            if not 0.2 <= labs["lactate"] <= 15:
                issues.append(f"Lactate is outside plausible range (0.2–15.0 mmol/L) in lab observation {time_key}.")

    return issues


def call_prediction_api(patient_id: str, age: int, gender: str, comorbidity_count: int,
                       vitals_t1: dict, vitals_t2: dict, vitals_t3: dict | None,
                       labs_t1: dict, labs_t2: dict | None) -> dict[str, Any]:
    """Call the FastAPI backend to get sepsis risk prediction."""
    now = datetime.now()

    # Build vitals list with timestamps (exact same logic as Streamlit)
    vitals = []
    if vitals_t1:
        vitals.append({
            "timestamp": now.isoformat(),
            "heart_rate": float(vitals_t1["heart_rate"]),
            "temperature": float(vitals_t1["temperature"]),
            "oxygen_saturation": float(vitals_t1["spo2"]),
            "respiratory_rate": float(vitals_t1["respiratory_rate"]),
            "blood_pressure": float(vitals_t1["systolic_bp"]),
        })

    if vitals_t2:
        vitals.append({
            "timestamp": (now - timedelta(hours=3)).isoformat(),
            "heart_rate": float(vitals_t2["heart_rate"]),
            "temperature": float(vitals_t2["temperature"]),
            "oxygen_saturation": float(vitals_t2["spo2"]),
            "respiratory_rate": float(vitals_t2["respiratory_rate"]),
            "blood_pressure": float(vitals_t2["systolic_bp"]),
        })

    if vitals_t3:
        vitals.append({
            "timestamp": (now - timedelta(hours=5)).isoformat(),
            "heart_rate": float(vitals_t3["heart_rate"]),
            "temperature": float(vitals_t3["temperature"]),
            "oxygen_saturation": float(vitals_t3["spo2"]),
            "respiratory_rate": float(vitals_t3["respiratory_rate"]),
            "blood_pressure": float(vitals_t3["systolic_bp"]),
        })

    # Build labs list with timestamps (exact same logic as Streamlit)
    labs = []
    if labs_t1:
        labs.append({
            "timestamp": now.isoformat(),
            "white_cell_count": float(labs_t1["wbc"]),
            "crp": float(labs_t1["crp"]),
            "lactate": float(labs_t1["lactate"]),
            "creatinine": float(labs_t1["creatinine"]),
            "platelet_count": float(labs_t1["platelets"]),
        })

    if labs_t2:
        labs.append({
            "timestamp": (now - timedelta(hours=18)).isoformat(),
            "white_cell_count": float(labs_t2["wbc"]),
            "crp": float(labs_t2["crp"]),
            "lactate": float(labs_t2["lactate"]),
            "creatinine": float(labs_t2["creatinine"]),
            "platelet_count": float(labs_t2["platelets"]),
        })

    # Map gender to backend format (exact same mapping as Streamlit)
    gender_map = {
        "Female": "female",
        "Male": "male",
        "Intersex / other": "other/not specified",
        "Not recorded": "other/not specified",
    }

    payload = {
        "patient_id": patient_id,
        "age": age,
        "gender": gender_map.get(gender, "other/not specified"),
        "comorbidity_count": comorbidity_count,
        "vitals": vitals,
        "labs": labs,
    }

    try:
        response = requests.post(
            f"{BACKEND_URL}/predict-risk",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to connect to prediction service: {str(e)}")


def run_assessment(
    # Patient context
    patient_id: str, age: int, sex: str, comorbidities: int,
    # Vitals t1 (most recent)
    v1_hr: int, v1_bp: int, v1_rr: int, v1_temp: float, v1_spo2: int,
    # Vitals t2 (1-6 hours earlier)
    v2_hr: int, v2_bp: int, v2_rr: int, v2_temp: float, v2_spo2: int,
    # Vitals t3 (optional)
    add_v3: bool, v3_hr: int, v3_bp: int, v3_rr: int, v3_temp: float, v3_spo2: int,
    # Labs t1 (most recent)
    l1_lactate: float, l1_wbc: float, l1_crp: float, l1_creatinine: float, l1_platelets: int,
    # Labs t2 (optional)
    add_l2: bool, l2_lactate: float, l2_wbc: float, l2_crp: float, l2_creatinine: float, l2_platelets: int,
) -> tuple[str, str]:
    """Run sepsis risk assessment and return result HTML and status message."""

    # Collect observations
    vitals_t1 = {
        "heart_rate": v1_hr,
        "systolic_bp": v1_bp,
        "respiratory_rate": v1_rr,
        "temperature": v1_temp,
        "spo2": v1_spo2,
    }

    vitals_t2 = {
        "heart_rate": v2_hr,
        "systolic_bp": v2_bp,
        "respiratory_rate": v2_rr,
        "temperature": v2_temp,
        "spo2": v2_spo2,
    }

    vitals_t3 = {
        "heart_rate": v3_hr,
        "systolic_bp": v3_bp,
        "respiratory_rate": v3_rr,
        "temperature": v3_temp,
        "spo2": v3_spo2,
    } if add_v3 else None

    labs_t1 = {
        "lactate": l1_lactate,
        "wbc": l1_wbc,
        "crp": l1_crp,
        "creatinine": l1_creatinine,
        "platelets": l1_platelets,
    }

    labs_t2 = {
        "lactate": l2_lactate,
        "wbc": l2_wbc,
        "crp": l2_crp,
        "creatinine": l2_creatinine,
        "platelets": l2_platelets,
    } if add_l2 else None

    # Validate inputs
    issues = validate_inputs(vitals_t1, vitals_t2, vitals_t3, labs_t1, labs_t2)
    if issues:
        error_msg = "❌ **Validation Errors:**\n\n" + "\n".join(f"- {issue}" for issue in issues)
        return "", error_msg

    # Call API
    try:
        result = call_prediction_api(
            patient_id, age, sex, comorbidities,
            vitals_t1, vitals_t2, vitals_t3,
            labs_t1, labs_t2
        )

        # Format result
        score = result["sepsis_risk_score"] * 100
        category = result["risk_category"]
        window = result["prediction_window"]
        factors = result["key_risk_factors"]

        # Color-code by category
        if category == "High":
            color = COLORS["high"]
            icon = "🔴"
        elif category == "Moderate":
            color = COLORS["moderate"]
            icon = "🟠"
        else:
            color = COLORS["low"]
            icon = "🟢"

        # Build result HTML
        result_html = f"""
        <div style="border: 2px solid {color}; border-radius: 12px; padding: 24px; margin: 16px 0;">
            <h2 style="color: {color}; margin-top: 0;">
                {icon} {category} Risk
            </h2>
            <div style="font-size: 48px; font-weight: bold; color: {color}; margin: 16px 0;">
                {score:.1f}<span style="font-size: 24px; color: #666;">/100</span>
            </div>
            <p style="color: #666; font-size: 14px; margin-bottom: 16px;">
                <strong>Prediction window:</strong> {window}
            </p>
            <hr style="border: none; border-top: 1px solid #ddd; margin: 16px 0;">
            <p style="margin-bottom: 8px;"><strong>Key Risk Factors:</strong></p>
            <ul style="margin: 8px 0; padding-left: 24px;">
                {''.join(f'<li>{factor}</li>' for factor in factors)}
            </ul>
        </div>
        """

        success_msg = f"✅ Assessment complete for patient {patient_id}"
        return result_html, success_msg

    except Exception as e:
        error_msg = f"❌ **Prediction Error:**\n\n{str(e)}"
        return "", error_msg


# Build Gradio interface
with gr.Blocks(title="Elvara | Sepsis Risk Assessment") as demo:
    gr.Markdown(
        """
        # Elvara — Sepsis Risk Assessment

        **Clinical decision support for early sepsis detection**

        ---
        """
    )

    # Disclaimer banner (exact text from Streamlit)
    gr.Markdown(
        """
        > **ML-BASED ESTIMATOR**
        > Predictions are generated by a trained machine learning model. This is not
        > a diagnostic device and must be used alongside local clinical protocols and
        > professional judgement.

        ---
        """
    )

    with gr.Row():
        # Left column: Patient Context + Vitals
        with gr.Column(scale=1):
            gr.Markdown("### Patient Context")
            patient_id = gr.Textbox(label="Patient Identifier", value="ELV-2048")
            age = gr.Number(label="Age", value=67, minimum=0, maximum=120, step=1, precision=0)
            sex = gr.Dropdown(
                label="Sex",
                choices=["Female", "Male", "Intersex / other", "Not recorded"],
                value="Female"
            )
            comorbidities = gr.Number(
                label="Known Comorbidities",
                value=2,
                minimum=0,
                maximum=20,
                step=1,
                precision=0,
                info="Count of documented chronic conditions"
            )

            gr.Markdown("---")
            gr.Markdown("### Vital Signs (2 required observations)")

            gr.Markdown("**Most recent observation**")
            with gr.Row():
                v1_hr = gr.Number(label="Heart Rate (bpm)", value=104, minimum=30, maximum=240, step=1)
                v1_bp = gr.Number(label="Systolic BP (mmHg)", value=98, minimum=40, maximum=280, step=1)
            with gr.Row():
                v1_rr = gr.Number(label="Respiratory Rate (/min)", value=22, minimum=4, maximum=80, step=1)
                v1_temp = gr.Number(label="Temperature (°C)", value=38.4, minimum=30.0, maximum=45.0, step=0.1)
            v1_spo2 = gr.Number(label="Oxygen Saturation (%)", value=94, minimum=50, maximum=100, step=1)

            gr.Markdown("**1–6 hours earlier**")
            with gr.Row():
                v2_hr = gr.Number(label="Heart Rate (bpm)", value=98, minimum=30, maximum=240, step=1)
                v2_bp = gr.Number(label="Systolic BP (mmHg)", value=105, minimum=40, maximum=280, step=1)
            with gr.Row():
                v2_rr = gr.Number(label="Respiratory Rate (/min)", value=20, minimum=4, maximum=80, step=1)
                v2_temp = gr.Number(label="Temperature (°C)", value=37.8, minimum=30.0, maximum=45.0, step=0.1)
            v2_spo2 = gr.Number(label="Oxygen Saturation (%)", value=95, minimum=50, maximum=100, step=1)

            add_v3 = gr.Checkbox(label="Add third vital observation (optional)", value=False)

            with gr.Group(visible=True) as v3_group:
                gr.Markdown("**2–6 hours earlier (optional)**")
                with gr.Row():
                    v3_hr = gr.Number(label="Heart Rate (bpm)", value=92, minimum=30, maximum=240, step=1)
                    v3_bp = gr.Number(label="Systolic BP (mmHg)", value=110, minimum=40, maximum=280, step=1)
                with gr.Row():
                    v3_rr = gr.Number(label="Respiratory Rate (/min)", value=18, minimum=4, maximum=80, step=1)
                    v3_temp = gr.Number(label="Temperature (°C)", value=37.2, minimum=30.0, maximum=45.0, step=0.1)
                v3_spo2 = gr.Number(label="Oxygen Saturation (%)", value=96, minimum=50, maximum=100, step=1)

        # Right column: Labs + Results
        with gr.Column(scale=1):
            gr.Markdown("### Laboratory Results (1–2 observations)")

            gr.Markdown("**Most recent lab results**")
            with gr.Row():
                l1_lactate = gr.Number(label="Lactate (mmol/L)", value=2.6, minimum=0.0, maximum=30.0, step=0.1)
                l1_wbc = gr.Number(label="WBC (×10⁹/L)", value=15.8, minimum=0.0, maximum=100.0, step=0.1)
            with gr.Row():
                l1_crp = gr.Number(label="CRP (mg/L)", value=85.0, minimum=0.0, maximum=500.0, step=0.1)
                l1_creatinine = gr.Number(label="Creatinine (mg/dL)", value=1.7, minimum=0.1, maximum=20.0, step=0.1)
            l1_platelets = gr.Number(label="Platelet Count (×10⁹/L)", value=142, minimum=1, maximum=1000, step=1)

            add_l2 = gr.Checkbox(label="Add earlier lab result (optional)", value=False)

            with gr.Group(visible=True) as l2_group:
                gr.Markdown("**12–24 hours earlier (optional)**")
                with gr.Row():
                    l2_lactate = gr.Number(label="Lactate (mmol/L)", value=2.0, minimum=0.0, maximum=30.0, step=0.1)
                    l2_wbc = gr.Number(label="WBC (×10⁹/L)", value=12.5, minimum=0.0, maximum=100.0, step=0.1)
                with gr.Row():
                    l2_crp = gr.Number(label="CRP (mg/L)", value=65.0, minimum=0.0, maximum=500.0, step=0.1)
                    l2_creatinine = gr.Number(label="Creatinine (mg/dL)", value=1.5, minimum=0.1, maximum=20.0, step=0.1)
                l2_platelets = gr.Number(label="Platelet Count (×10⁹/L)", value=165, minimum=1, maximum=1000, step=1)

            gr.Markdown("---")

            # Assessment button
            assess_btn = gr.Button("Run Risk Assessment", variant="primary", size="lg")

            # Status message
            status_msg = gr.Markdown("")

            # Result display
            gr.Markdown("### Assessment Result")
            result_display = gr.HTML(
                """
                <div style="border: 1px dashed #ccc; border-radius: 12px; padding: 40px; text-align: center; color: #999;">
                    <p style="font-size: 18px; margin: 0;">Awaiting assessment</p>
                    <p style="font-size: 14px; margin-top: 8px;">Enter patient data and click "Run Risk Assessment"</p>
                </div>
                """
            )

    # Wire up the assessment button
    assess_btn.click(
        fn=run_assessment,
        inputs=[
            patient_id, age, sex, comorbidities,
            v1_hr, v1_bp, v1_rr, v1_temp, v1_spo2,
            v2_hr, v2_bp, v2_rr, v2_temp, v2_spo2,
            add_v3, v3_hr, v3_bp, v3_rr, v3_temp, v3_spo2,
            l1_lactate, l1_wbc, l1_crp, l1_creatinine, l1_platelets,
            add_l2, l2_lactate, l2_wbc, l2_crp, l2_creatinine, l2_platelets,
        ],
        outputs=[result_display, status_msg]
    )

    gr.Markdown(
        """
        ---

        **Reference Ranges:**
        - Heart Rate: 60–100 bpm
        - Systolic BP: 90–120 mmHg
        - Respiratory Rate: 12–20 /min
        - Temperature: 36.5–37.5 °C
        - Oxygen Saturation: 95–100%
        - Lactate: 0.5–2.2 mmol/L
        - WBC: 4.0–11.0 ×10⁹/L
        - CRP: <10 mg/L
        - Creatinine: 0.6–1.3 mg/dL
        - Platelet Count: 150–450 ×10⁹/L
        """
    )


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=False
    )
