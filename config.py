"""
Configuration settings for the Gym Progress Tracker app.
"""

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

# Muscle groups
MUSCLE_GROUPS = [
    "Chest", "Back", "Shoulders", "Arms", "Biceps", "Triceps", 
    "Legs", "Rear Delts", "Core", "Other"
]

# Compound lifts for 1RM tracking
COMPOUND_LIFTS = [
    'squat', 'bench', 'deadlift', 'overhead press', 'row', 
    'barbell row', 'bench press', 'squat'
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
