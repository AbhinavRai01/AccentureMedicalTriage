# PatientTriage.ai

**Project:** Accenture Innovation Challenge 2026 – Problem Track 2  
**Team:** WeWillWin (Abhinav Rai, Karan Aditya, Jai A Mishra)  
**Institution:** Indian Institute of Technology (IIT) Guwahati  

---

## 1. Architectural Vision & Core Principles

**PatientTriage.ai** is an AI-powered Emergency Department (ED) clinical decision-support layer designed to optimize patient sequencing and reduce wait times without replacing clinical judgment.

- **Asymmetric Risk Optimization**: Missing a critical case is categorically worse than over-prioritizing a minor one. The machine learning layer utilizes asymmetric loss penalties during model training ($\alpha = 23.0$ for Geriatric, $\alpha = 18.0$ for Adult, $\alpha = 28.0$ for Pediatric) to heavily penalize False Negatives (undertriage).
- **Deterministic Safety Floors**: Predictive ML outputs are strictly bounded by ESI v5 deterministic clinical rule checks. Priority can only be automatically escalated, never downgraded without clinician action:
  $$\text{Final\_ESI} = \min(\text{ML\_ESI\_Recommendation}, \text{ABCDE\_ESI\_Floor})$$
- **Zero-History Resilience**: Engineered to gracefully handle realistic ED constraints where over 50% of patients arrive with zero prior medical history.
- **Two-Stage Architecture**:
  - **Stage 1 (Discrete UI Classification Gate)**: Discrete human-in-the-loop checkpoint displaying ESI level, Tree-Level confidence score, triggered ABCDE safety rules, and SHAP feature contributions.
  - **Stage 2 (Dynamic Priority Scheduler)**: Continuous Max Heap priority queue where sorting scores update dynamically with waiting time:
    $$\text{Priority Score}(t) = W_{\text{floor}} \cdot (6 - \text{ESI}_{\text{final}}) + W_{\text{risk}} \cdot P_{\text{risk}} + W_{\text{time}} \cdot \ln\left(1 + \frac{t_{\text{wait}}}{\tau}\right)$$
    with $W_{\text{floor}} = 1000, W_{\text{risk}} = 100, W_{\text{time}} = 15, \tau = 30$.

---

## 2. Tech Stack & Repository Structure

```
patienttriage/
├── models/
│   ├── geriatric_xgb.json       # Frailty-aware XGBoost model (65+, alpha=23.0)
│   ├── adult_xgb.json           # Acute derangement XGBoost model (18-64, alpha=18.0)
│   └── pediatric_xgb.json       # Pediatric risk XGBoost model (<18, alpha=28.0)
├── data/
│   └── esi_reference_tables.json # ESI v5 vital thresholds & age reference ranges
├── rule_engine/
│   ├── decision_a.py            # Immediate life threat check (ESI 1)
│   ├── decision_b.py            # Altered mental status / high risk check (ESI 2)
│   ├── decision_c.py            # Resource estimation & fallback handler
│   ├── decision_d.py            # Danger zone vital check (ESI 2) + Geriatric Frailty Guard
│   └── engine.py                # ABCDE safety floor aggregation
├── scheduler/
│   ├── scoring.py               # Priority Score continuous formula
│   └── max_heap.py              # Dynamic priority queue & surge manager
├── explain/
│   ├── shap_explainer.py        # SHAP TreeExplainer extraction
│   ├── uncertainty.py           # Tree-level ensemble variance score
│   └── grounding.py             # Structured JSON claim validator
├── agent/
│   ├── tools.py                 # Agent function schemas
│   ├── orchestrator.py          # Tool-calling loop & reasoning trace builder
│   └── llm_client.py            # Ollama API client wrapper & fallback engine
├── api/
│   └── main.py                  # FastAPI endpoints (/analyze-patient, /queue, /override)
├── ui/
│   └── app.py                   # Streamlit Interactive Dashboard
├── scripts/
│   ├── generate_data.py         # Synthetic ED dataset generator (6,230 cases)
│   └── train_models.py          # Asymmetric loss model trainer & exporter
└── tests/
    ├── test_rule_engine.py      # ESI handbook practice test cases
    ├── test_scheduler.py        # Heap sorting & surge tests
    ├── test_grounding.py        # Hallucination rejection unit tests
    └── test_api.py              # API endpoint integration tests
```

---

## 3. Quick Start & Execution

### Run Interactive Streamlit UI
```bash
python main.py --ui
```

### Run FastAPI Backend Server
```bash
python main.py --api
# API documentation available at http://localhost:8000/docs
```

### Run Terminal Batch Triage Simulation
```bash
python main.py --simulate
```

### Run Pytest Verification Suite
```bash
python -m pytest patienttriage/tests -v
```

---

## 4. CDS Regulatory Governance & Compliance
Operating as a **Non-Device Clinical Decision Support (CDS)** tool, PatientTriage.ai maintains strict separation between predictive risk insights and medical diagnostics. Clinicians maintain final override authority over all triage assignments.

