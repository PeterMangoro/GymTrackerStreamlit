"""
Exercise Analysis page for the Gym Progress Tracker app.
"""

import streamlit as st
import plotly.graph_objects as go


"""
Exercise Analysis page for the Gym Progress Tracker app.
"""

import streamlit as st
import plotly.graph_objects as go
from utils.data_processing import load_workout_data, get_file_mtime

# Load data
csv_path = 'workouts.csv'
file_mtime = get_file_mtime(csv_path)
df = load_workout_data(csv_path, file_mtime)

if df.empty:
    st.error("No workout data found. Please add some workouts first.")
    st.stop()

st.header("🏋️ Exercise Analysis")

# Exercise selector
selected_exercise = st.selectbox("Select Exercise for Analysis", df['Exercise'].unique())

exercise_data = df[df['Exercise'] == selected_exercise].copy()

if not exercise_data.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Exercise Statistics")
        st.write(f"**Total Sessions:** {len(exercise_data)}")
        st.write(f"**Average RPE:** {exercise_data['RPE'].mean():.1f}")
        st.write(f"**Max Weight:** {exercise_data['Avg_Weight'].max():.1f} lbs")
        st.write(f"**Total Volume:** {exercise_data['Total_Volume'].sum():,.0f} lbs")
    
    with col2:
        st.subheader("Recent Performance")
        recent_data = exercise_data.tail(5)[['Date', 'Avg_Weight', 'Total_Reps', 'RPE']]
        st.dataframe(recent_data, width='stretch')
    
    # Detailed progression chart
    st.subheader("Detailed Progression")
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=exercise_data['Date'],
        y=exercise_data['Avg_Weight'],
        mode='lines+markers',
        name='Average Weight',
        line=dict(color='blue')
    ))
    
    fig.add_trace(go.Scatter(
        x=exercise_data['Date'],
        y=exercise_data['Total_Reps'],
        mode='lines+markers',
        name='Total Reps',
        yaxis='y2',
        line=dict(color='red')
    ))
    
    fig.update_layout(
        title=f"{selected_exercise} - Weight and Reps Progression",
        xaxis_title="Date",
        yaxis_title="Average Weight (lbs)",
        yaxis2=dict(title="Total Reps", overlaying="y", side="right"),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, config={'displayModeBar': False})
