# Gym Progress Tracker - Modular Structure

This is the refactored modular version of the Gym Progress Tracker application.

## 📁 Project Structure

```
Gym/
├── app.py                    # Main application (modular)
├── config.py                # Configuration settings
├── workouts.csv             # Data file
├── requirements.txt         # Dependencies
├── README.md               # Project documentation
├── utils/                   # Utility functions
│   ├── __init__.py
│   └── data_processing.py  # Data loading and processing functions
├── modules/                 # Page modules
│   ├── __init__.py
│   ├── dashboard.py        # Dashboard page
│   ├── performance_insights.py  # Performance & Strength Insights
│   ├── progress_tracking.py     # Progress Tracking page
│   ├── exercise_analysis.py     # Exercise Analysis page
│   └── workout_management.py    # Add Workout & History pages
└── components/             # Shared UI components
    ├── __init__.py
    └── ui_components.py    # Reusable UI components
```

## 🚀 Running the App

To run the app:

```bash
streamlit run app.py
```

## 📦 Module Descriptions

### `config.py`
- Centralized configuration settings
- Page configuration, navigation, muscle groups, thresholds
- Easy to modify without touching code

### `utils/data_processing.py`
- Data loading and caching functions
- CSV parsing and validation
- 1RM calculations and volume computations
- All data transformation logic

### `modules/` Directory
Each page is now a separate module:
- **`dashboard.py`**: Main dashboard with key metrics
- **`performance_insights.py`**: Comprehensive performance analysis
- **`progress_tracking.py`**: Progress charts and tracking
- **`exercise_analysis.py`**: Detailed exercise analysis
- **`workout_management.py`**: Add workouts and view history

### `components/ui_components.py`
- Shared UI components
- Header, sidebar, CSS rendering
- Reusable across all pages

## ✅ Benefits of Modular Structure

1. **Maintainability**: Each feature is in its own file
2. **Readability**: Smaller, focused files are easier to understand
3. **Reusability**: Components can be shared across pages
4. **Testing**: Individual modules can be tested separately
5. **Collaboration**: Multiple developers can work on different modules
6. **Configuration**: Centralized settings in `config.py`
7. **Scalability**: Easy to add new pages or features

## 🔄 Migration Complete

The original monolithic app has been replaced with a clean modular structure. All functionality is preserved with better organization.

## 🛠️ Development

To add a new page:
1. Create a new file in `pages/`
2. Add the page content following the existing pattern
3. Streamlit will automatically detect and add it to navigation
4. Add any new configuration to `config.py` if needed

To modify configuration:
- Edit `config.py` instead of hardcoding values in modules
