"""
ML Workout Recommendations Page
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

from utils.data_processing import load_workout_data, get_file_mtime
from utils.ml_recommender import MLWorkoutRecommender
from utils.complete_workout_recommender import CompleteWorkoutRecommender


def show_ml_recommendations():
    """Display ML workout recommendations page"""
    # Custom CSS for dark theme
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5em;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .recommendation-section {
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
    }
    
    .performance-section {
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
    }
    
    .metric-card {
        background: rgba(255,255,255,0.08);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
    }
    
    .reasoning-text {
        background: rgba(102, 126, 234, 0.1);
        border-left: 4px solid #667eea;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
        font-style: italic;
        color: #B0B0B0;
    }
    
    .analysis-section {
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
    }
    
    .history-section {
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Dark theme for Streamlit components */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        color: #B0B0B0;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Workout Recommendations</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    csv_path = 'workouts.csv'
    file_mtime = get_file_mtime(csv_path)
    df = load_workout_data(csv_path, file_mtime)
    
    if df.empty:
        st.error("No workout data found. Please add some workouts first.")
        return
    
    # Initialize ML recommender
    if 'ml_recommender' not in st.session_state:
        st.session_state.ml_recommender = MLWorkoutRecommender()
    
    # Initialize Complete Workout Recommender
    if 'complete_workout_recommender' not in st.session_state:
        st.session_state.complete_workout_recommender = CompleteWorkoutRecommender()
    
    recommender = st.session_state.ml_recommender
    complete_recommender = st.session_state.complete_workout_recommender
    
    # Train models if not already trained
    if not recommender.is_trained:
        with st.spinner("Training ML models... This may take a moment."):
            success = recommender.train(df)
            if success:
                st.success("✅ ML models trained successfully!")
            else:
                st.error("❌ Failed to train ML models. Please check your data.")
                return
    
    # Sidebar controls with dark theme styling
    st.sidebar.markdown("""
    <div style="
        background: rgba(102, 126, 234, 0.1);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
    ">
        <h4 style="color: #667eea; margin: 0;">🎛️ Recommendation Settings</h4>
    </div>
    """, unsafe_allow_html=True)
    
    recommendation_type = st.sidebar.selectbox(
        "Recommendation Type",
        ["hybrid", "context_aware", "collaborative", "content", "sequence"],
        format_func=lambda x: {
            "hybrid": "🤖 Hybrid (Recommended)",
            "context_aware": "🧠 Context-Aware",
            "collaborative": "👥 Collaborative Filtering",
            "content": "📊 Content-Based",
            "sequence": "🔄 Sequence-Based"
        }[x]
    )
    
    n_recommendations = st.sidebar.slider("Number of Recommendations", 3, 10, 5)
    
    # Add info about current settings
    st.sidebar.markdown(f"""
    <div style="
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
        padding: 10px;
        margin: 10px 0;
        font-size: 0.8em;
        color: #B0B0B0;
    ">
        <strong>Current Settings:</strong><br>
        Type: {recommendation_type.replace('_', ' ').title()}<br>
        Count: {n_recommendations} recommendations
    </div>
    """, unsafe_allow_html=True)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="recommendation-section">', unsafe_allow_html=True)
        st.subheader("🎯 Your Personalized Recommendations")
        
        # Get recommendations
        recommendations = recommender.get_recommendations(
            df, recommendation_type, n_recommendations
        )
        
        if "error" in recommendations:
            st.error(f"Error: {recommendations['error']}")
        else:
            # Display recommendations with enhanced styling
            st.markdown(f"""
            <div style="
                background: rgba(102, 126, 234, 0.15);
                border-radius: 10px;
                padding: 15px;
                margin: 15px 0;
                border-left: 4px solid #667eea;
            ">
                <h4 style="color: #667eea; margin: 0 0 8px 0;">{recommendations['type']}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="reasoning-text">
                {recommendations['reasoning']}
            </div>
            """, unsafe_allow_html=True)
            
            # Create recommendation cards with dark theme styling
            for i, exercise in enumerate(recommendations['recommendations'], 1):
                with st.container():
                    # Different colors for different positions
                    colors = {
                        1: "#2E8B57",  # Sea Green for #1
                        2: "#4169E1",  # Royal Blue for #2
                        3: "#DC143C",  # Crimson for #3
                        4: "#FF8C00",  # Dark Orange for #4
                        5: "#9932CC"   # Dark Orchid for #5
                    }
                    
                    bg_color = colors.get(i, "#2C2C2C")  # Default dark gray
                    
                    st.markdown(f"""
                    <div style="
                        border: 2px solid {bg_color};
                        border-radius: 12px;
                        padding: 20px;
                        margin: 15px 0;
                        background: linear-gradient(135deg, {bg_color}20, {bg_color}10);
                        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                        transition: transform 0.2s ease;
                    ">
                        <div style="
                            display: flex;
                            align-items: center;
                            justify-content: space-between;
                        ">
                            <div>
                                <h3 style="
                                    color: {bg_color};
                                    margin: 0 0 8px 0;
                                    font-size: 1.2em;
                                    font-weight: bold;
                                ">#{i}</h3>
                                <h4 style="
                                    color: #FFFFFF;
                                    margin: 0;
                                    font-size: 1.4em;
                                    font-weight: 600;
                                ">{exercise}</h4>
                            </div>
                            <div style="
                                background-color: {bg_color};
                                border-radius: 50%;
                                width: 40px;
                                height: 40px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                color: white;
                                font-weight: bold;
                                font-size: 1.2em;
                            ">{i}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="performance-section">', unsafe_allow_html=True)
        st.subheader("📊 Model Performance")
        
        # Get model performance
        performance = recommender.get_model_performance(df)
        
        if "error" not in performance:
            # Create styled metric cards
            metrics = [
                ("Total Workouts", performance['total_workouts'], "#2E8B57"),
                ("Unique Exercises", performance['unique_exercises'], "#4169E1"),
                ("Muscle Groups", performance['muscle_groups'], "#DC143C"),
                ("Prediction Accuracy", f"{performance['prediction_accuracy']:.1%}", "#FF8C00")
            ]
            
            for metric_name, metric_value, color in metrics:
                st.markdown(f"""
                <div class="metric-card" style="border-left-color: {color};">
                    <div style="
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    ">
                        <span style="color: #B0B0B0; font-size: 0.9em;">{metric_name}</span>
                        <span style="color: {color}; font-size: 1.5em; font-weight: bold;">{metric_value}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="
                background: rgba(46, 139, 87, 0.15);
                border-radius: 10px;
                padding: 15px;
                margin: 15px 0;
                border-left: 4px solid #2E8B57;
                text-align: center;
            ">
                <span style="color: #2E8B57; font-weight: bold;">✅ {performance['model_status']}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error(f"Error: {performance['error']}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed Analysis Section
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
    st.subheader("🔍 Detailed Analysis")
    
    # Create tabs for different analyses
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏋️ Complete Workouts", "📈 Training Patterns", "🎯 Exercise Preferences", 
        "⚖️ Muscle Balance", "🔄 Workout Sequences"
    ])
    
    with tab1:
        show_complete_workout_recommendations(df, complete_recommender)
    
    with tab2:
        show_training_patterns(df)
    
    with tab3:
        show_exercise_preferences(df)
    
    with tab4:
        show_muscle_balance_analysis(df)
    
    with tab5:
        show_workout_sequences(df)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Recommendation History
    st.markdown('<div class="history-section">', unsafe_allow_html=True)
    st.subheader("📚 Recommendation History")
    
    if 'recommendation_history' not in st.session_state:
        st.session_state.recommendation_history = []
    
    # Add current recommendation to history
    if "error" not in recommendations:
        history_entry = {
            'timestamp': datetime.now(),
            'type': recommendation_type,
            'recommendations': recommendations['recommendations'],
            'reasoning': recommendations['reasoning']
        }
        st.session_state.recommendation_history.append(history_entry)
        
        # Keep only last 10 entries
        if len(st.session_state.recommendation_history) > 10:
            st.session_state.recommendation_history = st.session_state.recommendation_history[-10:]
    
    # Display history
    if st.session_state.recommendation_history:
        for i, entry in enumerate(reversed(st.session_state.recommendation_history)):
            with st.expander(f"Recommendation #{len(st.session_state.recommendation_history) - i} - {entry['type']} ({entry['timestamp'].strftime('%Y-%m-%d %H:%M')})"):
                st.write(f"**Type:** {entry['type']}")
                st.write(f"**Reasoning:** {entry['reasoning']}")
                st.write(f"**Recommendations:** {', '.join(entry['recommendations'])}")
    else:
        st.info("No recommendation history yet. Generate some recommendations to see your history!")
    
    st.markdown('</div>', unsafe_allow_html=True)


def show_complete_workout_recommendations(df, complete_recommender):
    """Show complete workout recommendations with sets, reps, and weights"""
    st.subheader("🏋️ Complete Workout Recommendations")
    
    # Workout type selection
    col1, col2 = st.columns(2)
    
    with col1:
        workout_type = st.selectbox(
            "Workout Type",
            ["balanced", "upper_body", "lower_body", "push", "pull", "cardio"],
            format_func=lambda x: {
                "balanced": "⚖️ Balanced Full Body",
                "upper_body": "💪 Upper Body Focus",
                "lower_body": "🦵 Lower Body Focus", 
                "push": "📤 Push Movements",
                "pull": "📥 Pull Movements",
                "cardio": "🏃 Cardio & Conditioning"
            }[x]
        )
    
    with col2:
        duration = st.slider("Workout Duration (minutes)", 30, 120, 60)
    
    # Generate workout button
    if st.button("🎯 Generate Complete Workout", type="primary"):
        with st.spinner("Generating your personalized workout..."):
            workout = complete_recommender.recommend_complete_workout(df, workout_type, duration)
            
            if workout:
                # Display workout summary
                st.markdown(f"""
                <div style="
                    background: rgba(46, 139, 87, 0.15);
                    border-radius: 15px;
                    padding: 20px;
                    margin: 20px 0;
                    border-left: 4px solid #2E8B57;
                ">
                    <h3 style="color: #2E8B57; margin: 0 0 10px 0;">📊 Workout Summary</h3>
                    <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                        <div><strong>Type:</strong> {workout['workout_type'].replace('_', ' ').title()}</div>
                        <div><strong>Duration:</strong> ~{workout['estimated_duration']} minutes</div>
                        <div><strong>Exercises:</strong> {workout['exercises']} exercises</div>
                        <div><strong>Total Volume:</strong> {workout['total_volume']:,.0f} lbs</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Display exercises
                st.subheader("🏋️ Your Workout Plan")
                
                for i, exercise in enumerate(workout['exercises'], 1):
                    # Color coding for different muscle groups
                    muscle_colors = {
                        'Chest': '#DC143C',
                        'Back': '#4169E1', 
                        'Legs': '#2E8B57',
                        'Shoulders': '#FF8C00',
                        'Arms': '#9932CC',
                        'Triceps': '#9932CC',
                        'Biceps': '#9932CC'
                    }
                    
                    color = muscle_colors.get(exercise['muscle_group'], '#667eea')
                    
                    # Create exercise card using columns for better layout
                    with st.container():
                        st.markdown(f"""
                        <div style="
                            border: 2px solid {color};
                            border-radius: 12px;
                            padding: 20px;
                            margin: 15px 0;
                            background: linear-gradient(135deg, {color}20, {color}10);
                            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                        ">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                <h3 style="color: {color}; margin: 0;">#{i} {exercise['exercise']}</h3>
                                <span style="
                                    background-color: {color};
                                    color: white;
                                    padding: 5px 10px;
                                    border-radius: 15px;
                                    font-size: 0.8em;
                                ">{exercise['muscle_group']}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Use Streamlit columns for the metrics
                        col1, col2, col3, col4, col5 = st.columns(5)
                        
                        with col1:
                            st.metric("Sets", exercise['sets'])
                        with col2:
                            st.metric("Reps", exercise['reps'])
                        with col3:
                            st.metric("Weight", f"{exercise['weight']} lbs")
                        with col4:
                            st.metric("Rest", f"{exercise['rest_time']}s")
                        with col5:
                            st.metric("RPE Target", f"{exercise['rpe_target']}")
                        
                        # Exercise notes
                        st.info(f"💡 {exercise['notes']}")
                        
                        st.markdown("---")  # Separator between exercises
                
                # Display workout tips
                st.subheader("💡 Workout Tips")
                
                for tip in workout['recommendations']:
                    st.markdown(f"""
                    <div style="
                        background: rgba(102, 126, 234, 0.1);
                        border-left: 4px solid #667eea;
                        padding: 10px 15px;
                        margin: 8px 0;
                        border-radius: 5px;
                        color: #B0B0B0;
                    ">
                        ✅ {tip}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Save workout option
                if st.button("💾 Save This Workout"):
                    if 'saved_workouts' not in st.session_state:
                        st.session_state.saved_workouts = []
                    
                    workout_entry = {
                        'timestamp': datetime.now(),
                        'workout': workout,
                        'type': workout_type,
                        'duration': duration
                    }
                    
                    st.session_state.saved_workouts.append(workout_entry)
                    st.success("✅ Workout saved! You can view it in the Workout History section.")
            else:
                st.error("❌ Failed to generate workout. Please check your data.")
    
    # Show saved workouts
    if 'saved_workouts' in st.session_state and st.session_state.saved_workouts:
        st.subheader("💾 Saved Workouts")
        
        for i, saved_workout in enumerate(reversed(st.session_state.saved_workouts[-5:]), 1):
            with st.expander(f"Workout #{len(st.session_state.saved_workouts) - i + 1} - {saved_workout['type'].replace('_', ' ').title()} ({saved_workout['timestamp'].strftime('%Y-%m-%d %H:%M')})"):
                workout = saved_workout['workout']
                
                st.write(f"**Type:** {workout['workout_type'].replace('_', ' ').title()}")
                st.write(f"**Duration:** ~{workout['estimated_duration']} minutes")
                st.write(f"**Exercises:** {workout['exercises']} exercises")
                st.write(f"**Total Volume:** {workout['total_volume']:,.0f} lbs")
                
                st.write("**Exercises:**")
                for j, exercise in enumerate(workout['exercises'], 1):
                    st.write(f"{j}. {exercise['exercise']} - {exercise['sets']}x{exercise['reps']} @ {exercise['weight']} lbs")


def show_training_patterns(df):
    """Show training pattern analysis"""
    # Weekly volume trend
    df['Week'] = df['Date'].dt.to_period('W')
    weekly_volume = df.groupby('Week')['Total_Volume'].sum()
    
    fig = px.line(
        x=weekly_volume.index.astype(str), 
        y=weekly_volume.values,
        title="Weekly Training Volume Trend",
        labels={'x': 'Week', 'y': 'Total Volume (lbs)'}
    )
    st.plotly_chart(fig, config={'displayModeBar': False})
    
    # RPE distribution
    fig_rpe = px.histogram(
        df, x='RPE', 
        title="RPE Distribution",
        nbins=10
    )
    st.plotly_chart(fig_rpe, config={'displayModeBar': False})


def show_exercise_preferences(df):
    """Show exercise preference analysis"""
    # Most frequent exercises
    exercise_counts = df['Exercise'].value_counts().head(10)
    
    fig = px.bar(
        x=exercise_counts.values,
        y=exercise_counts.index,
        orientation='h',
        title="Top 10 Most Frequent Exercises"
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, config={'displayModeBar': False})
    
    # Exercise variety over time
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.to_period('M')
    monthly_variety = df.groupby('Month')['Exercise'].nunique()
    
    fig_variety = px.line(
        x=monthly_variety.index.astype(str),
        y=monthly_variety.values,
        title="Exercise Variety Over Time",
        labels={'x': 'Month', 'y': 'Number of Unique Exercises'}
    )
    st.plotly_chart(fig_variety, config={'displayModeBar': False})


def show_muscle_balance_analysis(df):
    """Show muscle balance analysis"""
    # Muscle group volume distribution - using bar chart instead of pie
    muscle_volume = df.groupby('Muscle Group')['Total_Volume'].sum()
    
    fig_volume = px.bar(
        x=muscle_volume.index,
        y=muscle_volume.values,
        title="Training Volume by Muscle Group",
        labels={'x': 'Muscle Group', 'y': 'Total Volume (lbs)'}
    )
    fig_volume.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_volume, config={'displayModeBar': False})
    
    # Muscle group frequency
    muscle_frequency = df['Muscle Group'].value_counts()
    
    fig_freq = px.bar(
        x=muscle_frequency.index,
        y=muscle_frequency.values,
        title="Workout Frequency by Muscle Group",
        labels={'x': 'Muscle Group', 'y': 'Number of Workouts'}
    )
    fig_freq.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_freq, config={'displayModeBar': False})


def show_workout_sequences(df):
    """Show workout sequence analysis"""
    # Daily workout patterns
    df['DayOfWeek'] = df['Date'].dt.day_name()
    daily_patterns = df.groupby('DayOfWeek').size()
    
    # Reorder days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_patterns = daily_patterns.reindex(day_order, fill_value=0)
    
    fig = px.bar(
        x=daily_patterns.index,
        y=daily_patterns.values,
        title="Workout Frequency by Day of Week"
    )
    st.plotly_chart(fig, config={'displayModeBar': False})
    
    # Rest day patterns
    df_sorted = df.sort_values('Date')
    dates = pd.date_range(start=df_sorted['Date'].min(), end=df_sorted['Date'].max(), freq='D')
    workout_dates = set(df_sorted['Date'].dt.date)
    
    rest_days = []
    workout_days = []
    
    for date in dates:
        if date.date() in workout_dates:
            workout_days.append(date)
        else:
            rest_days.append(date)
    
    st.write(f"**Workout Days:** {len(workout_days)}")
    st.write(f"**Rest Days:** {len(rest_days)}")
    st.write(f"**Workout Frequency:** {len(workout_days) / len(dates):.1%}")


# Add this page to the pages directory
if __name__ == "__main__":
    show_ml_recommendations()
