"""
Ollama API Client Wrapper with Fallback Local Reasoning Engine.
Connects to local Ollama instance (gemma4:12b with think: false) for grounded clinical narrative synthesis,
with seamless zero-dependency deterministic fallback if Ollama is offline.
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional


class OllamaLLMClient:
    """
    Client for interacting with local Ollama service for Non-Device CDS synthesis.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "gemma4:12b",
        timeout: int = 15
    ):
        self.base_url = os.environ.get("OLLAMA_HOST", base_url).rstrip('/')
        self.model = os.environ.get("OLLAMA_MODEL", model)
        self.timeout = timeout
        self.is_connected = self._test_connection()

    def _test_connection(self) -> bool:
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.05)
            # Default Ollama port 11434
            res = s.connect_ex(('127.0.0.1', 11434))
            s.close()
            return res == 0
        except Exception:
            return False

    def generate_clinical_trace(
        self,
        patient_data: Dict[str, Any],
        ml_result: Dict[str, Any],
        rule_result: Dict[str, Any],
        shap_result: Dict[str, Any],
        final_esi: int
    ) -> Dict[str, Any]:
        """
        Generate grounded clinical reasoning trace using Ollama or fallback reasoner.
        """
        # If Ollama is online, query the local LLM
        if self.is_connected:
            try:
                system_prompt = (
                    "You are PatientTriage.ai, a non-device Clinical Decision Support assistant. "
                    "Synthesize a factual, grounded triage clinical assessment based strictly on the provided "
                    "ML predictions, SHAP feature rankings, and ESI v5 deterministic rules. Do not hallucinate. "
                    "Return a structured JSON summary."
                )
                
                payload = {
                    "model": self.model,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.1,
                        "think": False
                    },
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": json.dumps({
                                "patient": patient_data,
                                "ml_result": ml_result,
                                "rule_result": rule_result,
                                "shap_result": shap_result,
                                "final_esi": final_esi
                            })
                        }
                    ]
                }
                
                response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=self.timeout)
                if response.status_code == 200:
                    resp_json = response.json()
                    content = resp_json.get("message", {}).get("content", "")
                    parsed = json.loads(content)
                    return {
                        'provider': 'ollama',
                        'model': self.model,
                        'structured_narrative': parsed
                    }
            except Exception:
                pass

        # Deterministic Structured Reasoning Fallback
        return self._generate_deterministic_clinical_trace(
            patient_data, ml_result, rule_result, shap_result, final_esi
        )

    def _generate_deterministic_clinical_trace(
        self,
        patient_data: Dict[str, Any],
        ml_result: Dict[str, Any],
        rule_result: Dict[str, Any],
        shap_result: Dict[str, Any],
        final_esi: int
    ) -> Dict[str, Any]:
        """
        Deterministic, rigorously grounded template synthesis compliant with CDS standards.
        """
        age = patient_data.get('age', 35)
        cohort = ml_result.get('cohort', 'adult')
        p_risk = ml_result.get('p_risk', 0.0)
        ml_esi = ml_result.get('ml_esi_recommendation', 3)
        rule_floor = rule_result.get('acuity_floor', 5)
        triggered_rules = rule_result.get('triggered_rules', [])
        conf_score = ml_result.get('confidence_score', 100.0)
        req_review = ml_result.get('requires_human_review', False)
        
        top_features = shap_result.get('top_features', [])
        risk_increasing_factors = [f for f in top_features if f.get('is_risk_increasing', False)]
        protective_factors = [f for f in top_features if not f.get('is_risk_increasing', True)]

        # Acuity description
        esi_labels = {
            1: "ESI 1 (Resuscitation - Immediate Life-Saving Intervention Required)",
            2: "ESI 2 (Emergent / High Risk - Escalated Priority)",
            3: "ESI 3 (Urgent - Multiple Resources / Standard Priority)",
            4: "ESI 4 (Less Urgent - Single Resource)",
            5: "ESI 5 (Non-Urgent - Zero Resources)"
        }

        # Check alignment between ML and Rules
        if ml_esi == rule_floor:
            alignment_status = f"Consensus Alignment: Both ML model and ESI v5 deterministic rules agree on ESI {final_esi}."
        elif rule_floor < ml_esi:
            alignment_status = (
                f"Safety Floor Escalation: Deterministic clinical rule floor (ESI {rule_floor}) automatically "
                f"overrode ML prediction (ESI {ml_esi}) to prevent undertriage."
            )
        else:
            alignment_status = (
                f"ML Risk Escalation: Demographic XGBoost agent identified elevated critical risk "
                f"(P_risk={p_risk*100:.1f}%), escalating acuity to ESI {ml_esi}."
            )

        # Build feature rationale sentences
        feature_bulletins = []
        for f in top_features[:3]:
            feat = f['feature']
            val = f['value']
            shap_val = f['shap_value']
            ref = f.get('clinical_reference')
            dir_text = "elevating clinical risk" if shap_val > 0 else "reducing baseline risk"
            ref_text = f" (normal reference: {ref[0]}-{ref[1]})" if ref and isinstance(ref, list) else ""
            feature_bulletins.append(f"{feat.replace('_', ' ').title()} recorded at {val}{ref_text}, {dir_text} (SHAP: {shap_val:+.3f}).")

        trace_summary = {
            'final_esi_recommended': final_esi,
            'esi_label': esi_labels.get(final_esi, f"ESI {final_esi}"),
            'alignment_status': alignment_status,
            'risk_probability_pct': round(p_risk * 100.0, 1),
            'confidence_score_pct': conf_score,
            'requires_human_review': req_review,
            'primary_risk_factors': [
                {
                    'feature': f['feature'],
                    'value': f['value'],
                    'direction': 'increasing' if f['is_risk_increasing'] else 'decreasing',
                    'shap_impact': f['shap_value']
                }
                for f in top_features
            ],
            'triggered_safety_rules': triggered_rules,
            'clinical_rationale': (
                f"Patient ({age}y, {cohort}) evaluated under {cohort.capitalize()} XGBoost Agent and ESI v5 safety guidelines. "
                f"{alignment_status} " + " ".join(feature_bulletins)
            ),
            'governance_disclaimer': (
                "NON-DEVICE CLINICAL DECISION SUPPORT NOTICE: PatientTriage.ai provides contextualized risk estimates and "
                "safety floor bounds to assist triage sequencing. Final triage classification and clinical disposition "
                "remain the sole responsibility of the attending healthcare professional."
            )
        }

        return {
            'provider': 'deterministic_clinical_engine',
            'model': 'esi_v5_grounded_synthesizer',
            'structured_narrative': trace_summary
        }
