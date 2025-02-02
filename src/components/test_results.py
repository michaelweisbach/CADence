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
                help="""**High-risk features on CCTA include:**  \n- Left main disease with ≥50% stenosis  \n- Three-vessel disease with ≥70% stenosis  \n- Two-vessel disease with ≥70% stenosis including proximal LAD  \n- One-vessel proximal LAD disease with ≥70% stenosis and FFR-CT ≤0.8
                """
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

        # Create columns for functional tests
        test_cols = st.columns([0.20, 0.20, 0.20, 0.20, 0.20], gap="small")

        if not st.session_state.use_ffr:
            # Show all tests for anatomical reference
            _render_anatomical_tests(test_cols)
        else:
            # Show only FFR-validated tests
            _render_ffr_tests(test_cols)

        # Get valid test results
        test_results = _get_valid_test_results()
        
        if test_results:
            _render_test_results_metric(test_results)
            
    return test_results

def _render_anatomical_tests(columns: List[st.columns]) -> None:
    """Render all anatomical test inputs."""
    tests = [
        ('stress_ecg', 'Str-ECG', """**High-risk features on Stress ECG:**  \n• Duke Treadmill Score < −10"""),
        ('stress_echo', 'Str-Echo', """**High-risk features on Stress Echo:**  \n• ≥3 of 16 segments with stress-induced hypokinesia or akinesia"""),
        ('spect', 'SPECT', """**High-risk features on SPECT:**  \n• Area of ischaemia ≥10% of the LV myocardium"""),
        ('pet', 'PET', """**High-risk features on PET:**  \n• Area of ischaemia ≥10% of the LV myocardium"""),
        ('stress_cmr', 'Str-CMR', """**High-risk features on Stress CMR:**  \n• ≥2 of 16 segments with stress perfusion defects or  \n• ≥3 dobutamine-induced dysfunctional segments""")
    ]
    
    for (test, label, help_text), col in zip(tests, columns):
        with col:
            _render_test_input(test, label, help_text)

def _render_ffr_tests(columns: List[st.columns]) -> None:
    """Render only FFR-validated test inputs."""
    tests = [
        ('stress_ecg', 'Str-ECG', """**High-risk features on Stress ECG:**  \n• Duke Treadmill Score < −10"""),
        ('stress_echo', 'Str-Echo', """**High-risk features on Stress Echo:**  \n• ≥3 of 16 segments with stress-induced hypokinesia or akinesia"""),
        ('spect', 'SPECT', """**High-risk features on SPECT:**  \n• Area of ischaemia ≥10% of the LV myocardium"""),
        ('pet', 'PET', """**High-risk features on PET:**  \n• Area of ischaemia ≥10% of the LV myocardium"""),
        ('stress_cmr', 'Str-CMR', """**High-risk features on Stress CMR:**  \n• ≥2 of 16 segments with stress perfusion defects or  \n• ≥3 dobutamine-induced dysfunctional segments""")
    ]
    
    for (test, label, help_text), col in zip(tests, columns[:3]):
        with col:
            _render_test_input(test, label, help_text)
            
    # Show info box if no FFR-validated tests are checked
    if not any(st.session_state.completed_tests[f'{test}_done'] 
              for test in FFR_VALIDATED_TESTS):
        st.info("Note: Only SPECT, PET, and Stress CMR have been validated "
                "against FFR as reference standard.")

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
    # Get valid tests based on reference standard
    valid_tests = (FFR_VALIDATED_TESTS if st.session_state.use_ffr 
                  else AVAILABLE_TESTS)
    
    # Filter completed tests with results
    test_results = {
        k: v for k, v in st.session_state.test_results.items() 
        if k in valid_tests and v
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