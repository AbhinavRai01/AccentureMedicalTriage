"""
Unit tests for Grounding Validator and Hallucination Rejection.
Tests mathematical verification of clinical narrative claims against empirical SHAP values,
raw patient vitals, and deterministic ESI v5 safety floors.
"""

import pytest
from patienttriage.explain.grounding import GroundingValidator


@pytest.fixture
def sample_grounding_context():
    raw_patient = {
        'age': 50,
        'heart_rate': 110.0,
        'resp_rate': 18.0,
        'spo2': 98.0,
        'sbp': 130.0,
        'cfs_frailty_score': 2
    }
    
    shap_explanation = {
        'top_features': [
            {'feature': 'heart_rate', 'value': 110.0, 'shap_value': 0.85, 'is_risk_increasing': True},
            {'feature': 'spo2', 'value': 98.0, 'shap_value': -0.42, 'is_risk_increasing': False}
        ],
        'all_features_shap': [
            {'feature': 'heart_rate', 'value': 110.0, 'shap_value': 0.85, 'is_risk_increasing': True},
            {'feature': 'resp_rate', 'value': 18.0, 'shap_value': -0.10, 'is_risk_increasing': False},
            {'feature': 'spo2', 'value': 98.0, 'shap_value': -0.42, 'is_risk_increasing': False}
        ]
    }
    
    rule_output = {
        'acuity_floor': 2,
        'triggered_rules': ["Decision Point D (Adult/Geriatric): Tachycardia (HR 110 > 100 bpm)"],
        'is_hard_locked': True
    }
    
    return raw_patient, shap_explanation, rule_output


def test_valid_clinical_claims_pass_grounding(sample_grounding_context):
    """Test correctly formulated grounded clinical summary passes validation."""
    raw, shap, rules = sample_grounding_context
    
    valid_summary = {
        'recommended_esi': 2,
        'primary_risk_factors': [
            {'feature': 'heart_rate', 'value': 110.0, 'direction': 'increasing'}
        ],
        'triggered_safety_rules': [
            "Decision Point D (Adult/Geriatric): Tachycardia"
        ]
    }
    
    is_valid, violations, audit = GroundingValidator.validate_clinical_claims(
        raw, shap, rules, valid_summary
    )
    
    assert is_valid is True
    assert len(violations) == 0
    assert audit['is_grounded'] is True


def test_hallucination_of_protective_feature_as_risk_is_rejected(sample_grounding_context):
    """Test hallucination claiming normal/protective SpO2 increased risk is caught."""
    raw, shap, rules = sample_grounding_context
    
    hallucinatory_summary = {
        'recommended_esi': 2,
        'primary_risk_factors': [
            {'feature': 'spo2', 'value': 98.0, 'direction': 'increasing'}  # False: SpO2 98% has negative SHAP!
        ]
    }
    
    is_valid, violations, audit = GroundingValidator.validate_clinical_claims(
        raw, shap, rules, hallucinatory_summary
    )
    
    assert is_valid is False
    assert any("SHAP Direction Violation" in v for v in violations)


def test_acuity_floor_violation_is_rejected(sample_grounding_context):
    """Test claim that assigns ESI 4 when safety floor is ESI 2 is caught."""
    raw, shap, rules = sample_grounding_context
    
    invalid_floor_summary = {
        'recommended_esi': 4,  # Violates floor ESI 2!
        'primary_risk_factors': []
    }
    
    is_valid, violations, audit = GroundingValidator.validate_clinical_claims(
        raw, shap, rules, invalid_floor_summary
    )
    
    assert is_valid is False
    assert any("Acuity Grounding Violation" in v for v in violations)


def test_numerical_mismatch_is_rejected(sample_grounding_context):
    """Test claiming heart rate was 140 when raw record was 110 is caught."""
    raw, shap, rules = sample_grounding_context
    
    mismatched_summary = {
        'recommended_esi': 2,
        'primary_risk_factors': [
            {'feature': 'heart_rate', 'value': 140.0, 'direction': 'increasing'}  # Actual is 110
        ]
    }
    
    is_valid, violations, audit = GroundingValidator.validate_clinical_claims(
        raw, shap, rules, mismatched_summary
    )
    
    assert is_valid is False
    assert any("Numerical Fidelity Violation" in v for v in violations)

