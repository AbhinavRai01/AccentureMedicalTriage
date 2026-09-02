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
    - Geriatric agent (65+): Penalty 23.0
    - Adult agent (18-64): Penalty 18.0
    - Pediatric agent (<18): Penalty 28.0

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

**Q: What machine learning algorithms are used?**

**A:** The predictive engine uses XGBoost (Extreme Gradient Boosting), chosen
for its high accuracy on tabular physiological data and native support for SHAP
explainability. To ensure patient safety, we designed a custom asymmetric
logistic loss function.

**Q: How does the custom asymmetric objective work?**

**A:** In clinical triage, False Negatives (undertriage of a critical patient)
are significantly more dangerous than False Positives (overtriage). Our custom
objective function mathematically forces the model to heavily penalize False
Negatives using a scaling factor.

**Q: How does the priority scheduler work?**

**A:** To prevent patient starvation (where lower-acuity patients wait
indefinitely), our Stage 2 priority scheduler recalculates positions
continuously using a time-decaying logarithmic function.


## Maintainers

- Abhinav Rai
- Karan Aditya
- Jai A Mishra
