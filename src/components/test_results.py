"""Test results component."""

import streamlit as st
from typing import Dict, List, Optional
from src.constants.clinical_constants import AVAILABLE_TESTS, FFR_VALIDATED_TESTS
from src.state.session_state import SessionState

def render_test_results() -> Optional[Dict[str, str]]:
    """
    Render the test results section.
    
    Returns:
        Optional[Dict[str, str]]: Dictionary of test results if any tests are completed
    """
    test_results = None
    
    with st.expander("💉 Have results of prior testing?  \nEnter them here for a post-test probability", expanded=False):
        # FFR reference standard toggle
        st.toggle(
            "Use **FFR** Reference Standard instead of **ICA** Reference Standard",
            help="Toggle between anatomical (ICA) and functional (FFR) reference standards",
            key='use_ffr'
        )

        # CCTA Section with dedicated layout
        col1, col2 = st.columns([0.2, 0.80])
        with col1:
            ccta_done = st.checkbox(
                "CCTA", 
                key='ccta_checkbox',
                value=st.session_state.completed_tests['ccta_done'],
                on_change=SessionState.update_test_completion,
                args=('ccta',),
                help="""**High-risk features on CCTA include:**  \n- Left main disease with ≥50% stenosis  \n- Three-vessel disease with ≥70% stenosis  \n- Two-vessel disease with ≥70% stenosis including proximal LAD  \n- One-vessel proximal LAD disease with ≥70% stenosis and FFR-CT ≤0.8"""
            )

        if ccta_done:
            with col2:
                st.session_state.completed_tests['ccta_done'] = True
                ccta_result = st.toggle(
                    "CCTA Positive", 
                    key='ccta_result',
                    help="""**High-risk features on CCTA include:**  \n- Left main disease with ≥50% stenosis  \n- Three-vessel disease with ≥70% stenosis  \n- Two-vessel disease with ≥70% stenosis including proximal LAD  \n- One-vessel proximal LAD disease with ≥70% stenosis and FFR-CT ≤0.8""",
                    on_change=SessionState.update_ccta_result
                )

        # Show all 5 columns for tests
        test_cols = st.columns([0.20, 0.20, 0.20, 0.20, 0.20], gap="small")
        _render_anatomical_tests(test_cols)
        
        # Show info message only when FFR is active and no FFR-validated tests are selected
        if st.session_state.use_ffr:
            any_ffr_test_selected = any(
                st.session_state.completed_tests.get(f'{test}_done', False)
                for test in FFR_VALIDATED_TESTS
            )
            if not any_ffr_test_selected:
                st.info("Only SPECT, PET, and Stress CMR have been validated "
                       "against FFR as reference standard.")

        # Get valid test results
        test_results = _get_valid_test_results()
        
        if test_results:
            _render_test_results_metric(test_results)
            
    return test_results

def _render_anatomical_tests(columns: List[st.columns]) -> None:
    """Render all anatomical test inputs."""
    # Define all tests with their properties
    all_tests = [
        ('stress_ecg', 'Str-ECG', """**High-risk features on Stress ECG:**  \n• Duke Treadmill Score < −10"""),
        ('stress_echo', 'Str-Echo', """**High-risk features on Stress Echo:**  \n• ≥3 of 16 segments with stress-induced hypokinesia or akinesia"""),
        ('spect', 'SPECT', """**High-risk features on SPECT:**  \n• Area of ischaemia ≥10% of the LV myocardium"""),
        ('pet', 'PET', """**High-risk features on PET:**  \n• Area of ischaemia ≥10% of the LV myocardium"""),
        ('stress_cmr', 'Str-CMR', """**High-risk features on Stress CMR:**  \n• ≥2 of 16 segments with stress perfusion defects or  \n• ≥3 dobutamine-induced dysfunctional segments""")
    ]
    
    if st.session_state.use_ffr:
        # Filter and reposition FFR-validated tests to positions 0, 1, 2
        ffr_tests = [test for test in all_tests if test[0] in FFR_VALIDATED_TESTS]
        for i, (test, label, help_text) in enumerate(ffr_tests):
            with columns[i]:  # Use first 3 positions (0, 1, 2)
                _render_test_input(test, label, help_text)
    else:
        # Render all tests in their original positions
        for i, (test, label, help_text) in enumerate(all_tests):
            with columns[i]:
                _render_test_input(test, label, help_text)

def _render_test_input(test: str, label: str, help_text: str) -> None:
    """Render a single test input with checkbox and result selection."""
    test_done = st.checkbox(
        label, 
        key=f'{test}_checkbox',
        value=st.session_state.completed_tests[f'{test}_done'],
        on_change=SessionState.update_test_completion,
        args=(test,),
        help=help_text
    )
    
    if test_done:
        st.selectbox(
            'Result', 
            ['Positive', 'Negative'],
            key=f'{test}_key',
            on_change=SessionState.update_test_result,
            args=(test,),
            help=help_text
        )

def _get_valid_test_results() -> Optional[Dict[str, str]]:
    """Get dictionary of valid test results based on reference standard."""
    # Get completed tests with results
    test_results = {
        k: v for k, v in st.session_state.test_results.items() 
        if v and st.session_state.completed_tests.get(f'{k}_done', False)
    }
    
    # If using FFR reference standard, filter other tests to only FFR-validated ones
    # but always keep CCTA results if they exist
    if st.session_state.use_ffr:
        ccta_result = test_results.get('ccta')  # Store CCTA result if it exists
        test_results = {
            k: v for k, v in test_results.items()
            if k in FFR_VALIDATED_TESTS or k == 'ccta'
        }
    
    return test_results if test_results else None

def _render_test_results_metric(test_results: Dict[str, str]) -> None:
    """Render the post-test probability metric."""
    from src.utils.calculations import adjust_likelihood_for_test_results
    
    # Get base probability for calculation
    is_adjusted = st.session_state.manual_rf_cl_adjustment is not None
    asterisk = "*" if is_adjusted else ""
    
    if 'current_cacs_cl' in st.session_state:
        base_prob = st.session_state.current_cacs_cl
        label_prefix = "Post-Test"
        if is_adjusted:
            label_prefix += " **Adjusted**"
        label = f"{label_prefix} CACS-CL"
    else:
        if is_adjusted:
            base_prob = st.session_state.manual_rf_cl_adjustment
            label = "Post-Test **Adjusted** RF-CL"
        else:
            base_prob = st.session_state.current_rf_cl
            label = "Post-Test RF-CL"
    
    # Calculate adjusted probability
    reference = 'functional' if st.session_state.use_ffr else 'anatomical'
    adjusted_prob = adjust_likelihood_for_test_results(
        base_prob,
        test_results,
        reference
    )
    
    # Display metric
    st.metric(
        label,
        f"{adjusted_prob:.1f}%{asterisk}",
        delta=f"{adjusted_prob - base_prob:.1f}%"
    )