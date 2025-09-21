# 💪 Gym Progress Tracker

A comprehensive Streamlit application for tracking your workout progress and analyzing fitness metrics.

## Features

### 📊 Dashboard
- Key metrics overview (total workouts, exercises, volume, average RPE)
- Recent workouts display
- Muscle group distribution charts

### 📈 Progress Tracking
- Volume progression over time
- RPE (Rate of Perceived Exertion) trends
- Weight progression for specific exercises
- Customizable date ranges and exercise filters

### 🏋️ Exercise Analysis
- Detailed statistics for individual exercises
- Weight and reps progression charts
- Performance history and trends

### 📝 Add Workout
- Easy form to add new workout entries
- Supports complex set/rep/weight formats
- RPE tracking with slider input

### 📋 Workout History
- Complete workout history with filtering
- Sort by date, exercise, RPE, or volume
- Export filtered data to CSV

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run app.py
```

## Data Format

The app expects a CSV file named `workouts.csv` with the following columns:
- **Date**: Workout date (YYYY-MM-DD format)
- **Exercise**: Exercise name
- **Sets x Reps x Weight**: Format like "3x10x135lb; 2x8x155lb"
- **RPE**: Rate of Perceived Exertion (1-10 scale)
- **Muscle Group**: Target muscle group

## Usage Tips

- Use semicolons (;) to separate multiple sets in the same workout
- For failure sets, use format like "3xfailure"
- RPE scale: 1-3 (very easy), 4-6 (moderate), 7-8 (hard), 9-10 (maximal)
- The app automatically calculates total volume, average weight, and total reps

## Dark Theme Support

The app includes built-in dark theme compatibility and will automatically adapt to your system's theme preferences.

## Data Export

You can export filtered workout data from the Workout History page for backup or analysis in other tools.

