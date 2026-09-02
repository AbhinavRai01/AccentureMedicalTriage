# PatientTriage.ai

PatientTriage.ai is an AI-powered Emergency Department (ED) clinical
decision-support layer designed to optimize patient sequencing and reduce wait
times without replacing clinical judgment. Operating as a Non-Device Clinical
Decision Support (CDS) tool, it maintains strict separation between predictive
risk insights and medical diagnostics.

This project was built for the Accenture Innovation Challenge 2026, Problem
Track 2 by Team WeWillWin (Abhinav Rai, Karan Aditya, Jai A Mishra from IIT
Guwahati).


## Table of contents

- Core architectural principles
- Machine learning models
- Screenshots
- Repository structure
- Requirements
- Recommended modules
- Installation
- Configuration
- Troubleshooting
- FAQ
- Maintainers


## Core architectural principles

1. Asymmetric risk optimization (Zero undertriage): Missing a critical case is
   categorically worse than over-prioritizing a minor one. Our machine learning
   layer utilizes asymmetric loss penalties during XGBoost model training to
   heavily penalize False Negatives (undertriage).

1. Deterministic safety floors (ABCDE rule engine): Predictive ML outputs are
   strictly bounded by ESI v5 deterministic clinical rule checks. Priority can
   only be automatically escalated, never downgraded without clinician action.

1. Zero-history resilience: Engineered to gracefully handle realistic ED
   constraints where over 50% of patients arrive with zero prior medical
   history.

1. Dynamic two-stage architecture:
    - Stage 1 (Discrete UI classification gate): Discrete human-in-the-loop
      checkpoint displaying ESI level, Tree-Level confidence score, triggered
      ABCDE safety rules, and SHAP feature contributions.
    - Stage 2 (Dynamic priority scheduler): Continuous Max Heap priority queue
      where sorting scores update dynamically with waiting time to prevent
      starvation.


## Machine learning models

The predictive engine is the core of PatientTriage.ai and relies on **XGBoost
(Extreme Gradient Boosting)**. It was chosen for its exceptional accuracy on
tabular physiological data and its native support for SHAP explainability. 

### The custom asymmetric objective

In clinical triage, False Negatives (undertriage of a critical patient) are
significantly more dangerous than False Positives (overtriage). To ensure
uncompromising patient safety, we designed a custom asymmetric logistic loss
function. This objective mathematically forces the model to heavily penalize
False Negatives using a scaling factor, alpha ($\alpha$):

- **Gradient**: $p \cdot (\alpha \cdot y + \beta \cdot (1 - y)) - \alpha \cdot y$
- **Hessian**: $p \cdot (1 - p) \cdot (\alpha \cdot y + \beta \cdot (1 - y))$

### Demographic-calibrated models

Instead of relying on a single generalized model, the architecture intelligently
routes patients to one of three age-stratified XGBoost agents. Each agent is
calibrated with a unique penalty ($\alpha$) and a specialized feature set:

1. **Geriatric agent (Age 65+)**
   - **Penalty ($\alpha$)**: `23.0`
   - **Features**: Vital signs, comorbidities, prior history, and importantly,
     the Clinical Frailty Scale (CFS) score.
   - **Rationale**: Elderly patients often present atypically. A high penalty
     and frailty tracking suppress undertriage.

1. **Adult agent (Age 18-64)**
   - **Penalty ($\alpha$)**: `18.0`
   - **Features**: Standard ED physiological vitals and history.
   - **Rationale**: Balances acute derangement detection against resource-wasting
     overtriage.

1. **Pediatric agent (Age <18)**
   - **Penalty ($\alpha$)**: `28.0`
   - **Features**: Continuous age, vitals, and history.
   - **Rationale**: Pediatric vitals change rapidly and have different baselines
     depending on age. Carries the highest penalty multiplier due to rapid
     decompensation risks.

*Model hyperparameters*: `max_depth=4` for shallow, highly interpretable trees;
`learning_rate=0.01` to prevent overfitting; `threshold=0.504`.


## Screenshots

![Screenshot 1](images/Screenshot%202026-09-02%20183247.png)

![Screenshot 2](images/Screenshot%202026-09-02%20183349.png)

![Screenshot 3](images/Screenshot%202026-09-02%20183424.png)

![Screenshot 4](images/Screenshot%202026-09-02%20183513.png)

![Screenshot 5](images/Screenshot%202026-09-02%20183543.png)

![Screenshot 6](images/Screenshot%202026-09-02%20204914.png)

![Screenshot 7](images/Screenshot%202026-09-02%20204948.png)


## Repository structure

- web: Core AI engine, backend API, and Streamlit dashboard.
    - patienttriage: Core Python package (rules, models, scheduler).
    - main.py: Main entry point for CLI, API, UI, and simulations.
- mobile: Flutter mobile client application (staff app).


## Requirements

This project requires the following environments:

- [Python 3.10+](https://www.python.org/downloads/)
- [Flutter](https://flutter.dev/)


## Recommended modules

No recommended modules.


## Installation

1. Navigate to the `web` directory to launch the backend or the interactive
   dashboard.
1. Install Python dependencies:
   `pip install -r requirements.txt`
1. Navigate to the `mobile` directory for the staff-facing mobile application.
1. Install Flutter dependencies:
   `flutter pub get`


## Configuration

Run the web application and AI engine:

- Interactive clinical dashboard (Streamlit): `python main.py --ui`
- RESTful API server (FastAPI): `python main.py --api`
- Terminal batch triage simulation: `python main.py --simulate`
- Test suite: `python main.py --test`

Run the mobile application:

- In the `mobile` directory: `flutter run`


## Troubleshooting

If the application does not load or you encounter issues during installation or
execution, check the following:

- Are the correct versions of Python and Flutter installed?
- Have all dependencies in `requirements.txt` and `pubspec.yaml` been
  successfully resolved?


## FAQ

**Q: How does the priority scheduler work?**

**A:** To prevent patient starvation (where lower-acuity patients wait
indefinitely), our Stage 2 priority scheduler recalculates positions
continuously using a time-decaying logarithmic function.


**Q: How is model governance and explainability handled?**

**A:** Explainable AI (XAI) using SHAP TreeExplainer extraction visually breaks
down the physiological factors driving risk for every single patient. Dedicated
grounding validators ensure that structured JSON claims mathematically match
SHAP attributions before UI presentation.


## Maintainers

- Abhinav Rai
- Karan Aditya
- Jai A Mishra

