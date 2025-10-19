"""
Performance & Strength Insights page for the Gym Progress Tracker app.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta
from config import COMPOUND_LIFTS, HIGH_RPE_THRESHOLD, CONSECUTIVE_HIGH_RPE_WARNING, HIGH_VOLUME_THRESHOLD, LOW_VOLUME_THRESHOLD, UNDERTRAINED_THRESHOLD_WEEKS
from utils.data_processing import load_workout_data, get_file_mtime

# Load data
csv_path = 'workouts.csv'
file_mtime = get_file_mtime(csv_path)
df = load_workout_data(csv_path, file_mtime)

if df.empty:
    st.error("No workout data found. Please add some workouts first.")
    st.stop()

st.header("🏅 Performance & Strength Insights")

# Create tabs for different insight categories
tab1, tab2, tab3, tab4 = st.tabs([
    "🧠 Progress & Balance",
    "📊 Set & Rep PRs",
    "📅 Weekly/Monthly",
    "⚡ Advanced Features"
])

with tab3:
    st.subheader("📅 Weekly Training Volume by Muscle Group")
    
    # Create weekly volume by muscle group using string dates instead of Period
    df['Week_Start'] = df['Date'].dt.to_period('W').dt.start_time.dt.strftime('%Y-%m-%d')
    weekly_volume = df.groupby(['Week_Start', 'Muscle Group'])['Total_Volume'].sum().reset_index()
    
    if not weekly_volume.empty:
        fig_weekly = px.bar(weekly_volume, x='Week_Start', y='Total_Volume', color='Muscle Group',
                          title="Weekly Training Volume by Muscle Group")
        fig_weekly.update_xaxes(tickangle=45)
        st.plotly_chart(fig_weekly, config={'displayModeBar': False})
    
    # Workout Frequency Heatmap
    st.subheader("Workout Frequency Heatmap")
    
    # Create calendar heatmap data
    workout_dates = df['Date'].dt.date.value_counts().sort_index()
    
    if not workout_dates.empty:
        # Create a simple heatmap using plotly
        dates = pd.date_range(start=workout_dates.index.min(), end=workout_dates.index.max(), freq='D')
        heatmap_data = []
        
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            count = workout_dates.get(date.date(), 0)
            heatmap_data.append({
                'Date': date_str,
                'Workouts': count,
                'Day': date.day,
                'Month': date.month,
                'Year': date.year
            })
        
        heatmap_df = pd.DataFrame(heatmap_data)
        
        # Create heatmap
        fig_heatmap = px.density_heatmap(
            heatmap_df, 
            x='Month', 
            y='Day', 
            z='Workouts',
            title="Workout Frequency Calendar Heatmap",
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_heatmap, config={'displayModeBar': False})
    
    # Weekly RPE Average
    st.subheader("Weekly RPE Average")
    
    weekly_rpe = df.groupby('Week_Start')['RPE'].mean().reset_index()
    
    if not weekly_rpe.empty:
        fig_rpe = px.line(weekly_rpe, x='Week_Start', y='RPE',
                         title="Weekly Average RPE - Detect Overtraining Trends")
        fig_rpe.add_hline(y=HIGH_RPE_THRESHOLD, line_dash="dash", line_color="red", 
                         annotation_text="High RPE Warning Line")
        fig_rpe.update_xaxes(tickangle=45)
        st.plotly_chart(fig_rpe, config={'displayModeBar': False})

with tab1:
    st.subheader("🧠 Muscle Group Imbalance Alert")
    
    # Calculate training volume percentage by muscle group
    muscle_volume = df.groupby('Muscle Group')['Total_Volume'].sum()
    total_volume = muscle_volume.sum()
    muscle_percentage = (muscle_volume / total_volume * 100).round(1)
    
    # Create remarks for each muscle group
    remarks = []
    for muscle, percentage in muscle_percentage.items():
        if percentage > HIGH_VOLUME_THRESHOLD:
            remarks.append("⚠️ Very high training volume")
        elif percentage < LOW_VOLUME_THRESHOLD:
            remarks.append("⚠️ Low training volume")
        elif percentage > 25:
            remarks.append("✅ Good training volume")
        else:
            remarks.append("✅ Balanced training volume")
    
    # Display muscle group percentages with remarks
    muscle_df = pd.DataFrame({
        'Muscle Group': muscle_percentage.index,
        'Training Volume %': muscle_percentage.values,
        'Remarks': remarks
    }).sort_values('Training Volume %', ascending=False)
    
    st.dataframe(muscle_df, width='stretch')
    
    # Top 5 Most Trained Exercises
    st.subheader("Top 5 Most Trained Exercises")
    
    exercise_counts = df['Exercise'].value_counts().head(5)
    
    fig_top_exercises = px.bar(
        x=exercise_counts.values, 
        y=exercise_counts.index,
        orientation='h',
        title="Most Frequently Trained Exercises"
    )
    fig_top_exercises.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_top_exercises, config={'displayModeBar': False})
    
    # Undertrained Exercises
    st.subheader("Undertrained Exercises")
    
    # Find exercises not trained in the last X weeks
    weeks_ago = df['Date'].max() - timedelta(weeks=UNDERTRAINED_THRESHOLD_WEEKS)
    recent_exercises = df[df['Date'] >= weeks_ago]['Exercise'].unique()
    all_exercises = df['Exercise'].unique()
    undertrained = [ex for ex in all_exercises if ex not in recent_exercises]
    
    if undertrained:
        st.warning(f"Exercises not trained in the last {UNDERTRAINED_THRESHOLD_WEEKS} weeks: {', '.join(undertrained)}")
    else:
        st.success("✅ All exercises have been trained recently")

with tab4:
    st.subheader("⚡ Intensity Zones (RPE Categories)")
    
    # Categorize workouts by RPE
    def categorize_rpe(rpe):
        if rpe < 7:
            return "Easy (<7)"
        elif rpe <= 8:
            return "Moderate (7-8)"
        else:
            return "Hard (>8)"
    
    df['RPE_Category'] = df['RPE'].apply(categorize_rpe)
    rpe_counts = df['RPE_Category'].value_counts()
    
    fig_intensity = px.bar(x=rpe_counts.index, y=rpe_counts.values,
                          title="Training Intensity Distribution")
    st.plotly_chart(fig_intensity, config={'displayModeBar': False})
    
    # Fatigue & Recovery Score
    st.subheader("Fatigue & Recovery Score")
    
    # Calculate consecutive high RPE sessions
    df_sorted = df.sort_values('Date')
    df_sorted['High_RPE'] = df_sorted['RPE'] > HIGH_RPE_THRESHOLD
    df_sorted['Consecutive_High_RPE'] = df_sorted['High_RPE'].groupby((~df_sorted['High_RPE']).cumsum()).cumsum()
    
    max_consecutive = df_sorted['Consecutive_High_RPE'].max()
    
    if max_consecutive >= CONSECUTIVE_HIGH_RPE_WARNING:
        st.error(f"🚨 Recovery Warning: {max_consecutive} consecutive sessions with RPE > {HIGH_RPE_THRESHOLD}")
        st.info("Consider taking a rest day or reducing training intensity")
    elif max_consecutive >= 2:
        st.warning(f"⚠️ High intensity streak: {max_consecutive} consecutive sessions with RPE > {HIGH_RPE_THRESHOLD}")
    else:
        st.success("✅ Training intensity appears manageable")
    
    # Show recent RPE trend
    recent_rpe = df_sorted.tail(10)[['Date', 'Exercise', 'RPE']]
    st.subheader("Recent RPE Trend")
    st.dataframe(recent_rpe, width='stretch')

with tab2:
    st.subheader("📊 Set & Rep Personal Records")
    
    # Find set & rep PRs for each exercise
    pr_data = []
    
    for exercise in df['Exercise'].unique():
        exercise_data = df[df['Exercise'] == exercise]
        
        # Get all unique weight-rep combinations
        weight_rep_combos = []
        for _, row in exercise_data.iterrows():
            for set_data in row['Parsed_Sets']:
                if set_data['weight'] > 0 and set_data['reps'] > 0:
                    weight_rep_combos.append({
                        'weight': set_data['weight'],
                        'reps': set_data['reps'],
                        'date': row['Date']
                    })
        
        if weight_rep_combos:
            # Find max reps at each weight
            weight_df = pd.DataFrame(weight_rep_combos)
            max_reps_by_weight = weight_df.groupby('weight')['reps'].max().reset_index()
            
            # Get the most impressive records (top 5 by weight*reps)
            max_reps_by_weight['score'] = max_reps_by_weight['weight'] * max_reps_by_weight['reps']
            top_records = max_reps_by_weight.nlargest(5, 'score')
            
            for _, record in top_records.iterrows():
                pr_data.append({
                    'Exercise': exercise,
                    'Weight (lbs)': record['weight'],
                    'Max Reps': record['reps'],
                    'Score': record['score']
                })
    
    if pr_data:
        pr_df = pd.DataFrame(pr_data)
        pr_df = pr_df.sort_values('Score', ascending=False).head(10)
        st.dataframe(pr_df, width='stretch')
    else:
        st.info("No set & rep PR data available")