"""Probability adjustment components."""

import streamlit as st
from typing import Optional
from src.state.session_state import SessionState

def _on_slider_change():
    """Handle slider value changes."""
    if 'manual_adjustment_value' in st.session_state:
        st.session_state.manual_rf_cl_adjustment = st.session_state.manual_adjustment_value

def _on_reset_click():
    """Handle reset button click."""
    st.session_state.manual_rf_cl_adjustment = None
    if 'manual_adjustment_value' in st.session_state:
        del st.session_state.manual_adjustment_value

def render_probability_adjustment(base_rf_cl: float) -> None:
    """
    Render the probability adjustment section.
    
    Args:
        base_rf_cl: Base RF-CL probability
    """
    # Show the appropriate metric based on whether there's a manual adjustment
    if st.session_state.manual_rf_cl_adjustment is not None:
        st.metric(
            "**Adjusted** Risk Factor-weighted Clinical Likelihood (Adj. RF-CL)", 
            f"{st.session_state.manual_rf_cl_adjustment:.1f}%*",
            delta=f"{st.session_state.manual_rf_cl_adjustment - base_rf_cl:.1f}%"
        )
    else:
        st.metric(
            "Risk Factor-weighted Clinical Likelihood (RF-CL)", 
            f"{base_rf_cl:.1f}%"
        )

    with st.expander("📝 ESC Recommends:  \nAdjust RF-CL based on Clinical Findings") as exp:
        # Update expander state
        st.session_state.manual_adjustment_expander_open = exp
        
        # Create columns for slider and reset button
        col1, col2 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        
        with col1:
            # If there's no manual adjustment yet, use base_rf_cl as the starting value
            starting_value = (st.session_state.manual_rf_cl_adjustment 
                            if st.session_state.manual_rf_cl_adjustment is not None 
                            else base_rf_cl)
            
            st.slider(
                "**Adjusted** Probability (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(starting_value),
                step=0.1,
                format="%.1f",
                key="manual_adjustment_value",
                on_change=_on_slider_change
            )
        
        with col2:
            st.button(
                "Reset",
                use_container_width=True,
                on_click=_on_reset_click
            )

        st.info("""
            The ESC guidelines suggest that clinicians should manually adjust the pre-test 
            probability based on other clinical parameters not captured in the 
            standard model.
        """)
        
        _render_adjustment_guidelines()

def render_cacs_section(current_prob: float) -> Optional[int]:
    """
    Render the CACS input section.
    
    Args:
        current_prob: Current probability (could be RF-CL or Adjusted RF-CL)
    
    Returns:
        Optional[int]: CACS value if entered, None otherwise
    """
    cacs = None
    with st.expander("💫 Have results of calcium score?  \nEnter them here for a CACS-CL", expanded=False):
        cacs = st.number_input(
            "Coronary Artery Calcium Score (Agatston)", 
            min_value=0, 
            value=None,
            help="Enter the Agatston calcium score if available"
        )
        
        if cacs is not None:
            from src.utils.calculations import calculate_cacs_cl
            
            cacs_cl = calculate_cacs_cl(current_prob, cacs)
            
            col1, col2 = st.columns([0.55, 0.45], vertical_alignment="center")
            with col1:
                is_adjusted = st.session_state.manual_rf_cl_adjustment is not None
                asterisk = "*" if is_adjusted else ""
                metric_label = ("**Adjusted** CACS-weighted Clinical Likelihood (Adj. CACS-CL)" 
                            if is_adjusted 
                            else "CACS-weighted Clinical Likelihood (CACS-CL)")
                st.metric(
                    metric_label,
                    f"{cacs_cl:.1f}%{asterisk}",
                    delta=f"{cacs_cl - current_prob:.1f}%"
                )
            
            with col2:
                _render_cacs_interpretation(cacs)
    
    return cacs

def _render_adjustment_guidelines() -> None:
    """Render the guidelines for clinical probability adjustment."""
    with st.popover("📚 ESC Guidelines for Clinical Probability Adjustment", use_container_width=True):
        st.markdown("""
                ### 📊 Clinical Adjustment Considerations
                
                [🔗 Access Full ESC Guidelines Here](https://www.escardio.org/Guidelines/Clinical-Practice-Guidelines/Chronic-Coronary-Syndromes)
                ___

                ### ⚡ ECG Changes
                - 📍 **Resting ECG abnormalities** - Q-waves or ST-segment/T-wave changes
                - 📍 **Exercise ECG findings** - even if not diagnostic
                - 📍 **Conduction abnormalities** - LBBB/RBBB

                ### ❤️ Cardiac Function
                - 💔 **LV dysfunction** - severe or segmental
                - 💓 **Ventricular arrhythmia** - presence of significant rhythm disturbance
                - 😮‍💨 **Heart failure symptoms** - exertional dyspnea, reduced exercise tolerance

                ### 🫀 Vascular Disease  
                - 🔄 **Peripheral artery disease** - documented PAD or symptoms
                - 🔍 **Pre-existing calcification** - noted on prior chest imaging
                - 🔍 **Carotid disease** - known carotid stenosis
                - 🔍 **Aortic disease** - aortic atherosclerosis

                ### 🏥 Comorbidities
                - 🎯 **Chronic kidney disease** - especially if eGFR <60
                - 🔥 **Inflammatory conditions** - rheumatoid arthritis, lupus
                - ⚠️ **Metabolic disorders** - thyroid disease, obesity

                ### 📋 Risk Factor Assessment
                - 📌 **Multiple Risk Factors** - Beyond those captured in basic assessment
                - 📈 **Risk Factor Severity** - e.g., poorly controlled diabetes, severe hypertension
                - ⏳ **Duration of Exposure** - Long-term exposure to risk factors increases impact
                - 🎯 **Risk Factor Clustering** - Multiple risk factors in younger patients (<50 years)

                ### 👥 Specific Patient Groups
                - 👩 **Post-menopausal women** - especially with risk factors
                - 🎗️ **Cancer survivors** - especially after chest radiotherapy
                - 🫀 **Transplant recipients** - immunosuppression impact
                - 🦠 **HIV patients** - accelerated atherosclerosis

                ___
                💡 *These factors should be considered when adjusting the pre-test probability based on your clinical judgment* 👨‍⚕️
                """)

def _render_cacs_interpretation(cacs: int) -> None:
    """Render the interpretation of CACS score."""
    if cacs == 0:
        st.success("No calcification")
    elif cacs < 10:
        st.success("Minimal calcification")
    elif cacs < 100:
        st.warning("Mild calcification")
    elif cacs < 400:
        st.warning("Moderate calcification")
    elif cacs < 1000:
        st.error("Severe calcification")
    else:
        st.error("Extensive calcification")