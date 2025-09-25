import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re
import numpy as np
import os

# Page configuration
st.set_page_config(
    page_title="Gym Progress Tracker",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme compatibility
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

@st.cache_data
def load_workout_data(csv_path, file_mtime):
    """Load and preprocess workout data from CSV"""
    try:
        df = pd.read_csv(csv_path)
        
        # Convert date column
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Parse sets x reps x weight data
        df['Parsed_Sets'] = df['Sets x Reps x Weight'].apply(parse_sets_reps_weight)
        
        # Calculate total volume (sets * reps * weight)
        df['Total_Volume'] = df['Parsed_Sets'].apply(calculate_total_volume)
        
        # Calculate average weight
        df['Avg_Weight'] = df['Parsed_Sets'].apply(calculate_avg_weight)
        
        # Calculate total reps
        df['Total_Reps'] = df['Parsed_Sets'].apply(calculate_total_reps)
        
        return df
    except FileNotFoundError:
        st.error("workouts.csv file not found. Please ensure the file exists in the same directory.")
        return pd.DataFrame()

def parse_sets_reps_weight(sets_string):
    """Parse sets x reps x weight string into structured data"""
    if pd.isna(sets_string):
        return []
    
    sets_data = []
    # Split by semicolon to handle multiple sets
    set_groups = sets_string.split(';')
    
    for set_group in set_groups:
        set_group = set_group.strip()
        
        # Handle different formats
        if 'x' in set_group:
            parts = set_group.split('x')
            if len(parts) >= 2:
                try:
                    sets = int(parts[0])
                    reps = int(parts[1])
                    weight_str = parts[2] if len(parts) > 2 else '0'
                    
                    # Extract weight number
                    weight_match = re.search(r'(\d+(?:\.\d+)?)', weight_str)
                    weight = float(weight_match.group(1)) if weight_match else 0
                    
                    sets_data.append({
                        'sets': sets,
                        'reps': reps,
                        'weight': weight
                    })
                except (ValueError, IndexError):
                    continue
        elif 'failure' in set_group.lower():
            # Handle failure sets
            sets_match = re.search(r'(\d+)x', set_group)
            sets = int(sets_match.group(1)) if sets_match else 1
            sets_data.append({
                'sets': sets,
                'reps': 0,  # failure sets
                'weight': 0
            })
    
    return sets_data

def calculate_total_volume(sets_data):
    """Calculate total volume (sets * reps * weight)"""
    if not sets_data:
        return 0
    
    total_volume = 0
    for set_data in sets_data:
        if set_data['reps'] > 0:  # Skip failure sets for volume calculation
            total_volume += set_data['sets'] * set_data['reps'] * set_data['weight']
    return total_volume

def calculate_avg_weight(sets_data):
    """Calculate average weight across all sets"""
    if not sets_data:
        return 0
    
    total_weight = 0
    total_sets = 0
    
    for set_data in sets_data:
        if set_data['weight'] > 0:
            total_weight += set_data['sets'] * set_data['weight']
            total_sets += set_data['sets']
    
    return total_weight / total_sets if total_sets > 0 else 0

def calculate_total_reps(sets_data):
    """Calculate total reps across all sets"""
    if not sets_data:
        return 0
    
    total_reps = 0
    for set_data in sets_data:
        if set_data['reps'] > 0:  # Skip failure sets
            total_reps += set_data['sets'] * set_data['reps']
    return total_reps

def main():
    st.markdown('<h1 class="main-header">💪 Gym Progress Tracker</h1>', unsafe_allow_html=True)
    
    # Load data with cache invalidation on file change
    csv_path = 'workouts.csv'
    try:
        file_mtime = os.path.getmtime(csv_path)
    except FileNotFoundError:
        file_mtime = 0
    df = load_workout_data(csv_path, file_mtime)
    
    if df.empty:
        st.stop()
    
    # Sidebar
    st.sidebar.title("Navigation")
    if st.sidebar.button("Refresh data"):
        st.cache_data.clear()
        st.rerun()
    page = st.sidebar.selectbox("Choose a page", [
        "📊 Dashboard",
        "📈 Progress Tracking", 
        "🏋️ Exercise Analysis",
        "📝 Add Workout",
        "📋 Workout History"
    ])
    
    if page == "📊 Dashboard":
        show_dashboard(df)
    elif page == "📈 Progress Tracking":
        show_progress_tracking(df)
    elif page == "🏋️ Exercise Analysis":
        show_exercise_analysis(df)
    elif page == "📝 Add Workout":
        show_add_workout()
    elif page == "📋 Workout History":
        show_workout_history(df)

def show_dashboard(df):
    """Display main dashboard with key metrics"""
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
    st.dataframe(recent_workouts, use_container_width=True)
    
    # Muscle group distribution
    st.subheader("Muscle Group Distribution")
    muscle_counts = df['Muscle Group'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_pie = px.pie(values=muscle_counts.values, names=muscle_counts.index, 
                        title="Workouts by Muscle Group")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        fig_bar = px.bar(x=muscle_counts.index, y=muscle_counts.values,
                        title="Workouts by Muscle Group")
        st.plotly_chart(fig_bar, use_container_width=True)

def show_progress_tracking(df):
    """Display progress tracking charts"""
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
        st.plotly_chart(fig_volume, use_container_width=True)
        
        # RPE over time
        st.subheader("RPE Over Time")
        daily_rpe = filtered_df.groupby('Date')['RPE'].mean().reset_index()
        
        fig_rpe = px.line(daily_rpe, x='Date', y='RPE', 
                         title="Average RPE Over Time")
        st.plotly_chart(fig_rpe, use_container_width=True)
        
        # Weight progression
        if selected_exercise != 'All':
            st.subheader("Weight Progression")
            weight_data = filtered_df[['Date', 'Avg_Weight']].dropna()
            
            if not weight_data.empty:
                fig_weight = px.line(weight_data, x='Date', y='Avg_Weight',
                                   title=f"Average Weight Progression - {selected_exercise}")
                st.plotly_chart(fig_weight, use_container_width=True)

def show_exercise_analysis(df):
    """Display detailed exercise analysis"""
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
            st.dataframe(recent_data, use_container_width=True)
        
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
        
        st.plotly_chart(fig, use_container_width=True)

def show_add_workout():
    """Display form to add new workout"""
    st.header("📝 Add New Workout")
    
    with st.form("add_workout_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input("Date", value=datetime.now().date())
            exercise = st.text_input("Exercise")
            muscle_group = st.selectbox("Muscle Group", [
                "Chest", "Back", "Shoulders", "Arms", "Biceps", "Triceps", 
                "Legs", "Rear Delts", "Core", "Other"
            ])
        
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

def show_workout_history(df):
    """Display complete workout history"""
    st.header("📋 Workout History")
    
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
    st.dataframe(filtered_df[display_columns], use_container_width=True)
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name=f"workout_history_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()

