import re

with open('patienttriage/ui/app.py', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix the main header replacement that might have missed
c = c.replace(
    'Two-Stage Emergency Triage Decision Support & Continuous Max Heap Dynamic Priority Scheduler',
    'Live Decision Support Dashboard'
)

# Clean up leading spaces inside quotes like st.button(" Pop")
c = re.sub(r'\" (.*?)\"', r'"\1"', c)

# Some more robotic terms removal
c = c.replace('P_risk', 'Risk Probability')
c = c.replace('P(Risk)', 'Risk %')
c = c.replace('Continuous Formula:', 'Priority calculation:')
c = c.replace('ML_ESI', 'AI_ESI')
c = c.replace('ABCDE_Floor', 'Safety_Rules')
c = c.replace('Tree-Level Confidence', 'AI Confidence')
c = c.replace('Epistemic tree variance indicates high model uncertainty', 'The AI model is uncertain about this case')
c = c.replace('Asymmetric Loss Function Formulation', 'How we evaluate risk')
c = c.replace('Non-Device CDS Regulatory Positioning', 'Regulatory Information')
c = c.replace('Deterministic ESI v5 Rules Evaluation', 'Safety Rules')

with open('patienttriage/ui/app.py', 'w', encoding='utf-8') as f:
    f.write(c)
