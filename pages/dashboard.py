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
    # Workout Days - shows consistency
    workout_days = df['Date'].nunique()
    st.metric("Workout Days", workout_days)

with col2:
    # Avg Workouts per Day - shows training frequency
    total_workouts = len(df)
    days_since_start = (df['Date'].max() - df['Date'].min()).days + 1
    avg_workouts_per_day = total_workouts / days_since_start if days_since_start > 0 else 0
    st.metric("Avg Workouts/Day", f"{avg_workouts_per_day:.1f}")

with col3:
    # Muscle Groups per Week - shows training balance
    df['Week'] = df['Date'].dt.to_period('W')
    muscle_groups_per_week = df.groupby('Week')['Muscle Group'].nunique().mean()
    st.metric("Muscle Groups/Week", f"{muscle_groups_per_week:.1f}")

with col4:
    # Average RPE - shows training intensity
    avg_rpe = df['RPE'].mean()
    st.metric("Average RPE", f"{avg_rpe:.1f}")

# Recent workouts
st.subheader("Recent Workouts")
recent_workouts = df.tail(10)[['Date', 'Exercise', 'Muscle Group', 'RPE', 'Total_Volume']]
st.dataframe(recent_workouts, width='stretch')

# Muscle group distribution
st.subheader("Muscle Group Distribution")

# Toggle between detailed and grouped view
view_type = st.radio("View Type:", ["Grouped (Simplified)", "Detailed"], horizontal=True)

if view_type == "Grouped (Simplified)":
    muscle_counts = df['Grouped_Muscle_Group'].value_counts()
    title = "Workouts by Muscle Group (Grouped)"
else:
    muscle_counts = df['Muscle Group'].value_counts()
    title = "Workouts by Muscle Group (Detailed)"

fig_bar = px.bar(x=muscle_counts.index, y=muscle_counts.values, title=title)
st.plotly_chart(fig_bar, width='stretch')
