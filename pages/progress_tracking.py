"""
Progress Tracking page for the Gym Progress Tracker app.
"""

import streamlit as st
import plotly.express as px


"""
Progress Tracking page for the Gym Progress Tracker app.
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

st.header("📈 Progress Tracking")

# Date range selector
date_range = st.date_input(
    "Select date range",
    value=(df['Date'].min().date(), df['Date'].max().date()),
    min_value=df['Date'].min().date(),
    max_value=df['Date'].max().date()
)

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]
else:
    filtered_df = df

# Exercise selector
selected_exercise = st.selectbox("Select Exercise", ['All'] + list(df['Exercise'].unique()))

if selected_exercise != 'All':
    filtered_df = filtered_df[filtered_df['Exercise'] == selected_exercise]

if not filtered_df.empty:
    # Volume over time
    st.subheader("Volume Over Time")
    daily_volume = filtered_df.groupby('Date')['Total_Volume'].sum().reset_index()
    
    fig_volume = px.line(daily_volume, x='Date', y='Total_Volume', 
                       title="Daily Training Volume")
    st.plotly_chart(fig_volume, config={'displayModeBar': False})
    
    # RPE over time
    st.subheader("RPE Over Time")
    daily_rpe = filtered_df.groupby('Date')['RPE'].mean().reset_index()
    
    fig_rpe = px.line(daily_rpe, x='Date', y='RPE', 
                     title="Average RPE Over Time")
    st.plotly_chart(fig_rpe, config={'displayModeBar': False})
    
    # Weight progression
    if selected_exercise != 'All':
        st.subheader("Weight Progression")
        weight_data = filtered_df[['Date', 'Avg_Weight']].dropna()
        
        if not weight_data.empty:
            fig_weight = px.line(weight_data, x='Date', y='Avg_Weight',
                               title=f"Average Weight Progression - {selected_exercise}")
            st.plotly_chart(fig_weight, config={'displayModeBar': False})
