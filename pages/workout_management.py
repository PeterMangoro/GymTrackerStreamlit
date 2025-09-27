"""
Workout Management page for the Gym Progress Tracker app.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from config import MUSCLE_GROUPS
from utils.data_processing import load_workout_data, get_file_mtime

# Load data
csv_path = 'workouts.csv'
file_mtime = get_file_mtime(csv_path)
df = load_workout_data(csv_path, file_mtime)

st.header("📝 Add New Workout")

with st.form("add_workout_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        date = st.date_input("Date", value=datetime.now().date())
        exercise = st.text_input("Exercise")
        muscle_group = st.selectbox("Muscle Group", MUSCLE_GROUPS)
    
    with col2:
        sets_reps_weight = st.text_area(
            "Sets x Reps x Weight", 
            placeholder="Example: 3x10x135lb; 2x8x155lb",
            help="Format: sets x reps x weight. Separate multiple sets with semicolons."
        )
        rpe = st.slider("RPE (Rate of Perceived Exertion)", 1, 10, 8)
    
    submitted = st.form_submit_button("Add Workout")
    
    if submitted:
        if exercise and sets_reps_weight:
            # Add to CSV
            new_row = {
                'Date': date.strftime('%Y-%m-%d'),
                'Exercise': exercise,
                'Sets x Reps x Weight': sets_reps_weight,
                'RPE': rpe,
                'Muscle Group': muscle_group
            }
            
            # Append to CSV
            try:
                df = pd.read_csv('workouts.csv')
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_csv('workouts.csv', index=False)
                st.success("Workout added successfully!")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Error adding workout: {str(e)}")
        else:
            st.error("Please fill in all required fields.")

st.header("📋 Workout History")

if not df.empty:
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        muscle_filter = st.selectbox("Filter by Muscle Group", ['All'] + list(df['Muscle Group'].unique()))
    
    with col2:
        exercise_filter = st.selectbox("Filter by Exercise", ['All'] + list(df['Exercise'].unique()))
    
    with col3:
        sort_by = st.selectbox("Sort by", ['Date (Newest)', 'Date (Oldest)', 'Exercise', 'RPE', 'Total Volume'])
    
    # Apply filters
    filtered_df = df.copy()
    
    if muscle_filter != 'All':
        filtered_df = filtered_df[filtered_df['Muscle Group'] == muscle_filter]
    
    if exercise_filter != 'All':
        filtered_df = filtered_df[filtered_df['Exercise'] == exercise_filter]
    
    # Sort data
    if sort_by == 'Date (Newest)':
        filtered_df = filtered_df.sort_values('Date', ascending=False)
    elif sort_by == 'Date (Oldest)':
        filtered_df = filtered_df.sort_values('Date', ascending=True)
    elif sort_by == 'Exercise':
        filtered_df = filtered_df.sort_values('Exercise')
    elif sort_by == 'RPE':
        filtered_df = filtered_df.sort_values('RPE', ascending=False)
    elif sort_by == 'Total Volume':
        filtered_df = filtered_df.sort_values('Total_Volume', ascending=False)
    
    # Display data
    display_columns = ['Date', 'Exercise', 'Muscle Group', 'Sets x Reps x Weight', 'RPE', 'Total_Volume', 'Avg_Weight']
    st.dataframe(filtered_df[display_columns], width='stretch')
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name=f"workout_history_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
else:
    st.info("No workout data found. Add some workouts to see the history.")