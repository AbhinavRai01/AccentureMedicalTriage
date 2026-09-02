"""
PatientTriage.ai - Streamlit Interactive Clinical Decision Support & Dynamic Scheduler Dashboard
Accenture Innovation Challenge 2026 - Problem Track 2
Team: WeWillWin (Abhinav Rai, Karan Aditya, Jai A Mishra) - IIT Guwahati
"""

import os
import json
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st

from patienttriage.agent.orchestrator import TriageOrchestrator
from patienttriage.scheduler.max_heap import DynamicMaxHeapQueue
from patienttriage.scripts.generate_data import generate_synthetic_triage_data

# Page configuration
st.set_page_config(
  page_title="PatientTriage.ai | Emergency Decision Support",
  page_icon="",
  layout="wide",
  initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
  }
  .main-header {
    font-size: 2.2rem;
    font-weight: 700;
    color: #005137; /* primary */
    margin-bottom: 0.2rem;
    letter-spacing: -0.01em;
  }
  .sub-header {
    font-size: 1.05rem;
    color: #3f4943; /* on-surface-variant */
    margin-bottom: 1.5rem;
  }
  .esi-badge-1 { background-color: #ba1a1a; color: white; padding: 6px 14px; border-radius: 0.25rem; font-weight: bold; font-size: 1.3rem; } /* triage-critical */
  .esi-badge-2 { background-color: #dc2c4f; color: white; padding: 6px 14px; border-radius: 0.25rem; font-weight: bold; font-size: 1.3rem; } /* triage-urgent */
  .esi-badge-3 { background-color: #ffdad6; color: #93000a; padding: 6px 14px; border-radius: 0.25rem; font-weight: bold; font-size: 1.3rem; } /* error-container / warning */
  .esi-badge-4 { background-color: rgba(255,255,255,0.7); color: #3f4943; border: 1px solid #bec9c1; padding: 6px 14px; border-radius: 0.25rem; font-weight: bold; font-size: 1.3rem; } /* glassmorphic neutral */
  .esi-badge-5 { background-color: rgba(255,255,255,0.7); color: #3f4943; border: 1px solid #bec9c1; padding: 6px 14px; border-radius: 0.25rem; font-weight: bold; font-size: 1.3rem; } /* glassmorphic neutral */
  .metric-box {
    background-color: rgba(255, 255, 255, 0.7); /* surface-glass */
    border: 1px solid #dfe4de; /* surface-variant */
    padding: 12px;
    border-radius: 0.5rem; /* rounded-lg */
    margin-bottom: 10px;
    backdrop-filter: blur(12px);
  }
  .cds-disclaimer {
    font-size: 0.8rem;
    color: #5c5f61; /* secondary */
    border-left: 3px solid #005137; /* primary */
    padding-left: 10px;
    margin-top: 20px;
  }
  /* Advanced Streamlit widget styling to match Clinical Glass Tailwind design */
  .stApp {
    background-color: #f6faf5;
    background-image: 
      radial-gradient(circle at 100% 0%, rgba(0, 81, 55, 0.05) 0%, transparent 40%),
      radial-gradient(circle at 0% 100%, rgba(222, 224, 226, 0.2) 0%, transparent 40%);
  }
  [data-testid="stSidebar"] {
    background-color: #f1f5ef !important;
    border-right: 1px solid rgba(190, 201, 193, 0.3);
  }
  [data-testid="stHeader"] {
    background-color: rgba(255, 255, 255, 0.7) !important;
    backdrop-filter: blur(12px) !important;
    box-shadow: 0 1px 8px rgba(0,0,0,0.04) !important;
  }
  .stButton > button {
    background: linear-gradient(to right, #005137, #006c4a);
    color: white !important;
    border: none !important;
    border-radius: 9999px !important;
    padding: 0.5rem 1.5rem !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 6px -1px rgba(0, 81, 55, 0.2) !important;
    transition: all 0.3s ease !important;
  }
  .stButton > button:hover {
    box-shadow: 0 10px 15px -3px rgba(0, 81, 55, 0.3) !important;
    transform: translateY(-1px) !important;
  }
  [data-testid="stForm"] {
    background-color: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(12px);
    border: 0px solid transparent;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    border-radius: 1rem;
    padding: 1.5rem;
  }
  .stTextInput > div > div > input, 
  .stNumberInput > div > div > input, 
  .stSelectbox > div > div > select, 
  .stTextArea > div > textarea {
    background-color: #ebefea !important;
    border: 1px solid transparent !important;
    border-radius: 0.75rem !important;
    color: #181d1a !important;
    padding: 0.75rem 1rem !important;
    transition: all 0.2s !important;
  }
  .stTextInput > div > div > input:focus, 
  .stNumberInput > div > div > input:focus, 
  .stSelectbox > div > div > select:focus, 
  .stTextArea > div > textarea:focus {
    border-color: #9df4c9 !important;
    box-shadow: 0 0 0 2px rgba(157, 244, 201, 0.2) !important;
  }
  /* Custom tabs styling */
  [data-testid="stTabs"] [data-baseweb="tab-list"] {
    background-color: #ebefea;
    border-radius: 0.75rem;
    padding: 0.25rem;
    gap: 0.5rem;
  }
  [data-testid="stTabs"] [data-baseweb="tab"] {
    background-color: transparent;
    border-radius: 0.5rem;
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
    font-weight: 600;
    border: none !important;
  }
  [data-testid="stTabs"] [aria-selected="true"] {
    background-color: white !important;
    color: #005137 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  }
  /* Style columns to look like the tailwind layout cards */
  div[data-testid="column"] {
    background-color: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(12px);
    border: 1px solid #dfe4de;
    border-radius: 1rem;
    padding: 1.25rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    margin-bottom: 1rem;
  }
  /* Style native metrics */
  [data-testid="stMetricValue"] {
    font-size: 2.2rem !important;
    font-weight: 700 !important;
    color: #181d1a !important;
  }
  [data-testid="stMetricLabel"] {
    font-size: 14px !important;
    font-weight: 600 !important;
    color: #5c5f61 !important;
    text-transform: uppercase;
    letter-spacing: 0.02em;
  }
</style>
""", unsafe_allow_html=True)


# Initialize Session State
if 'orchestrator' not in st.session_state:
  st.session_state.orchestrator = TriageOrchestrator()

if 'scheduler' not in st.session_state:
  st.session_state.scheduler = DynamicMaxHeapQueue(surge_threshold=15)
  # Populate initial queue with 8 realistic patients
  df_init = generate_synthetic_triage_data(n_samples=8, random_seed=42)
  for _, row in df_init.iterrows():
    p = row.to_dict()
    res = st.session_state.orchestrator.analyze_patient(
      patient_data=p,
      wait_time_mins=float(p.get('current_wait_time_mins', 10.0)),
      is_surge=False
   )
    st.session_state.scheduler.add_patient(
      patient_id=res['patient_id'],
      esi_final=res['final_esi'],
      p_risk=res['p_risk'],
      wait_time_mins=res['wait_time_mins'],
      age=int(p.get('age', 35)),
      age_cohort=res['ml_details'].get('cohort', 'adult'),
      gender=p.get('gender', 'Unknown'),
      chief_complaint=f"Clinical Presentation ({p.get('age_cohort', 'adult').capitalize()})",
      has_prior_history=int(p.get('has_prior_history', 0)),
      confidence_score=res['confidence_score'],
      requires_human_review=res['requires_human_review'],
      vital_signs={
        'heart_rate': p.get('heart_rate'),
        'resp_rate': p.get('resp_rate'),
        'spo2': p.get('spo2'),
        'sbp': p.get('sbp'),
        'temp_c': p.get('temp_c'),
        'cfs_frailty_score': p.get('cfs_frailty_score')
      }
   )

if 'last_analysis' not in st.session_state:
  st.session_state.last_analysis = None


# --- SIDEBAR ---
with st.sidebar:
  st.markdown("""
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0"rel="stylesheet"/>
  <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
    <span class="material-symbols-outlined"style="color: #005137; font-size: 32px;">clinical_notes</span>
    <span style="font-size: 20px; font-weight: 600; color: #005137; letter-spacing: -0.01em;">PatientTriage.ai</span>
  </div>
  """, unsafe_allow_html=True)
  st.markdown("**Accenture Innovation Challenge 2026**")
  st.caption("Team: WeWillWin | IIT Guwahati")
  st.divider()

  st.markdown("#### :material/tune: Real-Time ED Controls")
  
  # Surge toggle
  surge_toggle = st.toggle("Enable Surge Mode", value=st.session_state.scheduler.surge_mode)
  if surge_toggle != st.session_state.scheduler.surge_mode:
    st.session_state.scheduler.set_surge_mode(surge_toggle)
    st.rerun()

  # Time Advancement
  st.markdown("**Advance Simulation Time**")
  col_t1, col_t2 = st.columns(2)
  with col_t1:
    if st.button(":material/fast_forward: +5 Mins", use_container_width=True):
      st.session_state.scheduler.advance_time(5.0)
      st.rerun()
  with col_t2:
    if st.button(":material/fast_forward: +15 Mins", use_container_width=True):
      st.session_state.scheduler.advance_time(15.0)
      st.rerun()

  st.divider()
  st.markdown("#### Priority Rules Active")
  st.success("Geriatric Patients (65+)")
  st.success("Adult Patients (18-64)")
  st.success("Pediatric Patients (<18)")

  st.divider()
  if st.button(":material/group_add: Load Sample Patients", use_container_width=True):
    st.session_state.scheduler.clear()
    df_demo = generate_synthetic_triage_data(n_samples=12, random_seed=999)
    for _, row in df_demo.iterrows():
      p = row.to_dict()
      res = st.session_state.orchestrator.analyze_patient(
        patient_data=p,
        wait_time_mins=float(p.get('current_wait_time_mins', 5.0)),
        is_surge=st.session_state.scheduler.is_surge_active()
     )
      st.session_state.scheduler.add_patient(
        patient_id=res['patient_id'],
        esi_final=res['final_esi'],
        p_risk=res['p_risk'],
        wait_time_mins=res['wait_time_mins'],
        age=int(p.get('age', 35)),
        age_cohort=res['ml_details'].get('cohort', 'adult'),
        gender=p.get('gender', 'Unknown'),
        chief_complaint="ED Triage Presentation",
        has_prior_history=int(p.get('has_prior_history', 0)),
        confidence_score=res['confidence_score'],
        requires_human_review=res['requires_human_review'],
        vital_signs={
          'heart_rate': p.get('heart_rate'),
          'resp_rate': p.get('resp_rate'),
          'spo2': p.get('spo2'),
          'sbp': p.get('sbp'),
          'temp_c': p.get('temp_c'),
          'cfs_frailty_score': p.get('cfs_frailty_score')
        }
     )
    st.rerun()

  if st.button(":material/delete: Clear Queue", use_container_width=True):
    st.session_state.scheduler.clear()
    st.rerun()


# --- HEADER ---
st.markdown("""
<div style="position: absolute; top: 0px; right: 0px; display: flex; align-items: center; gap: 1rem; padding: 10px;">
  <div style="text-align: right; line-height: 1.2;">
    <p style="margin: 0; font-size: 14px; font-weight: 600; color: #181d1a;">Dr. Sarah Chen</p>
    <p style="margin: 0; font-size: 12px; color: #3f4943;">ER Senior Lead</p>
  </div>
  <div style="width: 40px; height: 40px; border-radius: 50%; background-color: #005137; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(0, 81, 55, 0.2); color: white; font-weight: bold;">
    SC
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="margin-top: 10px; margin-bottom: 20px;">
  <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
    <span style="background-color: #dfe4de; color: #3f4943; padding: 2px 10px; border-radius: 9999px; font-size: 12px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;">
      Emergency Department
    </span>
    <div style="width: 4px; height: 4px; border-radius: 50%; background-color: rgba(0, 81, 55, 0.4);"></div>
    <span style="color: #5c5f61; font-size: 12px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;">
      Live Decision Support
    </span>
  </div>
  <h1 style="font-size: 32px; font-weight: 700; color: #181d1a; margin: 0; letter-spacing: -0.01em; line-height: 1.2;">PatientTriage.ai</h1>
  <p style="font-size: 16px; color: #5c5f61; margin-top: 8px; margin-bottom: 0;">Live Decision Support Dashboard</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
  ":material/assignment: Patient Intake",
  ":material/list_alt: Waiting Room Queue",
  ":material/verified: Governance & Audit"
])


# =========================================================================
# TAB 1: PATIENT INTAKE & TRIAGE ANALYSIS
# =========================================================================
with tab1:
  st.markdown("### 1. Clinical Intake & Physiological Vitals Assessment")
  
  # Preset scenarios for quick demo testing
  preset_cols = st.columns(6)
  preset_chosen = None
  with preset_cols[0]:
    if st.button(":material/ecg: Cardiac Arrest", use_container_width=True):
      preset_chosen = "cardiac_arrest"
  with preset_cols[1]:
    if st.button(":material/neurology: Stroke / STEMI", use_container_width=True):
      preset_chosen = "stroke"
  with preset_cols[2]:
    if st.button(":material/elderly: Frail Elderly", use_container_width=True):
      preset_chosen = "frail_elderly"
  with preset_cols[3]:
    if st.button(":material/child_care: Febrile Infant", use_container_width=True):
      preset_chosen = "pediatric_fever"
  with preset_cols[4]:
    if st.button(":material/person_alert: Borderline Adult", use_container_width=True):
      preset_chosen = "borderline_adult"
  with preset_cols[5]:
    if st.button(":material/healing: Minor Sprain", use_container_width=True):
      preset_chosen = "minor_sprain"

  # Default form values
  def_age = 45
  def_cohort = "adult"
  def_gender = "Female"
  def_cfs = 2
  def_history = 1
  def_comorb = 1
  def_hr = 82.0
  def_rr = 16.0
  def_spo2 = 98.0
  def_sbp = 125.0
  def_temp = 37.1
  def_complaint = "Acute abdominal pain and nausea"
  def_req_life = 0
  def_high_risk = 0
  def_ams = 0
  def_severe_pain = 0
  def_chest_pain = 0
  def_stroke = 0
  def_resources = 2

  if preset_chosen == "cardiac_arrest":
    def_age = 62
    def_cohort = "adult"
    def_hr = 0.0
    def_rr = 0.0
    def_spo2 = 65.0
    def_sbp = 40.0
    def_complaint = "Unresponsive, apneic, pulseless collapse"
    def_req_life = 1
  elif preset_chosen == "stroke":
    def_age = 71
    def_cohort = "geriatric"
    def_cfs = 4
    def_hr = 104.0
    def_rr = 22.0
    def_spo2 = 93.0
    def_sbp = 185.0
    def_complaint = "Sudden right-sided facial droop and arm weakness (FAST+)"
    def_stroke = 1
    def_high_risk = 1
  elif preset_chosen == "frail_elderly":
    def_age = 84
    def_cohort = "geriatric"
    def_cfs = 7
    def_history = 0 # Zero history test!
    def_comorb = 0
    def_hr = 96.0 # >90 triggers Frailty Guard!
    def_rr = 19.0
    def_spo2 = 94.0
    def_sbp = 115.0
    def_temp = 37.8
    def_complaint = "Generalized weakness, poor oral intake, borderline lethargy"
  elif preset_chosen == "pediatric_fever":
    def_age = 3
    def_cohort = "pediatric"
    def_hr = 148.0 # >140 for toddler triggers Ped Danger Zone!
    def_rr = 38.0  # >35 for toddler triggers Ped Danger Zone!
    def_spo2 = 91.0 # <92% hypoxia
    def_sbp = 82.0
    def_temp = 39.4
    def_complaint = "High fever, rapid grunting respirations, decreased activity"
  elif preset_chosen == "borderline_adult":
    def_age = 34
    def_cohort = "adult"
    def_hr = 88.0
    def_rr = 18.0
    def_spo2 = 97.0
    def_sbp = 120.0
    def_temp = 37.5
    def_complaint = "Moderate abdominal cramps, requires lab work and CT scan"
    def_resources = 2
  elif preset_chosen == "minor_sprain":
    def_age = 24
    def_cohort = "adult"
    def_hr = 72.0
    def_rr = 14.0
    def_spo2 = 99.0
    def_sbp = 118.0
    def_temp = 36.8
    def_complaint = "Twisted ankle while jogging, ambulatory with mild swelling"
    def_resources = 1

  with st.form("patient_intake_form"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
      st.markdown("##### :material/person: Demographics")
      p_id = st.text_input("Patient Identifier", value=f"PID_{np.random.randint(10000, 99999)}")
      age = st.number_input("Age (Years)", min_value=0.1, max_value=115.0, value=float(def_age), step=1.0)
      
      # Cohort auto-selection based on age
      if age < 18:
        cohort_default_idx = 0
      elif age >= 65:
        cohort_default_idx = 2
      else:
        cohort_default_idx = 1

      cohort = st.selectbox("Demographic Age Cohort", ["pediatric", "adult", "geriatric"], index=cohort_default_idx)
      gender = st.selectbox("Gender", ["Female", "Male", "Other"], index=0 if def_gender=="Female" else 1)
      
      has_history = st.radio("Intake History Status", [1, 0], format_func=lambda x: "Verified Records Present"if x==1 else "Zero-History / Unverified Baseline (50% ED Case)", index=0 if def_history==1 else 1)
      comorbidity = st.number_input("Comorbidity Count", min_value=0, max_value=10, value=int(def_comorb))
      cfs = st.slider("Clinical Frailty Scale (CFS: 1=Robust, 9=Terminally Ill)", min_value=1, max_value=9, value=int(def_cfs))

    with col2:
      st.markdown("##### :material/monitor_heart: Vitals")
      hr = st.number_input("Heart Rate (BPM)", min_value=0.0, max_value=250.0, value=float(def_hr), step=1.0)
      rr = st.number_input("Respiratory Rate (Breaths/min)", min_value=0.0, max_value=80.0, value=float(def_rr), step=1.0)
      spo2 = st.number_input("Oxygen Saturation SpO2 (%)", min_value=40.0, max_value=100.0, value=float(def_spo2), step=0.5)
      sbp = st.number_input("Systolic Blood Pressure SBP (mmHg)", min_value=30.0, max_value=260.0, value=float(def_sbp), step=1.0)
      temp_c = st.number_input("Body Temperature (°C)", min_value=30.0, max_value=44.0, value=float(def_temp), step=0.1)
      wait_time = st.number_input("Current Elapsed Wait Time (Mins)", min_value=0.0, max_value=600.0, value=15.0, step=5.0)

    with col3:
      st.markdown("##### :material/medical_services: Clinical Context")
      complaint = st.text_area("Presenting Complaint / Clinical Context", value=def_complaint, height=70)
      
      st.markdown("**Decision Point A/B Checklist:**")
      req_life = st.checkbox("Immediate life-saving intervention / Agonal / Pulseless (ESI 1)", value=bool(def_req_life))
      high_risk = st.checkbox("High risk presentation / Severe acute distress (ESI 2)", value=bool(def_high_risk))
      ams = st.checkbox("Altered mental status / Acute disorientation / GCS < 14 (ESI 2)", value=bool(def_ams))
      chest_pain = st.checkbox("Acute ischemic chest pain / STEMI suspect (ESI 2)", value=bool(def_chest_pain))
      stroke_sym = st.checkbox("Acute stroke symptoms / FAST+ (ESI 2)", value=bool(def_stroke))
      
      st.markdown("**Decision Point C: Expected Resources:**")
      resources = st.selectbox(
        "Resource Estimation", 
        [2, 1, 0, -1], 
        format_func=lambda x: "2+ Resources: Labs, CT/X-Ray, IV meds (ESI 3)"if x==2 else ("1 Resource: X-Ray or Simple Suturing (ESI 4)"if x==1 else ("0 Resources: Exam/Prescription Only (ESI 5)"if x==0 else "Insufficient Data (Arrival intake uncollected)")),
        index=0 if def_resources==2 else (1 if def_resources==1 else 2)
     )

    submit_intake = st.form_submit_button(":material/analytics: Analyze Patient", use_container_width=True)

  if submit_intake or preset_chosen:
    patient_data = {
      'patient_id': p_id,
      'age': float(age),
      'age_cohort': cohort,
      'gender': gender,
      'cfs_frailty_score': int(cfs),
      'has_prior_history': int(has_history),
      'comorbidity_count': int(comorbidity),
      'heart_rate': float(hr),
      'resp_rate': float(rr),
      'spo2': float(spo2),
      'sbp': float(sbp),
      'temp_c': float(temp_c),
      'chief_complaint': complaint,
      'requires_lifesaving_intervention': 1 if req_life else 0,
      'high_risk_situation': 1 if high_risk else 0,
      'altered_mental_status': 1 if ams else 0,
      'acute_chest_pain_ischemic': 1 if chest_pain else 0,
      'acute_stroke_symptoms': 1 if stroke_sym else 0,
      'resources_used': None if resources == -1 else resources
    }

    with st.spinner("Analyzing patient data..."):
      analysis = st.session_state.orchestrator.analyze_patient(
        patient_data=patient_data,
        wait_time_mins=float(wait_time),
        is_surge=st.session_state.scheduler.is_surge_active()
     )
      st.session_state.last_analysis = analysis

  # Render Analysis Results
  if st.session_state.last_analysis is not None:
    res = st.session_state.last_analysis
    st.divider()
    st.markdown("### 2. Stage 1 Triage Determination & Explainability Gate")

    # Top Metric Banner
    res_col1, res_col2, res_col3, res_col4, res_col5 = st.columns(5)
    
    final_esi = res['final_esi']
    badge_class = f"esi-badge-{final_esi}"
    
    with res_col1:
      st.markdown(f"**Final Acuity Determination**")
      st.markdown(f"<span class='{badge_class}'>ESI LEVEL {final_esi}</span>", unsafe_allow_html=True)
      if res.get('is_hard_locked'):
        st.caption("Deterministically Safety Floor Locked")

    with res_col2:
      st.metric(
        label="Raw Risk Probability (Risk Probability)",
        value=f"{res['p_risk']*100:.1f}%",
        delta=f"Threshold: 50.4%",
        delta_color="inverse"if res['p_risk'] >= 0.504 else "normal"
     )

    with res_col3:
      conf_val = res['confidence_score']
      st.metric(
        label="AI Confidence",
        value=f"{conf_val:.1f}%",
        delta="Mandatory Review (<20%)"if conf_val < 20.0 else "High Consensus",
        delta_color="off"if conf_val >= 20.0 else "inverse"
     )

    with res_col4:
      st.metric(
        label="Stage 2 Priority Score",
        value=f"{res['priority_score']:.1f} pts",
        delta=f"Wait: {res['wait_time_mins']} min"
     )

    with res_col5:
      ag_state = res['agreement_state']
      if ag_state == "AGREEMENT":
        st.success("ML & Rules Consensus")
      elif ag_state == "RULE_SAFETY_ESCALATION":
        st.warning("Rule Floor Escalated")
      else:
        st.info("ML Risk Escalated")

    # Mandatory Review Alert
    if res['requires_human_review']:
      st.error("**MANDATORY HUMAN OVERRIDE CHECKPOINT**: The AI model is uncertain about this case (<20% confidence) or unverified history conflict. Attendee clinician sign-off required.")

    # SHAP & Safety Rules Row
    exp_col1, exp_col2 = st.columns([3, 2])
    
    with exp_col1:
      st.markdown("####What influenced this decision?")
      top_shaps = res['shap_details'].get('top_features', [])
      if top_shaps:
        shap_df = pd.DataFrame(top_shaps)
        shap_df['feature_clean'] = shap_df['feature'].str.replace('_', ' ').str.title()
        
        chart = alt.Chart(shap_df).mark_bar().encode(
          x=alt.X('shap_value:Q', title='SHAP Impact on Clinical Risk (Log-Odds)'),
          y=alt.Y('feature_clean:N', sort='-x', title='Clinical Feature'),
          color=alt.Color('is_risk_increasing:N', scale=alt.Scale(domain=[True, False], range=['#dc2c4f', '#31C231']), legend=alt.Legend(title="Impact", labelExpr="datum.value ? 'Elevates Risk' : 'Protective / Normal'")),
          tooltip=['feature_clean', 'value', 'shap_value', 'cohort_band']
       ).properties(height=260)
        st.altair_chart(chart, use_container_width=True)

    with exp_col2:
      st.markdown("####Clinical Safety Checks")
      triggered = res['rule_details'].get('triggered_rules', [])
      if triggered:
        for rule_text in triggered:
          st.info(f"{rule_text}")
      else:
        st.caption("No acute ABCDE red flags triggered. Acuity governed by standard resource pathways.")
      
      st.markdown(f"**ML Recommendation**: ESI {res['ml_esi_recommendation']} | **Safety Floor**: ESI {res['rule_acuity_floor']}")
      st.caption("Rule Engine Equation: Final_ESI = min(AI_ESI, Safety_Rules)")

    # Clinical Narrative Trace
    st.markdown("####Clinical Summary")
    narrative = res.get('clinical_narrative', {})
    st.markdown(f"*{narrative.get('clinical_rationale', 'Clinical rationale synthesized.')}*")
    
    audit_info = res.get('grounding_audit', {})
    if audit_info.get('is_grounded'):
      st.success(f"**Grounding Validator Passed**: All {len(audit_info.get('verified_facts', []))} clinical claims mathematically verified against SHAP attributions and raw physiological vitals.")
    else:
      st.error(f"**Grounding Violations Detected**: {', '.join(audit_info.get('violations', []))}")

    # Add to Queue Button
    st.markdown("---")
    add_col1, add_col2 = st.columns([2, 3])
    with add_col1:
      if st.button(":material/person_add: Add Patient to Waiting Room", type="primary", use_container_width=True):
        st.session_state.scheduler.add_patient(
          patient_id=res['patient_id'],
          esi_final=res['final_esi'],
          p_risk=res['p_risk'],
          wait_time_mins=res['wait_time_mins'],
          age=int(res['raw_patient_data'].get('age', 35)),
          age_cohort=res['ml_details'].get('cohort', 'adult'),
          gender=res['raw_patient_data'].get('gender', 'Unknown'),
          chief_complaint=res['raw_patient_data'].get('chief_complaint', 'General ED presentation'),
          has_prior_history=int(res['raw_patient_data'].get('has_prior_history', 0)),
          confidence_score=res['confidence_score'],
          requires_human_review=res['requires_human_review'],
          vital_signs={
            'heart_rate': res['raw_patient_data'].get('heart_rate'),
            'resp_rate': res['raw_patient_data'].get('resp_rate'),
            'spo2': res['raw_patient_data'].get('spo2'),
            'sbp': res['raw_patient_data'].get('sbp'),
            'temp_c': res['raw_patient_data'].get('temp_c'),
            'cfs_frailty_score': res['raw_patient_data'].get('cfs_frailty_score')
          }
       )
        st.success(f"Patient {res['patient_id']} added to Waiting Room Queue! Switch to Stage 2 tab to view real-time rank.")


# =========================================================================
# TAB 2: DYNAMIC PRIORITY QUEUE (MAX HEAP)
# =========================================================================
with tab2:
  st.markdown("###Waiting Room Priority Queue")
  
  queue_list = st.session_state.scheduler.get_ranked_queue()
  
  # Summary Metrics Row
  q_col1, q_col2, q_col3, q_col4 = st.columns(4)
  with q_col1:
    st.metric("Total Patients Waiting", len(queue_list))
  with q_col2:
    surge_active = st.session_state.scheduler.is_surge_active()
    st.metric("Surge Mode Status", "ACTIVE (3x)"if surge_active else "NORMAL", delta="W_time = 30"if surge_active else "W_time = 15")
  with q_col3:
    high_acuity_count = sum(1 for p in queue_list if p['esi_final'] <= 2)
    st.metric("Critical / Emergent (ESI 1-2)", high_acuity_count)
  with q_col4:
    pending_review_count = sum(1 for p in queue_list if p['requires_human_review'])
    st.metric("Pending Nurse Review", pending_review_count, delta_color="inverse")

  st.markdown("#### Real-Time Waiting Room Queue")
  st.caption("Priority calculation: Priority Score(t) = W_floor × (6 - ESI) + W_risk × Risk Probability + W_time × ln(1 + t_wait / 30)")

  if queue_list:
    # Display Table
    table_rows = []
    for p in queue_list:
      table_rows.append({
        "Rank": f"#{p['queue_rank']}",
        "Patient ID": p['patient_id'],
        "Acuity Level": f"ESI {p['esi_final']}",
        "Risk %": f"{p['p_risk']*100:.1f}%",
        "Wait Time": f"{p['wait_time_mins']:.1f} min",
        "Priority Score": f"{p['priority_score']:.1f}",
        "Cohort / Age": f"{p['age_cohort'].capitalize()} ({p['age']}y)",
        "Review Flag": "Review Required" if p['requires_human_review'] else "Verified",
        "Override Status": f"Overridden ({p['override_reason']})" if p['is_overridden'] else "Auto-Triaged"
      })
    
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

    # Actions Section: Pop next / Overrides / Deterioration
    st.divider()
    action_col1, action_col2 = st.columns(2)

    with action_col1:
      st.markdown("####Next Patient to See")
      top_p = queue_list[0]
      st.info(f"**Next in Line for Bed Assignment**: Patient **{top_p['patient_id']}** (Rank #1, ESI {top_p['esi_final']}, Priority Score {top_p['priority_score']:.1f})")
      if st.button(":material/notifications_active: Call Next Patient", type="primary", use_container_width=True):
        popped = st.session_state.scheduler.pop_next_patient()
        st.success(f"Called {popped.patient_id} into ED examination room. Queue re-indexed.")
        st.rerun()

    with action_col2:
      st.markdown("####Clinical Override")
      patient_ids = [p['patient_id'] for p in queue_list]
      override_target_id = st.selectbox("Select Patient to Override", patient_ids)
      override_new_esi = st.selectbox("Assign New ESI Acuity", [1, 2, 3, 4, 5], index=1)
      override_reason = st.text_input("Override Rationale (Required for Audit Trail)", value="Clinical intuition / Observed subtle frailty")
      
      if st.button("Submit Clinician Override", use_container_width=True):
        st.session_state.scheduler.record_nurse_override(
          patient_id=override_target_id,
          new_esi=override_new_esi,
          reason=override_reason,
          clinician_id="Triage_Nurse_Lead"
       )
        st.success(f"Override applied! Patient {override_target_id} updated to ESI {override_new_esi} and queue re-sorted.")
        st.rerun()
  else:
    st.info("Waiting room queue is currently empty. Use the intake tab or sidebar button to add patients.")


# =========================================================================
# TAB 3: GOVERNANCE & AUDIT TRAIL
# =========================================================================
with tab3:
  st.markdown("### Clinical Decision Support (CDS) Governance & Compliance")
  
  st.markdown("""
  ##### 1. Regulatory Information
  PatientTriage.ai operates strictly as a **Non-Device Clinical Decision Support (CDS)** software tool.
  - **No Autonomous Diagnostic Decisions**: All predictive outputs are formatted as contextualized risk indicators and deterministic safety bounds.
  - **Deterministic Safety Guarantee**: Predictive ML outputs are strictly bounded by ESI v5 deterministic rules ($Final\_ESI = \min(ML\_ESI, ABCDE\_Floor)$).
  - **Mandatory Human-in-the-Loop**: Clinicians retain unrestricted authority to override any AI suggestion, with all overrides recorded into the immutable audit trail.
  - **Local-First PHI Privacy**: All model inferences, SHAP calculations, and rule checks execute entirely on the local deployment target.
  """)

  st.markdown("##### 2. Nurse Override Audit Log")
  audit_log = st.session_state.scheduler.override_audit_log
  if audit_log:
    st.dataframe(pd.DataFrame(audit_log), use_container_width=True)
  else:
    st.caption("No manual clinician overrides logged in current session.")

  st.markdown("##### 3. How we evaluate risk")
  st.latex(r"""
  \mathcal{L}_{\text{asym}}(y, p) = - \left[\alpha \cdot y \log(p) + \beta \cdot (1 - y) \log(1 - p) \right]
  """)
  st.markdown("""
  - **Geriatric Agent (65+)**: $\alpha = 23.0, \beta = 1.0$ (Heavily suppresses False Negatives to protect high-risk elders)
  - **Adult Agent (18-64)**: $\alpha = 18.0, \beta = 1.0$ (Balances acute derangement against overtriage)
  - **Pediatric Agent (<18)**: $\alpha = 28.0, \beta = 1.0$ (Highest penalty multiplier for rapid pediatric decompensation risks)
  """)

  st.markdown('<div class="cds-disclaimer">DISCLAIMER: For clinical demonstration and decision support only. Not for standalone automated diagnosis.</div>', unsafe_allow_html=True)

