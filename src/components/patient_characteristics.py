"""Patient characteristics component."""

import streamlit as st
from typing import Tuple
from src.utils.validators import validate_age

def _initialize_state():
    """Initialize all state variables if they don't exist."""
    if 'age' not in st.session_state:
        st.session_state.age = 55
    
    if 'gender' not in st.session_state:
        st.session_state.gender = "Male"
        
    if 'symptom_type_state' not in st.session_state:
        st.session_state.symptom_type_state = "Chest Pain"
        
    if 'chest_pain_criteria_state' not in st.session_state:
        st.session_state.chest_pain_criteria_state = [
            "Substernal chest discomfort",
            "Provoked by exertion/stress",
            "Relieved by rest/nitroglycerin"
        ]
        
    if 'dyspnea_state' not in st.session_state:
        st.session_state.dyspnea_state = False
        
    if 'needs_recalculation' not in st.session_state:
        st.session_state.needs_recalculation = False

def _handle_age_change():
    """Handle age changes."""
    st.session_state.needs_recalculation = True
    if 'manual_rf_cl_adjustment' in st.session_state:
        st.session_state.manual_rf_cl_adjustment = None

def _handle_gender_change():
    """Handle gender changes."""
    st.session_state.needs_recalculation = True
    if 'manual_rf_cl_adjustment' in st.session_state:
        st.session_state.manual_rf_cl_adjustment = None

def _handle_symptom_type_change():
    """Handle symptom type changes."""
    st.session_state.needs_recalculation = True
    if 'manual_rf_cl_adjustment' in st.session_state:
        st.session_state.manual_rf_cl_adjustment = None
    # Update the stored state with the selected value or default to "Chest Pain"
    if 'symptom_type' in st.session_state:
        st.session_state.symptom_type_state = st.session_state.symptom_type or "Chest Pain"

def _handle_chest_pain_criteria_change():
    """Handle chest pain criteria changes."""
    st.session_state.needs_recalculation = True
    if 'manual_rf_cl_adjustment' in st.session_state:
        st.session_state.manual_rf_cl_adjustment = None
    # Update the stored state
    if 'chest_pain_criteria' in st.session_state:
        st.session_state.chest_pain_criteria_state = st.session_state.chest_pain_criteria

def _handle_dyspnea_change():
    """Handle dyspnea toggle changes."""
    st.session_state.needs_recalculation = True
    if 'manual_rf_cl_adjustment' in st.session_state:
        st.session_state.manual_rf_cl_adjustment = None
    # Update the stored state
    if 'exertional_dyspnea' in st.session_state:
        st.session_state.dyspnea_state = st.session_state.exertional_dyspnea

def render_patient_characteristics() -> Tuple[int, int, str]:
    """
    Render the patient characteristics section of the app.
    
    Returns:
        Tuple of (age, sex_binary, symptoms)
    """
    # Initialize all state variables
    _initialize_state()
    
    st.subheader("Patient Characteristics")
    
    # Age and gender input
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        age = st.slider(
            "Age",
            min_value=18,
            max_value=100,
            value=st.session_state.age,
            step=1,
            key='age',
            help="The risk models were validated for ages 30-79. Results outside this range should be interpreted with caution.",
            on_change=_handle_age_change
        )
    with col2:
        sex = st.radio(
            "Gender",
            options=["Male", "Female"],
            horizontal=True,
            key='gender',
            on_change=_handle_gender_change
        )
        
    # Validate age and show warning if needed
    is_valid, warning = validate_age(age)
    if warning:
        st.warning(f"⚠️ {warning}")
        
    # Symptom type selection with state management
    symptom_type = st.pills(
        "Select Primary Symptom:",
        ["Chest Pain", "Dyspnoea"],
        selection_mode="single",
        default=st.session_state.symptom_type_state,
        key='symptom_type',
        on_change=_handle_symptom_type_change
    )

    # If no selection, default to Chest Pain
    symptom_type = symptom_type or "Chest Pain"
    
    # Initialize symptoms variable
    symptoms = "non_anginal"  # default value
    
    # Show appropriate inputs based on symptom type
    if symptom_type == "Chest Pain":
        symptoms_criteria = st.pills(
            "Chest Pain Classification (select all which apply):",
            [
                "Substernal chest discomfort",
                "Provoked by exertion/stress",
                "Relieved by rest/nitroglycerin"
            ],
            selection_mode="multi",
            default=st.session_state.chest_pain_criteria_state,
            key='chest_pain_criteria',
            on_change=_handle_chest_pain_criteria_change
        )
        
        num_criteria = len(symptoms_criteria)
        
        if num_criteria == 3:
            symptoms = "typical"
            st.error("**Typical Angina** (all 3 characteristics present)")
        elif num_criteria == 2:
            symptoms = "atypical"
            st.warning("**Atypical Angina** (2 of 3 characteristics present)")
        else:
            symptoms = "non_anginal"
            st.success("**Non-anginal Chest Pain** (0-1 characteristics present)")
            
    elif symptom_type == "Dyspnoea":
        exertional_dyspnea = st.toggle(
            "Shortness of breath and/or trouble catching breath "
            "aggravated by physical exertion",
            value=st.session_state.dyspnea_state,
            key='exertional_dyspnea',
            help="Select if dyspnea is primarily exertional",
            on_change=_handle_dyspnea_change
        )
        
        if exertional_dyspnea:
            symptoms = "atypical"  # Treat as atypical angina
        else:
            symptoms = "non_anginal"  # Treat as non-anginal
    
    sex_binary = 1 if sex == "Male" else 0
    
    # Store current values in session state
    st.session_state.current_age = age
    st.session_state.current_sex_binary = sex_binary
    st.session_state.current_symptoms = symptoms
    
    return age, sex_binary, symptoms