"""Recommendations component for CADence."""

import streamlit as st
from typing import Dict, List, TypedDict, Optional

class Recommendation(TypedDict):
    """Type definition for recommendation dictionary."""
    test: str
    reason: str
    performance: str
    recommendation_quote: str
    class_: Optional[str]
    level: Optional[str]

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
    
    # First check for high-risk features on any completed test

    # Check CCTA for high-risk features
    if has_ccta and st.session_state.test_results.get('ccta') == 'Positive':
        recommendations.append({
            'test': 'Invasive Coronary Angiography',
            'reason': ('High event risk on CCTA - ≥50% left main stenosis, or ≥70% proximal LAD stenosis '
                     'with single or two-vessel CAD, or ≥70% proximal three-vessel CAD'),
            'performance': 'ICA with coronary pressure assessment',
            'recommendation_quote': ('*"In individuals at high risk of adverse events (regardless '
                                  'of symptoms), ICA—complemented by invasive coronary pressure '
                                  '(FFR/iFR) when appropriate—is recommended, with the aim of '
                                  'refining risk stratification and improving symptoms and '
                                  'cardiovascular outcomes by revascularization."*\n\n'
                                  '> Invasive coronary angiography/coronary pressure assessment is '
                                  'indicated if non-invasive assessment suggests high event risk—e.g. '
                                  'CCTA shows ≥50% left main stenosis, or ≥70% proximal LAD stenosis '
                                  'with single or two-vessel CAD, or ≥70% proximal three-vessel '
                                  'CAD—or when any stress test shows moderate to severe '
                                  'inducible ischaemia or when symptoms are highly suggestive of '
                                  'obstructive CAD.'),
            'class_': 'I',
            'level': 'A'
        })
        return recommendations

    # Check functional tests for high-risk features
    if has_functional:
        for test in ['stress_ecg', 'stress_echo', 'spect', 'pet', 'stress_cmr']:
            if completed_tests.get(f'{test}_done') and st.session_state.test_results.get(test) == 'Positive':
                recommendations.append({
                    'test': 'Invasive Coronary Angiography',
                    'reason': 'High event risk on functional testing - moderate to severe inducible ischaemia',
                    'performance': 'ICA with coronary pressure assessment',
                    'recommendation_quote': ('*"In individuals at high risk of adverse events (regardless '
                                          'of symptoms), ICA—complemented by invasive coronary pressure '
                                          '(FFR/iFR) when appropriate—is recommended, with the aim of '
                                          'refining risk stratification and improving symptoms and '
                                          'cardiovascular outcomes by revascularization."*\n\n'
                                          '> Invasive coronary angiography/coronary pressure assessment is '
                                          'indicated if non-invasive assessment suggests high event risk—e.g. '
                                          'CCTA shows ≥50% left main stenosis, or ≥70% proximal LAD stenosis '
                                          'with single or two-vessel CAD, or ≥70% proximal three-vessel '
                                          'CAD—or when any stress test shows moderate to severe '
                                          'inducible ischaemia or when symptoms are highly suggestive of '
                                          'obstructive CAD.'),
                    'class_': 'I',
                    'level': 'A'
                })
                return recommendations

    # If no high-risk features, proceed with standard recommendations

    # Very high pre-test probability
    if adjusted_ptp > 85:
        recommendations.append({
            'test': 'Invasive Coronary Angiography',
            'reason': 'Very high pre-test probability',
            'performance': 'Direct referral for invasive testing with FFR capability',
            'recommendation_quote': ('*"In individuals at high risk of adverse events '
                                  '(regardless of symptoms), ICA—complemented by '
                                  'invasive coronary pressure (FFR/iFR) when '
                                  'appropriate—is recommended."*'),
            'class_': 'I',
            'level': 'A'
        })

    # Both CCTA and functional testing completed
    elif has_ccta and has_functional:
        if (st.session_state.test_results.get('ccta') == 'Positive' or 
            any(st.session_state.test_results.get(test) == 'Positive' 
                for test in ['stress_ecg', 'stress_echo', 'spect', 'pet', 'stress_cmr'])):
            recommendations.append({
                'test': 'Invasive Coronary Angiography',
                'reason': 'Uncertain diagnosis after non-invasive testing',
                'performance': 'ICA with FFR capability',
                'recommendation_quote': ('*"Invasive coronary angiography with the '
                                      'availability of invasive functional assessments '
                                      'is recommended to confirm or exclude the diagnosis '
                                      'of obstructive CAD or ANOCA/INOCA in individuals '
                                      'with an uncertain diagnosis on non-invasive testing."*'),
                'class_': 'I',
                'level': 'B'
            })
        else:
            # Both tests negative
            recommendations.append({
                'test': 'Consider ANOCA/INOCA',
                'reason': 'Obstructive CAD excluded but symptoms persist',
                'performance': 'Consider invasive coronary functional testing to assess for microvascular or vasospastic disease if appropriate',
                'recommendation_quote': ('*"In persistently symptomatic patients despite medical '
                                      'treatment with suspected ANOCA/INOCA (i.e. anginal symptoms '
                                      'with normal coronary arteries or non-obstructive lesions at '
                                      'non-invasive imaging) and poor quality of life, invasive '
                                      'coronary functional testing is recommended to identify '
                                      'potentially treatable endotypes and to improve symptoms and '
                                      'quality of life, considering patient choices and preferences."*'),
                'class_': 'I',
                'level': 'B'
            })

    # CCTA done but uncertain functional significance
    elif has_ccta and not has_functional and st.session_state.test_results.get('ccta') != 'Positive':
        recommendations.append({
            'test': 'Non-invasive Functional Imaging',
            'reason': 'CAD of uncertain functional significance on CCTA',
            'performance': 'Functional testing recommended',
            'recommendation_quote': ('*"Functional imaging for myocardial ischaemia is '
                                  'recommended if CCTA has shown CAD of uncertain '
                                  'functional significance or is not diagnostic."*'),
            'class_': 'I',
            'level': 'B'
        })

    # Functional test done and no CCTA
    elif has_functional and not has_ccta:
        if any(st.session_state.test_results.get(test) == 'Non-diagnostic' 
               for test in ['stress_ecg', 'stress_echo', 'spect', 'pet', 'stress_cmr'] 
               if completed_tests.get(f'{test}_done')):
            recommendations.append({
                'test': 'CCTA',
                'reason': 'Non-diagnostic functional test',
                'performance': 'CCTA recommended when functional test is non-diagnostic',
                'recommendation_quote': ('*"CCTA is recommended in individuals with low or '
                                      'moderate (>5%–50%) pre-test likelihood if functional '
                                      'imaging for myocardial ischaemia is not diagnostic."*'),
                'class_': 'I',
                'level': 'B'
            })
        else:
            # Check PTP range for negative functional test
            if 5 < adjusted_ptp <= 50:
                recommendations.append({
                    'test': 'CCTA',
                    'reason': 'Rule out obstructive CAD in appropriate PTP range',
                    'performance': 'CCTA recommended to confirm absence of obstructive CAD',
                    'recommendation_quote': ('*"To rule out obstructive CAD in individuals with low or '
                                          'moderate (>5%–50%) pre-test likelihood, CCTA is recommended '
                                          'as the preferred diagnostic modality."*'),
                    'class_': 'I',
                    'level': 'B'
                })
            elif adjusted_ptp <= 5:
                recommendations.append({
                    'test': 'Consider ANOCA/INOCA',
                    'reason': 'Negative functional tests with very low PTP suggests non-obstructive cause',
                    'performance': 'Consider invasive coronary functional testing to assess for microvascular or vasospastic disease',
                    'recommendation_quote': ('*"In persistently symptomatic patients despite medical '
                                          'treatment with suspected ANOCA/INOCA (i.e. anginal symptoms '
                                          'with normal coronary arteries or non-obstructive lesions at '
                                          'non-invasive imaging) and poor quality of life, invasive '
                                          'coronary functional testing is recommended to identify '
                                          'potentially treatable endotypes and to improve symptoms and '
                                          'quality of life, considering patient choices and preferences."*'),
                    'class_': 'I',
                    'level': 'B'
                })

    # No prior testing - recommendations based on PTP
    elif not has_ccta and not has_functional:
        if adjusted_ptp <= 5:
            recommendations.append({
                'test': 'Consider Defer Testing',
                'reason': 'Very low pre-test probability',
                'performance': 'Risk of false positives exceeds benefit',
                'recommendation_quote': ('*"In individuals with a very low (≤5%) pre-test '
                                      'likelihood of obstructive CAD, deferral of further '
                                      'diagnostic tests should be considered."*'),
                'class_': 'IIa',
                'level': 'B'
            })
        
        elif 5 < adjusted_ptp <= 50:
            recommendations.append({
                'test': 'CCTA or Functional Imaging',
                'reason': 'Low or moderate pre-test probability',
                'performance': 'Either modality appropriate',
                'recommendation_quote': ('*"In symptomatic patients in whom the pre-test '
                                      'likelihood of obstructive CAD is >5%, CCTA or '
                                      'non-invasive functional imaging for myocardial '
                                      'ischaemia is recommended as the initial diagnostic test."*'),
                'class_': 'I',
                'level': 'B'
            })
            
        elif 50 < adjusted_ptp <= 85:
            recommendations.append({
                'test': 'Functional Imaging',
                'reason': 'High pre-test probability',
                'performance': 'Functional imaging preferred',
                'recommendation_quote': ('*"In individuals with suspected CCS and moderate '
                                      'or high (>15%–85%) pre-test likelihood of '
                                      'obstructive CAD, stress imaging is recommended '
                                      'to diagnose myocardial ischaemia and estimate '
                                      'the risk of MACE."*'),
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
    for rec in recommendations:
        _render_single_recommendation(rec)

def _render_single_recommendation(rec: Recommendation) -> None:
    """Render a single recommendation with appropriate formatting."""
    st.error(f"### {rec['test']}")
    
    content = ""
    if rec['class_'] is not None and rec['level'] is not None:
        content += f"**ESC Guideline Recommendation (Class {rec['class_']}, Level {rec['level']}):**\n\n"
    
    content += f"{rec['recommendation_quote']}\n\n"
    content += f"**Reason:** {rec['reason']}\n\n"
    content += f"**Performance:** {rec['performance']}"
    
    st.info(content)