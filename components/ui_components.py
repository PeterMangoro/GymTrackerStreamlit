"""
Shared UI components for the Gym Progress Tracker app.
"""

import warnings
import streamlit as st

# Suppress warnings globally
warnings.filterwarnings('ignore')


def render_css():
    """Render custom CSS for dark theme compatibility"""
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #1f77b4;
        }
        .dark-theme .metric-card {
            background-color: #262730;
            color: white;
        }
        .exercise-card {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
            border: 1px solid #e9ecef;
        }
        .dark-theme .exercise-card {
            background-color: #2d3748;
            color: white;
            border-color: #4a5568;
        }
    </style>
    """, unsafe_allow_html=True)
