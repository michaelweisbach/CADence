"""Recommendations component for CADence."""

import streamlit as st
from typing import Dict, List, TypedDict, Optional

class Recommendation(TypedDict):
    """Type definition for recommendation dictionary."""
    test: str
    reason: str
    performance: str
    recommendation_quote: str
    class_: str
    level: str

def get_recommendations(
    adjusted_ptp: float,
    completed_tests: Optional[Dict[str, bool]] = None
) -> List[Recommendation]:
    """
    Get test recommendations based on adjusted PTP and completed tests.
    
    Args:
        adjusted_ptp: Adjusted pre-test probability
        completed_tests: Dictionary of completed test flags
        
    Returns:
        List of recommendation dictionaries
    """
    if completed_tests is None:
        completed_tests = {}
        
    recommendations = []

    # Check if tests are completed
    has_ccta = completed_tests.get('ccta_done', False)
    has_functional = any(completed_tests.get(f'{test}_done', False) 
                        for test in ['stress_ecg', 'stress_echo', 'spect', 
                                   'pet', 'stress_cmr'])
    
    if adjusted_ptp <= 5:
        recommendations.append({
            'test': 'Defer Testing',
            'reason': 'Very low pre-test probability.',
            'performance': 'Risk of false positives exceeds benefit',
            'recommendation_quote': ('In individuals with a very low (≤5%) pre-test '
                                  'likelihood of obstructive CAD, deferral of further '
                                  'diagnostic tests should be considered.'),
            'class_': 'IIa',
            'level': 'B'
        })
        
    elif adjusted_ptp > 85:
        recommendations.append({
            'test': 'Invasive Coronary Angiography',
            'reason': 'High pre-test probability warrants direct invasive assessment.',
            'performance': 'Direct referral for invasive testing with FFR capability',
            'recommendation_quote': ('In individuals at high risk of adverse events '
                                  '(regardless of symptoms), ICA—complemented by '
                                  'invasive coronary pressure (FFR/iFR) when '
                                  'appropriate—is recommended.'),
            'class_': 'I',
            'level': 'A'
        })
        
    elif has_ccta and has_functional and 5 < adjusted_ptp < 85:
        recommendations.append({
            'test': 'Consider ICA',
            'reason': 'Diagnostic uncertainty after non-invasive testing',
            'performance': 'Consider ICA with FFR capability',
            'recommendation_quote': ('Invasive coronary angiography with the '
                                  'availability of invasive functional assessments '
                                  'is recommended to confirm or exclude the diagnosis '
                                  'of obstructive CAD or ANOCA/INOCA in individuals '
                                  'with an uncertain diagnosis on non-invasive testing.'),
            'class_': 'I',
            'level': 'B'
        })
        
    elif has_functional and not has_ccta and adjusted_ptp < 85:
        recommendations.append({
            'test': 'CCTA',
            'reason': 'Anatomical assessment needed after functional testing',
            'performance': 'CCTA recommended after functional testing',
            'recommendation_quote': ('CCTA is recommended in individuals with low or '
                                  'moderate (>5%–50%) pre-test likelihood if functional '
                                  'imaging for myocardial ischaemia is not diagnostic.'),
            'class_': 'I',
            'level': 'B'
        })
        
    elif has_ccta and not has_functional:
        recommendations.append({
            'test': 'Non-invasive Functional Imaging',
            'reason': 'Functional assessment needed after anatomical imaging',
            'performance': 'Recommended after CCTA if functional significance unclear',
            'recommendation_quote': ('Functional imaging for myocardial ischaemia is '
                                  'recommended if CCTA has shown CAD of uncertain '
                                  'functional significance or is not diagnostic.'),
            'class_': 'I',
            'level': 'B'
        })
        
    elif not has_ccta and not has_functional:
        if 50 < adjusted_ptp <= 85:
            recommendations.append({
                'test': 'Non-invasive Functional Imaging',
                'reason': 'Preferred in higher intermediate range',
                'performance': ('Functional imaging preferred for higher intermediate '
                              'range (50-85%)'),
                'recommendation_quote': ('In individuals with suspected CCS and moderate '
                                      'or high (>15%–85%) pre-test likelihood of '
                                      'obstructive CAD, stress imaging is recommended '
                                      'to diagnose myocardial ischaemia and estimate '
                                      'the risk of MACE.'),
                'class_': 'I',
                'level': 'B'
            })
            
        elif 15 < adjusted_ptp <= 50:
            recommendations.append({
                'test': 'CCTA',
                'reason': 'Preferred in lower intermediate range',
                'performance': ('CCTA preferred for lower intermediate range '
                              '(15-50%)'),
                'recommendation_quote': ('To rule out obstructive CAD in individuals '
                                      'with low or moderate (>5%–50%) pre-test '
                                      'likelihood, CCTA is recommended as the '
                                      'preferred diagnostic modality.'),
                'class_': 'I',
                'level': 'B'
            })
            
        elif 5 < adjusted_ptp <= 15:
            # Only recommend clinical assessment if RF-CL hasn't been manually adjusted
            if st.session_state.manual_rf_cl_adjustment is None:
                recommendations.append({
                    'test': 'Clinical Assessment',
                    'reason': 'Additional clinical data needed',
                    'performance': 'Adjust RF-CL based on clinical findings',
                    'recommendation_quote': ('It is recommended to use additional '
                                          'clinical data (e.g. examination of peripheral '
                                          'arteries, resting ECG, resting '
                                          'echocardiography, presence of vascular '
                                          'calcifications on previously performed '
                                          'imaging tests) to adjust the estimate '
                                          'yielded by the Risk Factor-weighted '
                                          'Clinical Likelihood model.'),
                    'class_': 'I',
                    'level': 'C'
                })
                
            recommendations.append({
                'test': 'CCTA',
                'reason': 'Optimal for ruling out CAD at low pre-test probability',
                'performance': 'CCTA recommended as preferred diagnostic modality',
                'recommendation_quote': ('To rule out obstructive CAD in individuals '
                                      'with low or moderate (>5%–50%) pre-test '
                                      'likelihood, CCTA is recommended as the '
                                      'preferred diagnostic modality.'),
                'class_': 'I',
                'level': 'B'
            })
    
    return recommendations

def render_recommendations(
    recommendations: List[Recommendation],
    current_probability: float
) -> None:
    """
    Render recommendations based on ESC guidelines.
    
    Args:
        recommendations: List of recommendation dictionaries
        current_probability: Current probability value
    """
    # For combined CCTA and Functional Imaging recommendation
    if (len(recommendations) == 2 and
        'CCTA' in [rec['test'] for rec in recommendations] and
        'Non-invasive Functional Imaging' in [rec['test'] for rec in recommendations]):
        
        st.error("### CCTA or Non-invasive Functional Imaging")
        st.info("""
        **ESC Guideline Recommendation (Class I, Level B):**
        
        *"In symptomatic patients in whom the pre-test likelihood of obstructive CAD 
        by clinical assessment is >5%, CCTA or non-invasive functional imaging for 
        myocardial ischaemia is recommended as the initial diagnostic test."*
        
        The guidelines specifically recommend:
        - CCTA preferred for lower intermediate range (15-50%)
        - Functional imaging preferred for higher intermediate range (50-85%)
        - Selection should be based on:
          - Local expertise and availability
          - Patient characteristics (e.g., radiation exposure, ability to exercise)
          - Likelihood of getting diagnostic image quality
        """)
        
    else:
        # Single recommendation display
        for rec in recommendations:
            _render_single_recommendation(rec)

def _render_single_recommendation(rec: Recommendation) -> None:
    """Render a single recommendation with appropriate formatting."""
    
    # Define recommendation templates
    templates = {
        'Defer Testing': {
            'title': "### Defer Testing",
            'content': """
            **ESC Guideline Recommendation (Class IIa, Level B):**
            
            *"{recommendation_quote}"*
            
            Clinical considerations:
            - Risk of false positive results exceeds benefit at this probability
            - Focus on:
              - Risk factor modification
              - Alternative diagnoses
              - Reassessment if symptoms change or worsen
            """
        },
        'CCTA': {
            'title': "### CCTA Recommended",
            'content': """
            **ESC Guideline Recommendation (Class I, Level B):**
            
            *"{recommendation_quote}"*
            
            Key benefits of CCTA:
            - Excellent for ruling out obstructive CAD (high negative predictive value)
            - Can detect non-obstructive coronary disease
            - Provides detailed coronary anatomy assessment
            - Allows calcium scoring from the same scan
            - Guides decision about need for subsequent functional testing
            """
        },
        'Clinical Assessment': {
            'title': "### Clinical Assessment and RF-CL Adjustment",
            'content': """
            **ESC Guideline Recommendation (Class I, Level C):**
            
            *"{recommendation_quote}"*
            
            **Use the 'Adjust RF-CL' option above to incorporate these findings.**
            """
        },
        'Non-invasive Functional Imaging': {
            'title': "### Non-invasive Functional Imaging",
            'content': """
            **ESC Guideline Recommendation (Class I, Level B):**
            
            *"{recommendation_quote}"*
            
            Benefits of functional imaging:
            - Directly demonstrates ischemia
            - Provides risk stratification
            - Guides revascularization decisions
            - Multiple modalities available:
              - Stress Echo
              - SPECT/PET
              - Stress CMR
            """
        },
        'Consider ICA': {
            'title': "### Diagnostic Uncertainty: Consider ICA",
            'content': """
            **ESC Guideline Recommendation (Class I, Level B):**
            
            *"{recommendation_quote}"*
            
            Important considerations:
            - Provides definitive anatomical assessment
            - Allows immediate pressure-wire assessment (FFR/iFR)
            - Can diagnose microvascular/vasospastic disease
            - Enables immediate intervention if needed
            - Consider when non-invasive tests are inconclusive or conflicting
            """
        },
        'Invasive Coronary Angiography': {
            'title': "### Invasive Coronary Angiography",
            'content': """
            **ESC Guideline Recommendation (Class I, Level A):**
            
            *"{recommendation_quote}"*
            
            High risk features include:
            - Left main disease with ≥50% stenosis
            - Three-vessel disease with ≥70% stenosis
            - Two-vessel disease with ≥70% stenosis including proximal LAD
            - One-vessel proximal LAD disease with ≥70% stenosis and FFR-CT ≤0.8
            
            Additional benefits:
            - Allows immediate intervention if needed
            - Provides definitive anatomical assessment
            - Enables pressure-wire assessment of lesions
            - Can assess for ANOCA/INOCA
            """
        }
    }
    
    template = templates.get(rec['test'])
    if template:
        st.error(template['title'])
        st.info(template['content'].format(recommendation_quote=rec['recommendation_quote']))