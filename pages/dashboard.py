"""
Dashboard page for the Gym Progress Tracker app.
"""

import streamlit as st
import plotly.express as px
from utils.data_processing import load_workout_data, get_file_mtime

# Load data
csv_path = 'workouts.csv'
file_mtime = get_file_mtime(csv_path)
df = load_workout_data(csv_path, file_mtime)

if df.empty:
    st.error("No workout data found. Please add some workouts first.")
    st.stop()

st.header("📊 Workout Dashboard")

# Key metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_workouts = len(df)
    st.metric("Total Workouts", total_workouts)

with col2:
    total_exercises = df['Exercise'].nunique()
    st.metric("Unique Exercises", total_exercises)

with col3:
    total_volume = df['Total_Volume'].sum()
    st.metric("Total Volume (lbs)", f"{total_volume:,.0f}")

with col4:
    avg_rpe = df['RPE'].mean()
    st.metric("Average RPE", f"{avg_rpe:.1f}")

# Recent workouts
st.subheader("Recent Workouts")
recent_workouts = df.tail(10)[['Date', 'Exercise', 'Muscle Group', 'RPE', 'Total_Volume']]
st.dataframe(recent_workouts, width='stretch')

# Muscle group distribution
st.subheader("Muscle Group Distribution")
muscle_counts = df['Muscle Group'].value_counts()

fig_bar = px.bar(x=muscle_counts.index, y=muscle_counts.values,
                title="Workouts by Muscle Group")
st.plotly_chart(fig_bar, width='stretch')
