"""
Triage Orchestrator Loop.
Coordinates XGBoost inference, ESI v5 deterministic rules, SHAP explanations,
grounding validation, and clinical reasoning trace generation.
"""

import os
from typing import Dict, Any, Optional

from patienttriage.agent.tools import TriageToolsRegistry
from patienttriage.agent.llm_client import OllamaLLMClient
from patienttriage.explain.grounding import GroundingValidator
from patienttriage.scheduler.scoring import compute_priority_score


class TriageOrchestrator:
    """
    Main Clinical Decision Support orchestration engine.
    """

    def __init__(self, models_dir: Optional[str] = None, data_dir: Optional[str] = None):
        self.tools = TriageToolsRegistry(models_dir=models_dir, data_dir=data_dir)
        self.llm_client = OllamaLLMClient()
        self.validator = GroundingValidator()

    def analyze_patient(
        self,
        patient_data: Dict[str, Any],
        wait_time_mins: float = 0.0,
        is_surge: bool = False
    ) -> Dict[str, Any]:
        """
        Execute full PatientTriage.ai pipeline for an incoming ED patient.
        """
        patient_id = str(patient_data.get('patient_id', 'PID_UNKNOWN'))
        
        # 1. Predictive ML Risk Agent
        ml_result = self.tools.predict_esi_xgboost(patient_data)
        ml_esi = ml_result.get('ml_esi_recommendation', 3)
        p_risk = ml_result.get('p_risk', 0.0)
        confidence_score = ml_result.get('confidence_score', 100.0)
        requires_human_review = ml_result.get('requires_human_review', False)

        # 2. Deterministic ESI v5 Safety Floor
        rule_result = self.tools.run_esi_rule_engine(patient_data)
        rule_floor = rule_result.get('acuity_floor', 5)

        # 3. Apply Hard Deterministic Acuity Floor: Final_ESI = min(ML_ESI, Rule_Floor)
        final_esi = min(ml_esi, rule_floor)

        # 4. Assess Agreement State
        if ml_esi == rule_floor:
            agreement_state = "AGREEMENT"
        elif rule_floor < ml_esi:
            agreement_state = "RULE_SAFETY_ESCALATION"
        else:
            agreement_state = "ML_PREDICTIVE_ESCALATION"

        # 5. Compute SHAP Feature Attributions
        shap_result = self.tools.get_shap_explanation(patient_data, top_k=5)

        # 6. Compute Real-Time Heap Priority Score
        priority_score = compute_priority_score(
            esi_final=final_esi,
            p_risk=p_risk,
            t_wait_mins=wait_time_mins,
            is_surge=is_surge
        )

        # 7. Synthesize Grounded Clinical Narrative Trace
        trace_result = self.llm_client.generate_clinical_trace(
            patient_data=patient_data,
            ml_result=ml_result,
            rule_result=rule_result,
            shap_result=shap_result,
            final_esi=final_esi
        )

        narrative = trace_result.get('structured_narrative', {})

        # 8. Grounding Validation
        is_grounded, violations, audit_record = self.validator.validate_clinical_claims(
            raw_patient_data=patient_data,
            shap_explanation=shap_result,
            rule_engine_output=rule_result,
            generated_summary=narrative
        )

        # Flag mandatory review if low confidence OR ungrounded claim detected
        if not is_grounded:
            requires_human_review = True

        return {
            'patient_id': patient_id,
            'final_esi': final_esi,
            'ml_esi_recommendation': ml_esi,
            'rule_acuity_floor': rule_floor,
            'agreement_state': agreement_state,
            'p_risk': p_risk,
            'confidence_score': confidence_score,
            'requires_human_review': requires_human_review,
            'is_hard_locked': rule_result.get('is_hard_locked', False),
            'priority_score': priority_score,
            'wait_time_mins': wait_time_mins,
            'is_surge_active': is_surge,
            'ml_details': ml_result,
            'rule_details': rule_result,
            'shap_details': shap_result,
            'clinical_narrative': narrative,
            'grounding_audit': audit_record,
            'raw_patient_data': patient_data
        }

