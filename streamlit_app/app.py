"""Elvara — clinical sepsis risk dashboard powered by ML."""

from __future__ import annotations

import math
import os
from datetime import datetime, timedelta
from typing import Any
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


st.set_page_config(
    page_title="Elvara | Sepsis Risk",
    page_icon="E",
    layout="wide",
    initial_sidebar_state="expanded",
)


COLORS = {
    "ink": "#172333",
    "muted": "#65758B",
    "subtle": "#8A98A9",
    "line": "#DDE5EC",
    "canvas": "#F4F7F9",
    "panel": "#FFFFFF",
    "teal": "#0F3D3E",
    "teal_bright": "#1D6868",
    "high": "#D64545",
    "moderate": "#E0A030",
    "low": "#3FA66D",
}

BACKEND_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")


def inject_styles() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap');

        :root {{
            --ink: {COLORS["ink"]};
            --muted: {COLORS["muted"]};
            --line: {COLORS["line"]};
            --canvas: {COLORS["canvas"]};
            --panel: {COLORS["panel"]};
            --teal: {COLORS["teal"]};
        }}

        .stApp {{
            background: var(--canvas);
            color: var(--ink);
            font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}

        [data-testid="stHeader"] {{
            background: transparent;
        }}

        [data-testid="stSidebar"] {{
            background: #EDF2F5;
            border-right: 1px solid var(--line);
        }}

        [data-testid="stSidebar"] > div:first-child {{
            padding: 2rem 1.3rem 1.5rem;
        }}

        .block-container {{
            max-width: 1480px;
            padding: 2.1rem 3rem 4rem;
        }}

        .brand-lockup {{
            display: flex;
            align-items: center;
            gap: 0.7rem;
            margin-bottom: 2.8rem;
        }}

        .brand-mark {{
            width: 32px;
            height: 32px;
            border-radius: 9px;
            display: grid;
            place-items: center;
            color: white;
            background: var(--teal);
            font-family: 'IBM Plex Mono', monospace;
            font-weight: 600;
            font-size: 0.9rem;
            letter-spacing: -0.06em;
        }}

        .brand-name {{
            color: var(--ink);
            font-size: 1.1rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        }}

        .eyebrow {{
            color: var(--muted);
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }}

        .page-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1.5rem;
            margin-bottom: 2.1rem;
        }}

        .page-title {{
            color: var(--ink);
            font-size: clamp(1.65rem, 2.8vw, 2.45rem);
            font-weight: 600;
            letter-spacing: -0.045em;
            line-height: 1.05;
            margin: 0.3rem 0 0.55rem;
        }}

        .page-subtitle {{
            color: var(--muted);
            font-size: 0.92rem;
            margin: 0;
        }}

        .status-pill {{
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            border: 1px solid #C9DDE0;
            border-radius: 999px;
            color: var(--teal);
            background: #F4FAFA;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.55rem 0.75rem;
            white-space: nowrap;
        }}

        .status-dot {{
            width: 7px;
            height: 7px;
            border-radius: 999px;
            background: var(--low);
        }}

        .section-heading {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            gap: 1rem;
            border-bottom: 1px solid var(--line);
            margin: 0.5rem 0 1.15rem;
            padding-bottom: 0.65rem;
        }}

        .section-title {{
            color: var(--ink);
            font-size: 0.91rem;
            font-weight: 700;
            letter-spacing: 0.015em;
            margin: 0;
        }}

        .section-note {{
            color: var(--subtle);
            font-size: 0.74rem;
            margin: 0;
        }}

        .panel {{
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 12px;
            padding: 1.2rem 1.25rem 1.35rem;
            box-shadow: 0 2px 6px rgba(23, 35, 51, 0.025);
        }}

        .input-group {{
            background: #F9FBFC;
            border: 1px solid #E8EEF2;
            border-radius: 9px;
            margin-bottom: 0.7rem;
            padding: 0.8rem 0.9rem 0.9rem;
        }}

        .input-group-label {{
            color: var(--muted);
            font-size: 0.71rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            margin-bottom: 0.15rem;
            text-transform: uppercase;
        }}

        .range-hint {{
            color: var(--subtle);
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.69rem;
            margin-top: 0.25rem;
        }}

        .context-card {{
            border-bottom: 1px solid #DCE5EA;
            margin: 0 -0.25rem 1.25rem;
            padding: 0 0.25rem 1.15rem;
        }}

        .context-label {{
            color: var(--subtle);
            font-size: 0.68rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }}

        .context-value {{
            color: var(--ink);
            font-size: 0.91rem;
            font-weight: 600;
            margin-top: 0.2rem;
        }}

        .sidebar-section {{
            color: var(--muted);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            margin: 1.3rem 0 0.7rem;
            text-transform: uppercase;
        }}

        .sidebar-footer {{
            border-top: 1px solid #DCE5EA;
            color: var(--subtle);
            font-size: 0.7rem;
            line-height: 1.5;
            margin-top: 2rem;
            padding-top: 0.85rem;
        }}

        .result-shell {{
            background: var(--teal);
            border-radius: 14px;
            color: #F5FBFB;
            min-height: 100%;
            overflow: hidden;
            padding: 1.5rem;
            position: relative;
        }}

        .result-shell::after {{
            border: 1px solid rgba(255,255,255,0.09);
            border-radius: 50%;
            content: "";
            height: 260px;
            position: absolute;
            right: -95px;
            top: -90px;
            width: 260px;
        }}

        .result-kicker {{
            color: #A9CBCB;
            font-size: 0.71rem;
            font-weight: 600;
            letter-spacing: 0.13em;
            text-transform: uppercase;
        }}

        .result-title {{
            color: white;
            font-size: 1.35rem;
            font-weight: 600;
            letter-spacing: -0.03em;
            margin: 0.35rem 0 0.2rem;
        }}

        .result-caption {{
            color: #B7CECE;
            font-size: 0.8rem;
            line-height: 1.45;
            margin: 0;
        }}

        .result-divider {{
            border-top: 1px solid rgba(255,255,255,0.15);
            margin: 1.2rem 0;
        }}

        .score-label {{
            color: #B7CECE;
            font-size: 0.71rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
        }}

        .score-number {{
            color: white;
            font-family: 'IBM Plex Mono', monospace;
            font-size: clamp(3.7rem, 6vw, 5.2rem);
            font-weight: 600;
            letter-spacing: -0.09em;
            line-height: 0.95;
            margin: 0.4rem 0 0.6rem;
        }}

        .score-unit {{
            color: #A9CBCB;
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 0.76rem;
            letter-spacing: 0;
            margin-left: 0.35rem;
        }}

        .category-badge {{
            border-radius: 999px;
            display: inline-flex;
            font-size: 0.75rem;
            font-weight: 700;
            padding: 0.38rem 0.7rem;
        }}

        .category-high {{ background: #F8DADB; color: #7C2528; }}
        .category-moderate {{ background: #FAEBC8; color: #684A0D; }}
        .category-low {{ background: #D9F0E1; color: #1F633E; }}

        .factor-heading {{
            color: #C5DADA;
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.1em;
            margin: 0 0 0.55rem;
            text-transform: uppercase;
        }}

        .factor-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
        }}

        .factor-chip {{
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.16);
            border-radius: 5px;
            color: #E5F0F0;
            font-size: 0.73rem;
            padding: 0.32rem 0.5rem;
        }}

        .window-box {{
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 8px;
            margin-top: 1.2rem;
            padding: 0.7rem 0.8rem;
        }}

        .window-label {{
            color: #A9CBCB;
            font-size: 0.69rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}

        .window-value {{
            color: white;
            font-size: 0.85rem;
            font-weight: 600;
            margin-top: 0.22rem;
        }}

        .empty-result {{
            align-items: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            min-height: 440px;
            padding: 2rem;
            text-align: center;
        }}

        .empty-icon {{
            align-items: center;
            border: 1px solid #A3C4C5;
            border-radius: 50%;
            color: var(--teal);
            display: flex;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 1.1rem;
            height: 46px;
            justify-content: center;
            margin-bottom: 1rem;
            width: 46px;
        }}

        .empty-title {{
            color: var(--ink);
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 0.35rem;
        }}

        .empty-copy {{
            color: var(--muted);
            font-size: 0.8rem;
            line-height: 1.5;
            max-width: 280px;
        }}

        .notice {{
            border-radius: 8px;
            font-size: 0.78rem;
            line-height: 1.45;
            margin: 0.8rem 0;
            padding: 0.75rem 0.85rem;
        }}

        .notice-error {{
            background: #FFF3F1;
            border: 1px solid #F0C7C2;
            color: #7E302A;
        }}

        .notice-info {{
            background: #EEF6F6;
            border: 1px solid #CDE1E1;
            color: #245758;
        }}

        .disclaimer {{
            color: var(--subtle);
            font-size: 0.69rem;
            line-height: 1.5;
            margin-top: 1.5rem;
        }}

        .time-badge {{
            background: #E8F2F3;
            border: 1px solid #C5DADA;
            border-radius: 5px;
            color: var(--teal);
            font-size: 0.68rem;
            font-weight: 600;
            padding: 0.25rem 0.5rem;
            display: inline-block;
            margin-bottom: 0.5rem;
        }}

        [data-testid="stNumberInput"] label,
        [data-testid="stTextInput"] label,
        [data-testid="stSelectbox"] label,
        [data-testid="stSlider"] label {{
            color: var(--ink) !important;
            font-size: 0.8rem !important;
            font-weight: 500 !important;
        }}

        [data-testid="stNumberInput"] input,
        [data-testid="stTextInput"] input {{
            background: white !important;
            border-color: #D5E0E7 !important;
            color: var(--ink) !important;
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 0.84rem !important;
        }}

        [data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
            background: white;
            border-color: #D5E0E7;
        }}

        .stButton > button {{
            background: var(--teal);
            border: 1px solid var(--teal);
            border-radius: 7px;
            color: white;
            font-size: 0.82rem;
            font-weight: 600;
            min-height: 2.5rem;
            transition: background 120ms ease, transform 120ms ease;
            width: 100%;
        }}

        .stButton > button:hover {{
            background: var(--teal_bright);
            border-color: var(--teal_bright);
            color: white;
            transform: translateY(-1px);
        }}

        .stButton > button:focus {{
            box-shadow: 0 0 0 3px rgba(29, 104, 104, 0.2);
        }}

        @media (max-width: 900px) {{
            .block-container {{ padding: 1.5rem 1rem 3rem; }}
            .page-header {{ flex-direction: column; margin-bottom: 1.5rem; }}
            .result-shell {{ margin-top: 1.25rem; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def section_heading(title: str, note: str) -> None:
    st.markdown(
        f"""
        <div class="section-heading">
            <p class="section-title">{title}</p>
            <p class="section-note">{note}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def input_hint(text: str) -> None:
    st.markdown(f'<div class="range-hint">{text}</div>', unsafe_allow_html=True)


def get_vital_inputs(time_label: str, key_prefix: str, defaults: dict) -> dict[str, Any]:
    """Render vital signs inputs for a single timepoint."""
    st.markdown(f'<div class="time-badge">{time_label}</div>', unsafe_allow_html=True)

    heart_rate = st.number_input(
        "Heart rate",
        min_value=30,
        max_value=240,
        value=defaults.get("heart_rate", 80),
        step=1,
        key=f"{key_prefix}_heart_rate",
        help="Beats per minute",
    )
    input_hint("Normal reference: 60–100 bpm")

    systolic_bp = st.number_input(
        "Systolic blood pressure",
        min_value=40,
        max_value=280,
        value=defaults.get("systolic_bp", 120),
        step=1,
        key=f"{key_prefix}_systolic_bp",
        help="Millimetres of mercury",
    )
    input_hint("Normal reference: 90–120 mmHg")

    respiratory_rate = st.number_input(
        "Respiratory rate",
        min_value=4,
        max_value=80,
        value=defaults.get("respiratory_rate", 16),
        step=1,
        key=f"{key_prefix}_respiratory_rate",
        help="Breaths per minute",
    )
    input_hint("Normal reference: 12–20 /min")

    temperature = st.number_input(
        "Temperature",
        min_value=30.0,
        max_value=45.0,
        value=defaults.get("temperature", 37.0),
        step=0.1,
        format="%.1f",
        key=f"{key_prefix}_temperature",
        help="Degrees Celsius",
    )
    input_hint("Plausible range: 34.0–42.0 °C")

    spo2 = st.number_input(
        "Oxygen saturation",
        min_value=50,
        max_value=100,
        value=defaults.get("spo2", 98),
        step=1,
        key=f"{key_prefix}_spo2",
        help="Peripheral oxygen saturation",
    )
    input_hint("Normal reference: 95–100%")

    return {
        "heart_rate": heart_rate,
        "systolic_bp": systolic_bp,
        "respiratory_rate": respiratory_rate,
        "temperature": temperature,
        "spo2": spo2,
    }


def get_lab_inputs(time_label: str, key_prefix: str, defaults: dict) -> dict[str, Any]:
    """Render laboratory inputs for a single timepoint."""
    st.markdown(f'<div class="time-badge">{time_label}</div>', unsafe_allow_html=True)

    lactate = st.number_input(
        "Lactate",
        min_value=0.0,
        max_value=30.0,
        value=defaults.get("lactate", 1.2),
        step=0.1,
        format="%.1f",
        key=f"{key_prefix}_lactate",
        help="Millimoles per litre",
    )
    input_hint("Normal reference: 0.5–2.2 mmol/L")

    wbc = st.number_input(
        "White blood cell count",
        min_value=0.0,
        max_value=100.0,
        value=defaults.get("wbc", 7.5),
        step=0.1,
        format="%.1f",
        key=f"{key_prefix}_wbc",
        help="10⁹ cells per litre",
    )
    input_hint("Normal reference: 4.0–11.0 ×10⁹/L")

    crp = st.number_input(
        "C-reactive protein (CRP)",
        min_value=0.0,
        max_value=500.0,
        value=defaults.get("crp", 5.0),
        step=0.1,
        format="%.1f",
        key=f"{key_prefix}_crp",
        help="Milligrams per litre",
    )
    input_hint("Normal reference: <10 mg/L")

    creatinine = st.number_input(
        "Creatinine",
        min_value=0.1,
        max_value=20.0,
        value=defaults.get("creatinine", 1.0),
        step=0.1,
        format="%.1f",
        key=f"{key_prefix}_creatinine",
        help="Milligrams per decilitre",
    )
    input_hint("Typical reference: 0.6–1.3 mg/dL")

    platelets = st.number_input(
        "Platelet count",
        min_value=1,
        max_value=1000,
        value=defaults.get("platelets", 250),
        step=1,
        key=f"{key_prefix}_platelets",
        help="10⁹ cells per litre",
    )
    input_hint("Normal reference: 150–450 ×10⁹/L")

    return {
        "lactate": lactate,
        "wbc": wbc,
        "crp": crp,
        "creatinine": creatinine,
        "platelets": platelets,
    }


def get_inputs() -> dict[str, Any]:
    """Render the input surface and return patient data with multiple timepoints."""
    section_heading("Clinical inputs", "Enter vital signs from 2 timepoints, labs from 1-2 timepoints")

    vitals_col, labs_col = st.columns(2, gap="large")

    with vitals_col:
        st.markdown(
            '<div class="input-group-label">Vital Signs (2 required observations)</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div style="margin-bottom: 1rem;"><em style="color: #65758B; font-size: 0.75rem;">Most recent observation</em></div>', unsafe_allow_html=True)

        vitals_t1 = get_vital_inputs(
            "Most recent",
            "v1",
            {"heart_rate": 104, "systolic_bp": 98, "respiratory_rate": 22, "temperature": 38.4, "spo2": 94}
        )

        st.markdown('<div style="margin: 1.5rem 0 1rem;"><em style="color: #65758B; font-size: 0.75rem;">Earlier observation (1–6 hours prior)</em></div>', unsafe_allow_html=True)

        vitals_t2 = get_vital_inputs(
            "1–6 hours earlier",
            "v2",
            {"heart_rate": 98, "systolic_bp": 105, "respiratory_rate": 20, "temperature": 37.8, "spo2": 95}
        )

        add_third_vital = st.checkbox("Add third vital observation (optional)", key="add_v3")
        vitals_t3 = None
        if add_third_vital:
            st.markdown('<div style="margin: 1rem 0 0.5rem;"><em style="color: #65758B; font-size: 0.75rem;">Third observation (2–6 hours prior)</em></div>', unsafe_allow_html=True)
            vitals_t3 = get_vital_inputs(
                "2–6 hours earlier",
                "v3",
                {"heart_rate": 92, "systolic_bp": 110, "respiratory_rate": 18, "temperature": 37.2, "spo2": 96}
            )

    with labs_col:
        st.markdown(
            '<div class="input-group-label">Laboratory Results (1–2 observations)</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div style="margin-bottom: 1rem;"><em style="color: #65758B; font-size: 0.75rem;">Most recent laboratory results</em></div>', unsafe_allow_html=True)

        labs_t1 = get_lab_inputs(
            "Most recent",
            "l1",
            {"lactate": 2.6, "wbc": 15.8, "crp": 85.0, "creatinine": 1.7, "platelets": 142}
        )

        add_second_lab = st.checkbox("Add earlier lab result (optional)", key="add_l2")
        labs_t2 = None
        if add_second_lab:
            st.markdown('<div style="margin: 1rem 0 0.5rem;"><em style="color: #65758B; font-size: 0.75rem;">Earlier lab result (12–24 hours prior)</em></div>', unsafe_allow_html=True)
            labs_t2 = get_lab_inputs(
                "12–24 hours earlier",
                "l2",
                {"lactate": 2.0, "wbc": 12.5, "crp": 65.0, "creatinine": 1.5, "platelets": 165}
            )

    return {
        "vitals_t1": vitals_t1,
        "vitals_t2": vitals_t2,
        "vitals_t3": vitals_t3,
        "labs_t1": labs_t1,
        "labs_t2": labs_t2,
    }


def validate_inputs(values: dict[str, Any]) -> list[str]:
    """Validate clinical inputs across all timepoints."""
    issues: list[str] = []

    for time_key in ["vitals_t1", "vitals_t2", "vitals_t3"]:
        if values.get(time_key):
            v = values[time_key]
            if not 34.0 <= v["temperature"] <= 42.0:
                issues.append(f"Temperature is outside plausible range (34.0–42.0 °C) in {time_key.replace('vitals_', 'vital observation ')}.")
            if not 70 <= v["spo2"] <= 100:
                issues.append(f"Oxygen saturation is outside plausible range (70–100%) in {time_key.replace('vitals_', 'vital observation ')}.")
            if not 40 <= v["systolic_bp"] <= 220:
                issues.append(f"Systolic BP is outside plausible range (40–220 mmHg) in {time_key.replace('vitals_', 'vital observation ')}.")

    for time_key in ["labs_t1", "labs_t2"]:
        if values.get(time_key):
            lab = values[time_key]
            if not 0.2 <= lab["lactate"] <= 15:
                issues.append(f"Lactate is outside plausible range (0.2–15.0 mmol/L) in {time_key.replace('labs_', 'lab observation ')}.")

    return issues


def call_prediction_api(patient_id: str, age: int, gender: str, comorbidity_count: int, observations: dict) -> dict[str, Any]:
    """Call the FastAPI backend to get sepsis risk prediction."""
    now = datetime.now()

    # Build vitals list with timestamps
    vitals = []
    if observations["vitals_t1"]:
        v1 = observations["vitals_t1"]
        vitals.append({
            "timestamp": now.isoformat(),
            "heart_rate": float(v1["heart_rate"]),
            "temperature": float(v1["temperature"]),
            "oxygen_saturation": float(v1["spo2"]),
            "respiratory_rate": float(v1["respiratory_rate"]),
            "blood_pressure": float(v1["systolic_bp"]),
        })

    if observations["vitals_t2"]:
        v2 = observations["vitals_t2"]
        vitals.append({
            "timestamp": (now - timedelta(hours=3)).isoformat(),
            "heart_rate": float(v2["heart_rate"]),
            "temperature": float(v2["temperature"]),
            "oxygen_saturation": float(v2["spo2"]),
            "respiratory_rate": float(v2["respiratory_rate"]),
            "blood_pressure": float(v2["systolic_bp"]),
        })

    if observations["vitals_t3"]:
        v3 = observations["vitals_t3"]
        vitals.append({
            "timestamp": (now - timedelta(hours=5)).isoformat(),
            "heart_rate": float(v3["heart_rate"]),
            "temperature": float(v3["temperature"]),
            "oxygen_saturation": float(v3["spo2"]),
            "respiratory_rate": float(v3["respiratory_rate"]),
            "blood_pressure": float(v3["systolic_bp"]),
        })

    # Build labs list with timestamps
    labs = []
    if observations["labs_t1"]:
        l1 = observations["labs_t1"]
        labs.append({
            "timestamp": now.isoformat(),
            "white_cell_count": float(l1["wbc"]),
            "crp": float(l1["crp"]),
            "lactate": float(l1["lactate"]),
            "creatinine": float(l1["creatinine"]),
            "platelet_count": float(l1["platelets"]),
        })

    if observations["labs_t2"]:
        l2 = observations["labs_t2"]
        labs.append({
            "timestamp": (now - timedelta(hours=18)).isoformat(),
            "white_cell_count": float(l2["wbc"]),
            "crp": float(l2["crp"]),
            "lactate": float(l2["lactate"]),
            "creatinine": float(l2["creatinine"]),
            "platelet_count": float(l2["platelets"]),
        })

    # Map gender to backend format
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


def gauge_svg(score: float, color: str) -> str:
    """Generate SVG gauge for risk score visualization."""
    radius = 76
    circumference = 2 * math.pi * radius
    progress = circumference * (score / 100) * 0.75
    return f"""
    <svg viewBox="0 0 200 150" role="img" aria-label="Risk score gauge">
      <path d="M 24 125 A 76 76 0 0 1 176 125" fill="none"
            stroke="rgba(255,255,255,0.14)" stroke-width="14" stroke-linecap="round"/>
      <path d="M 24 125 A 76 76 0 0 1 176 125" fill="none"
            stroke="{color}" stroke-width="14" stroke-linecap="round"
            stroke-dasharray="{progress:.2f} {circumference:.2f}"/>
      <text x="100" y="119" text-anchor="middle" fill="white"
            font-family="IBM Plex Mono, monospace" font-weight="600" font-size="10">RISK INDEX</text>
    </svg>
    """


def render_result(result: dict[str, Any] | None) -> None:
    """Render the prediction result panel."""
    if not result:
        st.markdown(
            """
            <div class="panel empty-result">
              <div class="empty-icon">--</div>
              <div class="empty-title">Awaiting a clinical assessment</div>
              <div class="empty-copy">
                Review the patient context and observations, then run an assessment
                to see a calibrated risk signal and its contributing factors.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # Map risk category to color
    category_colors = {
        "High": COLORS["high"],
        "Moderate": COLORS["moderate"],
        "Low": COLORS["low"],
    }

    score = result["sepsis_risk_score"] * 100
    category = result["risk_category"]
    color = category_colors.get(category, COLORS["moderate"])
    category_class = f"category-{category.lower()}"

    chips = "".join(
        f'<span class="factor-chip">{factor}</span>'
        for factor in result.get("key_risk_factors", ["No prominent indicators"])
    )

    st.markdown(
        f"""
        <div class="result-shell">
          <div class="result-kicker">Assessment complete</div>
          <div class="result-title">Sepsis risk signal</div>
          <p class="result-caption">Machine learning prediction from the values entered.</p>
          <div class="result-divider"></div>
          <div class="score-label">Risk score</div>
          <div class="score-number">{score:.0f}<span class="score-unit">/ 100</span></div>
          <div>{gauge_svg(score, color)}</div>
          <span class="category-badge {category_class}">{category} risk</span>
          <div class="result-divider"></div>
          <div class="factor-heading">Key risk factors</div>
          <div class="factor-list">{chips}</div>
          <div class="window-box">
            <div class="window-label">Prediction window</div>
            <div class="window-value">{result.get("prediction_window", "6-12 hours")}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> tuple[str, int, str, int]:
    """Render the sidebar with patient context."""
    with st.sidebar:
        st.markdown(
            """
            <div class="brand-lockup">
              <div class="brand-mark">E·</div>
              <div class="brand-name">elvara</div>
            </div>
            <div class="eyebrow">Clinical decision support</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="sidebar-section">Patient context</div>', unsafe_allow_html=True)
        patient_id = st.text_input("Patient identifier", value="ELV-2048", key="patient_id")
        age = st.number_input("Age", min_value=0, max_value=120, value=67, step=1, key="age")
        sex = st.selectbox(
            "Sex",
            ["Female", "Male", "Intersex / other", "Not recorded"],
            key="sex",
        )
        comorbidities = st.number_input(
            "Known comorbidities",
            min_value=0,
            max_value=20,
            value=2,
            step=1,
            key="comorbidities",
            help="Count of documented chronic conditions",
        )

        st.markdown('<div class="sidebar-section">Assessment details</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="context-card">
              <div class="context-label">Current patient</div>
              <div class="context-value">{patient_id or "Unassigned"}</div>
            </div>
            <div class="context-card">
              <div class="context-label">Last updated</div>
              <div class="context-value">{st.session_state.get("assessed_at", "Not yet assessed")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="sidebar-footer">
              ML-BASED ESTIMATOR<br>
              Predictions are generated by a trained machine learning model. This is not
              a diagnostic device and must be used alongside local clinical protocols and
              professional judgement.
            </div>
            """,
            unsafe_allow_html=True,
        )
    return patient_id, int(age), sex, int(comorbidities)


def main() -> None:
    inject_styles()
    patient_id, age, sex, comorbidities = render_sidebar()

    st.markdown(
        f"""
        <div class="page-header">
          <div>
            <div class="eyebrow">Patient assessment / {patient_id or "unassigned"}</div>
            <h1 class="page-title">Sepsis risk assessment</h1>
            <p class="page-subtitle">A focused view of physiological instability and associated risk.</p>
          </div>
          <div class="status-pill"><span class="status-dot"></span> ML model ready</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    observations = get_inputs()
    issues = validate_inputs(observations)

    if issues:
        st.markdown(
            '<div class="notice notice-error"><strong>Review before submitting</strong><br>'
            + "<br>".join(issues)
            + "</div>",
            unsafe_allow_html=True,
        )

    action_col, _ = st.columns([1, 2.2])
    with action_col:
        run_assessment = st.button("Run risk assessment", type="primary")

    if run_assessment:
        if issues:
            st.session_state["prediction_error"] = "Correct the flagged values before running an assessment."
            st.session_state["prediction"] = None
        else:
            st.session_state["prediction_error"] = None
            with st.spinner("Analyzing patient data with ML model…"):
                try:
                    prediction = call_prediction_api(patient_id, age, sex, comorbidities, observations)
                    st.session_state["prediction"] = prediction
                    st.session_state["assessed_at"] = datetime.now().strftime("%H:%M")
                except Exception as e:
                    st.session_state["prediction_error"] = f"Prediction service error: {str(e)}"
                    st.session_state["prediction"] = None

    error = st.session_state.get("prediction_error")
    if error:
        st.markdown(f'<div class="notice notice-error">{error}</div>', unsafe_allow_html=True)

    st.markdown('<div style="height: 1.65rem"></div>', unsafe_allow_html=True)
    section_heading("Result", "A summary for clinical review")
    result_col, note_col = st.columns([1.08, 0.92], gap="large")
    with result_col:
        render_result(st.session_state.get("prediction"))
    with note_col:
        st.markdown(
            """
            <div class="panel">
              <div class="input-group-label">How to read this view</div>
              <p style="color:#65758B;font-size:.82rem;line-height:1.55;margin:.6rem 0 0;">
                The score is a prioritisation signal, not a diagnosis. The category
                badge and written prediction window provide the at-a-glance summary;
                the chips show which observations contributed most to the estimate.
              </p>
              <div class="result-divider" style="border-color:#E3EAEF;margin:1.1rem 0;"></div>
              <div class="input-group-label">Signal thresholds</div>
              <div style="display:grid;gap:.7rem;margin-top:.75rem;">
                <div style="display:flex;align-items:center;gap:.55rem;font-size:.78rem;color:#65758B;">
                  <span style="width:9px;height:9px;border-radius:50%;background:#D64545"></span>
                  <strong style="color:#172333">High</strong> · ≥70%
                </div>
                <div style="display:flex;align-items:center;gap:.55rem;font-size:.78rem;color:#65758B;">
                  <span style="width:9px;height:9px;border-radius:50%;background:#E0A030"></span>
                  <strong style="color:#172333">Moderate</strong> · 35–69%
                </div>
                <div style="display:flex;align-items:center;gap:.55rem;font-size:.78rem;color:#65758B;">
                  <span style="width:9px;height:9px;border-radius:50%;background:#3FA66D"></span>
                  <strong style="color:#172333">Low</strong> · <35%
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        assessed_at = st.session_state.get("assessed_at")
        if assessed_at:
            st.markdown(
                f'<div class="disclaimer">Assessment generated at {assessed_at}. '
                "Use local clinical protocols and professional judgement.</div>",
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
