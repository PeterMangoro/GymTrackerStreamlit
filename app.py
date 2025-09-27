"""
Gym Progress Tracker - Main Application
"""

import streamlit as st
from config import PAGE_CONFIG
from components.ui_components import render_css


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
    
    **📈 Dashboard** - Overview of your workout statistics and recent activity
    
    **🏅 Performance & Strength Insights** - Advanced analytics including:
    - 1RM calculations and progression tracking
    - Personal records (PRs) 
    - Weekly/monthly training volume analysis
    - Muscle group balance monitoring
    - Training intensity zones
    - Recovery and fatigue tracking
    
    **📈 Progress Tracking** - Detailed charts showing your progress over time
    
    **🏋️ Exercise Analysis** - Deep dive into specific exercise performance
    
    **📝 Add Workout** - Log new workout sessions
    
    **📋 Workout History** - View and filter your complete workout history
    
    ### 🚀 Getting Started:
    
    1. **Add your first workout** using the "Add Workout" page
    2. **View your dashboard** to see your progress overview
    3. **Explore performance insights** to understand your training patterns
    4. **Track your progress** over time with detailed charts
    
    Use the navigation menu on the left to explore all features!
    """)
    
    # Add some visual elements
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Total Features", "6")
    
    with col2:
        st.metric("🏋️ Workout Days", "Tracked")
    
    with col3:
        st.metric("📈 Analytics", "Advanced")


if __name__ == "__main__":
    main()
