import re

with open('patienttriage/ui/app.py', 'r', encoding='utf-8') as f:
    c = f.read()

repl = {
    '"Enable Surge Mode (3x Volume Scaling)"': '":material/speed: Enable Surge Mode (3x Volume Scaling)"',
    '"Advance Simulation Time"': '":material/schedule: Advance Simulation Time"',
    '"Priority Rules Active"': '":material/admin_panel_settings: Priority Rules Active"',
    '"Load Sample Patients"': '":material/group_add: Load Sample Patients"',
    '"Clear Queue"': '":material/delete: Clear Queue"',
    '"Patient Intake"': '":material/assignment: Patient Intake"',
    '"Waiting Room Queue"': '":material/list_alt: Waiting Room Queue"',
    '"Governance & Audit"': '":material/verified: Governance & Audit"',
    '"Analyze Patient"': '":material/analytics: Analyze Patient"',
    '"Add Patient to Waiting Room"': '":material/person_add: Add Patient to Waiting Room"',
    '"Next Patient to See"': '":material/meeting_room: Next Patient to See"',
    '"Call Next Patient"': '":material/notifications_active: Call Next Patient"',
    '"Clinical Override"': '":material/edit_note: Clinical Override"',
    '##### Demographics': '##### :material/person: Demographics',
    '##### Vitals': '##### :material/monitor_heart: Vitals',
    '##### Clinical Context': '##### :material/medical_services: Clinical Context',
    '"Cardiac Arrest"': '":material/ecg: Cardiac Arrest"',
    '"Stroke / STEMI"': '":material/neurology: Stroke / STEMI"',
    '"Frail Elderly"': '":material/elderly: Frail Elderly"',
    '"Febrile Infant"': '":material/child_care: Febrile Infant"',
    '"Borderline Adult"': '":material/person_alert: Borderline Adult"',
    '"Minor Sprain"': '":material/healing: Minor Sprain"',
    '#### What influenced this decision?': '#### :material/science: What influenced this decision?',
    '#### Safety Rules': '#### :material/security: Safety Rules',
    '#### Clinical Summary': '#### :material/summarize: Clinical Summary',
    '"+5 Mins"': '":material/fast_forward: +5 Mins"',
    '"+15 Mins"': '":material/fast_forward: +15 Mins"',
    'Real-Time ED Controls': ':material/tune: Real-Time ED Controls',
}

for k, v in repl.items():
    c = c.replace(k, v)

with open('patienttriage/ui/app.py', 'w', encoding='utf-8') as f:
    f.write(c)
