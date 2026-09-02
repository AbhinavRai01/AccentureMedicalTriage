# 🏥 PatientTriage.ai
> **Accenture Innovation Challenge 2026 – Problem Track 2**  
> **Team:** WeWillWin (Abhinav Rai, Karan Aditya, Jai A Mishra) | IIT Guwahati

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Flutter](https://img.shields.io/badge/Mobile-Flutter-02569B.svg)](https://flutter.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**PatientTriage.ai** is an AI-powered Emergency Department (ED) clinical decision-support layer designed to optimize patient sequencing and reduce wait times without replacing clinical judgment. Operating as a **Non-Device Clinical Decision Support (CDS)** tool, it maintains strict separation between predictive risk insights and medical diagnostics.

---

## 🌟 Core Architectural Principles

1. **Asymmetric Risk Optimization (Zero Undertriage)**
   Missing a critical case is categorically worse than over-prioritizing a minor one. Our machine learning layer utilizes asymmetric loss penalties during XGBoost model training to heavily penalize False Negatives (undertriage).
   * **Geriatric Agent (65+)**: $\alpha = 23.0$
   * **Adult Agent (18-64)**: $\alpha = 18.0$
   * **Pediatric Agent (<18)**: $\alpha = 28.0$

2. **Deterministic Safety Floors (ABCDE Rule Engine)**
   Predictive ML outputs are strictly bounded by ESI v5 deterministic clinical rule checks. Priority can only be automatically escalated, never downgraded without clinician action:
   > $$\text{Final\_ESI} = \min(\text{ML\_ESI\_Recommendation}, \text{ABCDE\_ESI\_Floor})$$

3. **Zero-History Resilience**
   Engineered to gracefully handle realistic ED constraints where over 50% of patients arrive with zero prior medical history.

4. **Dynamic Two-Stage Architecture**
   - **Stage 1 (Discrete UI Classification Gate)**: Discrete human-in-the-loop checkpoint displaying ESI level, Tree-Level confidence score, triggered ABCDE safety rules, and SHAP feature contributions.
   - **Stage 2 (Dynamic Priority Scheduler)**: Continuous Max Heap priority queue where sorting scores update dynamically with waiting time to prevent starvation.

---

## 🏗️ Repository Structure

```text
📦 AccentureMedicalTriage
 ┣ 📂 web                  # Core AI Engine, Backend API, and Streamlit Dashboard
 ┃ ┣ 📂 patienttriage      # Core Python Package (Rules, Models, Scheduler, Explainability)
 ┃ ┣ 📜 main.py            # Main entry point for CLI, API, UI, and Simulations
 ┃ ┣ 📜 README.md          # Detailed Technical Documentation
 ┃ ┗ 📜 requirements.txt   # Python dependencies
 ┣ 📂 mobile               # Flutter Mobile Client Application (Staff App)
 ┃ ┣ 📂 lib                # Dart codebase
 ┃ ┗ 📜 pubspec.yaml       # Flutter dependencies
 ┗ 📜 README.md            # You are here
```

---

## 🚀 Quick Start Guide

### 1. Web Application & AI Engine (Python)

Navigate to the `web` directory to launch the backend or the interactive dashboard.

```bash
cd web
pip install -r requirements.txt
```

**Run the Interactive Clinical Dashboard (Streamlit)**
```bash
python main.py --ui
```

**Run the RESTful API Server (FastAPI)**
```bash
python main.py --api
# API Docs available at: http://localhost:8000/docs
```

**Run Terminal Batch Triage Simulation**
```bash
python main.py --simulate
```

**Run Test Suite**
```bash
python main.py --test
```

### 2. Mobile Application (Flutter)

The `mobile` directory contains the staff-facing mobile application for on-the-go triage management.

```bash
cd mobile
flutter pub get
flutter run
```

---

## 🤖 Machine Learning Algorithms: Asymmetric XGBoost

The predictive engine uses **XGBoost** (Extreme Gradient Boosting), chosen for its high accuracy on tabular physiological data and native support for SHAP explainability. To ensure patient safety, we designed a **custom asymmetric logistic loss function**.

### The Custom Asymmetric Objective
In clinical triage, False Negatives (undertriage of a critical patient) are significantly more dangerous than False Positives (overtriage). Our custom objective function mathematically forces the model to heavily penalize False Negatives using a scaling factor, $\alpha$:

> $$ \text{Gradient} = p \cdot (\alpha \cdot y + \beta \cdot (1 - y)) - \alpha \cdot y $$
> $$ \text{Hessian} = p \cdot (1 - p) \cdot (\alpha \cdot y + \beta \cdot (1 - y)) $$

### Demographic-Calibrated Models
Instead of a single generalized model, the architecture routes patients to one of three age-stratified XGBoost agents, each calibrated with a unique $\alpha$ penalty and feature set:

1. **Geriatric Agent (Age 65+)**
   - **Penalty ($\alpha$)**: `23.0`
   - **Features**: Vital signs, comorbidities, prior history, and importantly, the **Clinical Frailty Scale (CFS)** score.
   - **Rationale**: Elderly patients often present atypically. A high penalty and frailty tracking suppress undertriage.

2. **Adult Agent (Age 18-64)**
   - **Penalty ($\alpha$)**: `18.0`
   - **Features**: Standard ED physiological vitals and history.
   - **Rationale**: Balances acute derangement detection against resource-wasting overtriage.

3. **Pediatric Agent (Age <18)**
   - **Penalty ($\alpha$)**: `28.0`
   - **Features**: Continuous age, vitals, and history.
   - **Rationale**: Pediatric vitals change rapidly and have different baselines depending on age. Carries the highest penalty multiplier due to rapid decompensation risks.

*(Hyperparameters: `max_depth=4` for shallow, highly interpretable trees; `learning_rate=0.01` to prevent overfitting; `threshold=0.504`)*

---

## 🧠 Technical Deep Dive: The Priority Scheduler

To prevent patient starvation (where lower-acuity patients wait indefinitely), our Stage 2 Priority Scheduler recalculates positions continuously using a time-decaying logarithmic function:

$$
\text{Priority Score}(t) = W_{\text{floor}} \cdot (6 - \text{ESI}_{\text{final}}) + W_{\text{risk}} \cdot P_{\text{risk}} + W_{\text{time}} \cdot \ln\left(1 + \frac{t_{\text{wait}}}{\tau}\right)
$$

| Weight | Value | Purpose |
|---|---|---|
| $W_{\text{floor}}$ | 1000 | Heavily weights the ESI base class |
| $W_{\text{risk}}$ | 100 | Granularly ranks patients within the same ESI |
| $W_{\text{time}}$ | 15 (Normal) / 30 (Surge) | Gradually elevates priority based on waiting time |
| $\tau$ | 30 | Time constant for logarithmic scaling |

---

## 🛡️ Governance, Compliance, & Explainability

- **Explainable AI (XAI)**: SHAP TreeExplainer extraction visually breaks down the physiological factors driving risk for every single patient.
- **Audit Trails**: Every manual override by a triage nurse is logged with clinician ID, timestamp, and rationale.
- **Hallucination Rejection**: Dedicated grounding validators ensure that structured JSON claims mathematically match SHAP attributions and raw physiological vitals before UI presentation.

---

*Built with ❤️ for the Accenture Innovation Challenge 2026*
