"""
CADence: ESC 2024 CCS Guideline-Based Probability Calculator for Coronary Artery Disease
Main application entry point.
"""

import streamlit as st
from typing import Dict, Any

# Import components
from src.components.patient_characteristics import render_patient_characteristics
from src.components.risk_factors import render_risk_factors
from src.components.probability_adjustment import (
    render_probability_adjustment,
    render_cacs_section
)
from src.components.test_results import render_test_results
from src.components.recommendations import (
    get_recommendations,
    render_recommendations
)

# Import utilities and state management
from src.utils.calculations import (
    calculate_rf_cl,
    calculate_cacs_cl,
    adjust_likelihood_for_test_results
)
from src.state.session_state import SessionState

def setup_page():
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title="CAD Probability Calculator",
        page_icon="🫀"#,
        #layout="wide"
    )
    
    st.title("CADence 🫀")
    st.markdown("""
    <p style='font-size: 20px; margin-top: -20px; font-style: italic; color: #666666;'>
    ESC 2024 CCS Guideline-Based Probability Calculator for Coronary Artery Disease
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <p style='font-size: 16px; color: #888888;'>
    Your companion for evidence-based CAD assessment, integrating ESC guidelines, 
    risk factor analysis, and diagnostic recommendations into one seamless workflow.
    </p>
    """, unsafe_allow_html=True)

def render_footer():
    """Render the application footer with references and attribution."""
    st.markdown("---")
    st.markdown("""
    ### References
    1. Winther et al. JACC 2020 - Incorporating Coronary Calcification Into Pre-Test Assessment
    2. Knuuti et al. European Heart Journal 2018 - Meta-analysis of diagnostic tests
    3. 2024 ESC Guidelines for Management of Chronic Coronary Syndromes
    
    *This tool is for clinical decision support only.  
    Clinical judgment should always be used in conjunction with these results.*
    """)
    
    st.markdown("""
    <div style='margin-top: 20px; padding: 15px; border-left: 3px solid #0066cc; background-color: #f8f9fa;'>
        <p style='font-size: 14px; color: #444444; margin: 0;'>
            Developed by <a href='https://x.com/cardioshades' target='_blank' 
            style='text-decoration: none; color: inherit;'>
            <strong>Dr. U Bhalraam</strong></a> MBChB, BMSc, MRCP
        </p>
    </div>
    """, unsafe_allow_html=True)

def _on_score_change():
    """Handle changes to the probability score selection."""
    if 'probability_score_selector' not in st.session_state or not st.session_state.probability_score_selector:
        st.session_state.selected_probability_score = st.session_state.default_score
    else:
        st.session_state.selected_probability_score = st.session_state.probability_score_selector

def main():
    """Main application entry point."""
    # Set up the page
    setup_page()
    
    # Initialize session state
    SessionState.initialize_state()
    
    try:
        # Render patient characteristics section
        age, sex_binary, symptoms = render_patient_characteristics()
        
        # Store current values in session state
        st.session_state.current_age = age
        st.session_state.current_sex_binary = sex_binary
        st.session_state.current_symptoms = symptoms
        
        # Render risk factors section
        risk_factors = render_risk_factors()
        st.session_state.selected_risk_factors = risk_factors
        
        # Calculate base RF-CL
        if all(x is not None for x in [age, sex_binary, symptoms]):
            base_rf_cl = calculate_rf_cl(age, sex_binary, symptoms, risk_factors)
            st.session_state.current_rf_cl = base_rf_cl
            
            st.markdown("---")
            st.subheader("Risk Assessment")
            
            # Render probability adjustment section
            render_probability_adjustment(base_rf_cl)
            
            # Get current probability after manual adjustment (if any)
            current_prob = base_rf_cl
            if st.session_state.manual_rf_cl_adjustment is not None:
                current_prob = st.session_state.manual_rf_cl_adjustment
            
            # Render CACS section
            cacs = render_cacs_section(current_prob)
            
            # Update current probability if CACS is present
            if cacs is not None:
                current_prob = calculate_cacs_cl(current_prob, cacs)
                st.session_state.cacs_cl = current_prob
            
            # Render test results section
            test_results = render_test_results()
            
            # Get final probability including test results
            final_prob = current_prob
            if test_results:
                final_prob = adjust_likelihood_for_test_results(
                    current_prob,
                    test_results,
                    'functional' if st.session_state.use_ffr else 'anatomical'
                )
            
            st.session_state.final_probability = final_prob
            
            # Create options for segmented control in fixed order
            available_scores = ["RF-CL"]  # Always start with RF-CL

            # Add other scores in fixed order if they are available
            if st.session_state.manual_rf_cl_adjustment is not None:
                available_scores.append("**Adjusted** RF-CL")
                
            if cacs is not None:
                # If there's a manual adjustment, show as Adjusted CACS-CL
                if st.session_state.manual_rf_cl_adjustment is not None:
                    available_scores.append("**Adjusted** CACS-CL")
                else:
                    available_scores.append("CACS-CL")
                
            # Add post-test probability with appropriate label
            if test_results:
                if cacs is not None:
                    if st.session_state.manual_rf_cl_adjustment is not None:
                        available_scores.append("Post-Test **Adjusted** CACS-CL")
                    else:
                        available_scores.append("Post-Test CACS-CL")
                else:
                    if st.session_state.manual_rf_cl_adjustment is not None:
                        available_scores.append("Post-Test **Adjusted** RF-CL")
                    else:
                        available_scores.append("Post-Test RF-CL")

            st.markdown("---")
            st.subheader("Recommendations")

            # Store default score in session state
            st.session_state.default_score = available_scores[-1]
            
            # Initialize selected score if not exists
            if 'selected_probability_score' not in st.session_state:
                st.session_state.selected_probability_score = st.session_state.default_score
            
            # Show segmented control
            # Show segmented control
            selected_score = st.segmented_control(
                "Select which score you would like to base recommendations off of:",
                available_scores,
                selection_mode="single",
                default=st.session_state.default_score,
                key='probability_score_selector',
                on_change=_on_score_change
            )
            
            # Use selected score or default if None
            if selected_score is None:
                selected_score = st.session_state.default_score
            
            # Store the current selection
            st.session_state.selected_probability_score = selected_score
                
            # Determine which probability to use for recommendations
            recommendation_prob = base_rf_cl  # Default to base RF-CL
            if selected_score in ["CACS-CL", "**Adjusted** CACS-CL"] and cacs is not None:
                recommendation_prob = calculate_cacs_cl(current_prob, cacs)
            elif selected_score == "**Adjusted** RF-CL" and st.session_state.manual_rf_cl_adjustment is not None:
                recommendation_prob = st.session_state.manual_rf_cl_adjustment
            elif selected_score in ["Post-Test RF-CL", "Post-Test **Adjusted** RF-CL", 
                                  "Post-Test CACS-CL", "Post-Test **Adjusted** CACS-CL"]:
                recommendation_prob = final_prob
            
            # Ensure we have a valid probability
            if recommendation_prob is None:
                recommendation_prob = base_rf_cl
                
            # Display selected probability and get recommendations
            asterisk = "*" if "**Adjusted**" in selected_score else ""
            st.markdown(f"Recommendation based on {selected_score} :blue-background[[{recommendation_prob:.1f}%{asterisk}]]")
            recommendations = get_recommendations(
                recommendation_prob,
                st.session_state.completed_tests
            )
            render_recommendations(recommendations, recommendation_prob)
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
    
    # Render footer
    render_footer()

if __name__ == "__main__":
    main()