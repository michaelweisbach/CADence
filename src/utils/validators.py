"""Input validation utilities for the CADence app."""

from typing import Dict, List, Tuple, Optional
from src.constants.clinical_constants import MIN_AGE, MAX_AGE, VALIDATED_AGE_RANGE

def validate_age(age: int) -> Tuple[bool, Optional[str]]:
    """
    Validate the input age.
    
    Args:
        age: Patient age
        
    Returns:
        Tuple of (is_valid, warning_message)
    """
    if not MIN_AGE <= age <= MAX_AGE:
        return False, f"Age must be between {MIN_AGE} and {MAX_AGE}"
    
    if not VALIDATED_AGE_RANGE[0] <= age <= VALIDATED_AGE_RANGE[1]:
        return True, (
            f"The risk models were validated for ages {VALIDATED_AGE_RANGE[0]}-"
            f"{VALIDATED_AGE_RANGE[1]}. Results outside this range should be "
            "interpreted with caution."
        )
    
    return True, None

def validate_risk_factors(risk_factors: Dict[str, bool]) -> Tuple[bool, Optional[str]]:
    """
    Validate the risk factors dictionary.
    
    Args:
        risk_factors: Dictionary of risk factors and their presence
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_factors = {
        'diabetes', 'smoking', 'hypertension', 
        'dyslipidemia', 'family_history'
    }
    
    if not all(factor in risk_factors for factor in required_factors):
        return False, "Missing required risk factors"
        
    if not all(isinstance(value, bool) for value in risk_factors.values()):
        return False, "Risk factor values must be boolean"
        
    return True, None

def validate_test_results(
    test_results: Dict[str, str],
    reference_standard: str
) -> Tuple[bool, Optional[str]]:
    """
    Validate test results dictionary.
    
    Args:
        test_results: Dictionary of test names and their results
        reference_standard: 'anatomical' or 'functional'
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_results = {'Positive', 'Negative', ''}
    
    if not all(result in valid_results for result in test_results.values()):
        return False, "Invalid test result value"
        
    if reference_standard not in {'anatomical', 'functional'}:
        return False, "Invalid reference standard"
        
    return True, None