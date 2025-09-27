"""
Configuration settings for the Gym Progress Tracker app.
"""

import warnings
import os

# Suppress all warnings and errors globally
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'

# Suppress specific error types
import sys
import logging

# Suppress specific warnings and errors
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=PendingDeprecationWarning)

# Suppress logging errors
logging.getLogger().setLevel(logging.ERROR)

# Suppress specific Streamlit warnings
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'

# Page configuration
PAGE_CONFIG = {
    "page_title": "Gym Progress Tracker",
    "page_icon": "💪",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Navigation pages
NAVIGATION_PAGES = [
    "📊 Dashboard",
    "🏅 Performance & Strength Insights",
    "📈 Progress Tracking", 
    "🏋️ Exercise Analysis",
    "📝 Add Workout",
    "📋 Workout History"
]

# Required CSV columns
REQUIRED_COLUMNS = ['Date', 'Exercise', 'Sets x Reps x Weight', 'RPE', 'Muscle Group']

# Detailed muscle groups (after compound group expansion)
DETAILED_MUSCLE_GROUPS = [
    "Back", "Biceps", "Calves", "Chest", "Forearms", "Glutes", 
    "Hamstrings", "Legs", "Quads", "Rear Delts", "Recovery", 
    "Shoulders", "Traps", "Triceps"
]

# Muscle group mapping for analytics (detailed -> grouped)
MUSCLE_GROUP_MAPPING = {
    # Leg muscles grouped together
    "Quads": "Legs",
    "Glutes": "Legs", 
    "Hamstrings": "Legs",
    "Calves": "Legs",
    
    # Arm muscles grouped together
    "Biceps": "Arms",
    "Triceps": "Arms",
    "Forearms": "Arms",
    
    # Shoulder muscles grouped together
    "Shoulders": "Shoulders",
    "Rear Delts": "Shoulders",
    "Traps": "Shoulders",
    
    # Keep these as individual groups
    "Back": "Back",
    "Chest": "Chest",
    "Legs": "Legs",  # Original legs category
    "Recovery": "Recovery"
}

# Grouped muscle groups for analytics
GROUPED_MUSCLE_GROUPS = [
    "Back", "Chest", "Shoulders", "Arms", "Legs", "Recovery"
]

# Compound lifts for 1RM tracking
COMPOUND_LIFTS = [
    'squat', 'bench', 'deadlift', 'overhead press', 'row', 
    'barbell row', 'bench press', 'squat', 'incline', 'press',
    'dumbbell press', 'incline bench', 'incline press'
]

# RPE categories
RPE_CATEGORIES = {
    "Easy": (1, 6),
    "Moderate": (7, 8),
    "Hard": (9, 10)
}

# High RPE threshold for recovery warnings
HIGH_RPE_THRESHOLD = 8.5
CONSECUTIVE_HIGH_RPE_WARNING = 3

# Muscle group imbalance thresholds
HIGH_VOLUME_THRESHOLD = 40  # percentage
LOW_VOLUME_THRESHOLD = 10   # percentage

# Undertrained exercise threshold (weeks)
UNDERTRAINED_THRESHOLD_WEEKS = 4
