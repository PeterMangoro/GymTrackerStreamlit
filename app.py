"""
Gym Progress Tracker - Main Application
"""

import warnings
import streamlit as st
from config import PAGE_CONFIG
from components.ui_components import render_css

# Suppress warnings
warnings.filterwarnings('ignore')


def main():
    """Main application function"""
    # Page configuration
    st.set_page_config(**PAGE_CONFIG)
    
    # Render CSS
    render_css()
    
    # Welcome page content
    st.markdown('<h1 class="main-header">💪 Gym Progress Tracker</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    ## Welcome to Your Personal Gym Tracker! 🏋️‍♂️
    
    This application helps you track and analyze your workout progress with comprehensive insights and analytics.
    
    ### 📊 Available Features:
    
    **📈 [Dashboard](dashboard)** - Overview of your workout statistics and recent activity
    
    **🏅 [Performance & Strength Insights](performance_insights)** - Advanced analytics including:
    - 1RM calculations and progression tracking
    - Personal records (PRs) 
    - Weekly/monthly training volume analysis
    - Muscle group balance monitoring
    - Training intensity zones
    - Recovery and fatigue tracking
    
    **📈 [Progress Tracking](progress_tracking)** - Detailed charts showing your progress over time
    
    **🏋️ [Exercise Analysis](exercise_analysis)** - Deep dive into specific exercise performance
    
    **📝 [Add Workout](workout_management)** - Log new workout sessions
    
    **📋 [Workout History](workout_management)** - View and filter your complete workout history
    
    **🤖 [AI Workout Recommendations](ml_recommendations)** - Machine learning-powered workout suggestions
    
    ### 🚀 Getting Started:
    
    1. **Add your first workout** using the "Add Workout" page
    2. **View your dashboard** to see your progress overview
    3. **Explore performance insights** to understand your training patterns
    4. **Track your progress** over time with detailed charts
    5. **Get AI recommendations** for personalized workout plans
    
    Use the navigation menu on the left to explore all features!
    """)
    
    # Add some visual elements
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Total Features", "7")
    
    with col2:
        st.metric("🏋️ Workout Days", "Tracked")
    
    with col3:
        st.metric("🤖 AI Features", "ML-Powered")


if __name__ == "__main__":
    main()
