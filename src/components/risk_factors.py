"""Risk factors component for CADence."""

import streamlit as st
from typing import Dict
from src.constants.clinical_constants import RISK_FACTORS

def _initialize_state():
    """Initialize risk factor state if it doesn't exist."""
    if 'risk_factors_state' not in st.session_state:
        st.session_state.risk_factors_state = []
    
    if 'needs_recalculation' not in st.session_state:
        st.session_state.needs_recalculation = False

def _handle_risk_change():
    """Handle changes to risk factor selection."""
    st.session_state.needs_recalculation = True
    if 'manual_rf_cl_adjustment' in st.session_state:
        st.session_state.manual_rf_cl_adjustment = None
    # Update stored state
    if 'risk_factors' in st.session_state:
        st.session_state.risk_factors_state = st.session_state.risk_factors

def _get_risk_description(risk_factor: str) -> str:
    """
    Get the detailed description for a risk factor.
    
    Args:
        risk_factor: Name of the risk factor
        
    Returns:
        str: Detailed description of the risk factor
    """
    descriptions = {
                'Diabetes': """
        | Criterion | Definition |
        |-----------|------------|
        | Diagnosis | Type 1 or Type 2 Diabetes Mellitus |
        | Treatment | On medication or diet control |
        | Lab Values | HbA1c ≥6.5% (≥48 mmol/mol) OR  Random glucose ≥11.1 mmol/L |
                """,
                
                'Current/Past Smoking': """
        | Criterion | Definition |
        |-----------|------------|
        | Current smoker | Active smoking within the last year |
        | Past smoker | Quit >1 year ago |
        | Types | Includes vaping and e-cigarettes |
                """,
                
                'Hypertension': """
        | Criterion | Definition |
        |-----------|------------|
        | Blood Pressure | ≥140/90 mmHg on ≥2 occasions |
        | Treatment | On antihypertensive medication |
        | History | Documented history of hypertension |
                """,
                
                'Dyslipidemia': """
        | Criterion | Definition |
        |-----------|------------|
        | Total cholesterol | >5.2 mmol/L |
        | LDL | >3.4 mmol/L |
        | HDL | <1.0 mmol/L |
        | Treatment | On lipid-lowering medication |
                """,
                
                'Family History of Early CAD': """
        | Criterion | Definition |
        |-----------|------------|
        | Relationship | First-degree relative with premature CAD |
        | Male relative | <55 years |
        | Female relative | <65 years |
                """
    }
    
    return descriptions.get(risk_factor, "No detailed description available.")

def render_risk_factors() -> Dict[str, bool]:
    """
    Render the risk factors selection section.
    
    Returns:
        Dict[str, bool]: Dictionary mapping risk factor names to boolean values
    """
    # Initialize state
    _initialize_state()
    
    st.subheader("Risk Factors")
    
    # Present risk factors as selectable pills
    selected_risks = st.pills(
        label="Risk Factors",
        options=RISK_FACTORS,
        selection_mode="multi",
        default=st.session_state.risk_factors_state,
        key='risk_factors',
        on_change=_handle_risk_change,
        label_visibility="collapsed",
        help="Click to select risk factors. Hover over a risk factor for detailed criteria."
    )
    
    # Display help text in a help box below
    with st.expander("📋 Risk Factor Definitions", expanded=False):
        for rf in RISK_FACTORS:
            st.markdown(f"### {rf}")
            st.markdown(_get_risk_description(rf))
    
    # Convert selected risks to the format expected by calculations
    risk_factors = {
        'diabetes': "Diabetes" in selected_risks,
        'smoking': "Current/Past Smoking" in selected_risks,
        'hypertension': "Hypertension" in selected_risks,
        'dyslipidemia': "Dyslipidemia" in selected_risks,
        'family_history': "Family History of Early CAD" in selected_risks
    }
    
    return risk_factors