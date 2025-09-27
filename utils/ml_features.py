"""
Machine Learning Feature Engineering for Workout Recommendations
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class WorkoutFeatureEngineer:
    """Feature engineering for workout recommendation ML models"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df = self.df.sort_values('Date')
        
    def create_user_features(self) -> Dict:
        """Create user-level features"""
        features = {}
        
        # Basic stats
        features['total_workouts'] = len(self.df)
        features['workout_days'] = self.df['Date'].nunique()
        features['avg_workouts_per_day'] = features['total_workouts'] / max(1, features['workout_days'])
        
        # Time-based features
        if len(self.df) > 1:
            features['days_since_first_workout'] = (self.df['Date'].max() - self.df['Date'].min()).days
            features['days_since_last_workout'] = (datetime.now() - self.df['Date'].max()).days
        else:
            features['days_since_first_workout'] = 0
            features['days_since_last_workout'] = 0
            
        # RPE patterns
        features['avg_rpe'] = self.df['RPE'].mean()
        features['rpe_std'] = self.df['RPE'].std()
        features['high_rpe_ratio'] = (self.df['RPE'] > 8.5).mean()
        
        # Volume patterns
        features['avg_total_volume'] = self.df['Total_Volume'].mean()
        features['volume_trend'] = self._calculate_trend(self.df['Total_Volume'])
        
        # Strength progression
        if 'Estimated_1RM' in self.df.columns:
            features['strength_trend'] = self._calculate_trend(self.df['Estimated_1RM'])
        else:
            features['strength_trend'] = 0
            
        return features
    
    def create_muscle_group_features(self) -> Dict:
        """Create muscle group specific features"""
        muscle_features = {}
        
        # Volume by muscle group
        muscle_volume = self.df.groupby('Muscle Group')['Total_Volume'].sum()
        total_volume = muscle_volume.sum()
        
        for muscle in muscle_volume.index:
            muscle_features[f'{muscle.lower()}_volume_pct'] = (muscle_volume[muscle] / total_volume) * 100
            muscle_features[f'{muscle.lower()}_workout_count'] = len(self.df[self.df['Muscle Group'] == muscle])
            muscle_features[f'{muscle.lower()}_avg_rpe'] = self.df[self.df['Muscle Group'] == muscle]['RPE'].mean()
            
        # Muscle group balance
        muscle_features['muscle_group_balance'] = self._calculate_balance_score(muscle_volume)
        
        return muscle_features
    
    def create_exercise_features(self) -> Dict:
        """Create exercise-specific features"""
        exercise_features = {}
        
        # Exercise frequency
        exercise_counts = self.df['Exercise'].value_counts()
        exercise_features['most_frequent_exercise'] = exercise_counts.index[0] if len(exercise_counts) > 0 else None
        exercise_features['exercise_variety'] = len(exercise_counts)
        exercise_features['top_5_exercises_pct'] = (exercise_counts.head(5).sum() / len(self.df)) * 100
        
        # Exercise progression
        for exercise in exercise_counts.head(10).index:
            exercise_data = self.df[self.df['Exercise'] == exercise]
            if len(exercise_data) > 1:
                exercise_features[f'{exercise.lower().replace(" ", "_")}_progression'] = self._calculate_trend(exercise_data['Avg_Weight'])
            else:
                exercise_features[f'{exercise.lower().replace(" ", "_")}_progression'] = 0
                
        return exercise_features
    
    def create_temporal_features(self) -> Dict:
        """Create time-based features"""
        temporal_features = {}
        
        # Weekly patterns
        self.df['Week'] = self.df['Date'].dt.isocalendar().week
        weekly_volume = self.df.groupby('Week')['Total_Volume'].sum()
        
        temporal_features['weekly_volume_avg'] = weekly_volume.mean()
        temporal_features['weekly_volume_std'] = weekly_volume.std()
        temporal_features['weekly_consistency'] = 1 - (weekly_volume.std() / max(weekly_volume.mean(), 1))
        
        # Day of week patterns
        self.df['DayOfWeek'] = self.df['Date'].dt.day_name()
        day_patterns = self.df.groupby('DayOfWeek').size()
        temporal_features['preferred_workout_days'] = day_patterns.nlargest(3).index.tolist()
        
        # Recovery patterns
        temporal_features['avg_rest_days'] = self._calculate_avg_rest_days()
        
        return temporal_features
    
    def create_context_features(self, target_date: datetime = None) -> Dict:
        """Create context features for a specific date"""
        if target_date is None:
            target_date = datetime.now()
            
        context_features = {}
        
        # Recent workout context
        recent_workouts = self.df[self.df['Date'] <= target_date].tail(5)
        
        if len(recent_workouts) > 0:
            context_features['last_workout_muscle_group'] = recent_workouts.iloc[-1]['Muscle Group']
            context_features['last_workout_rpe'] = recent_workouts.iloc[-1]['RPE']
            context_features['last_workout_volume'] = recent_workouts.iloc[-1]['Total_Volume']
            context_features['days_since_last_workout'] = (target_date - recent_workouts.iloc[-1]['Date']).days
            
            # Recent muscle group frequency
            recent_muscle_groups = recent_workouts['Muscle Group'].value_counts()
            context_features['recent_muscle_group_frequency'] = recent_muscle_groups.to_dict()
            
            # Recovery status
            context_features['recovery_status'] = self._assess_recovery_status(recent_workouts)
        else:
            context_features['last_workout_muscle_group'] = None
            context_features['last_workout_rpe'] = 0
            context_features['last_workout_volume'] = 0
            context_features['days_since_last_workout'] = 999
            context_features['recent_muscle_group_frequency'] = {}
            context_features['recovery_status'] = 'ready'
            
        return context_features
    
    def _calculate_trend(self, series: pd.Series) -> float:
        """Calculate trend slope for a series"""
        if len(series) < 2:
            return 0
        
        x = np.arange(len(series))
        y = series.values
        
        # Remove NaN values
        mask = ~np.isnan(y)
        if mask.sum() < 2:
            return 0
            
        x_clean = x[mask]
        y_clean = y[mask]
        
        # Calculate slope
        slope = np.polyfit(x_clean, y_clean, 1)[0]
        return slope
    
    def _calculate_balance_score(self, muscle_volume: pd.Series) -> float:
        """Calculate muscle group balance score (0-1, higher is more balanced)"""
        if len(muscle_volume) == 0:
            return 0
            
        # Calculate coefficient of variation (lower = more balanced)
        cv = muscle_volume.std() / max(muscle_volume.mean(), 1)
        
        # Convert to balance score (0-1)
        balance_score = max(0, 1 - cv)
        return balance_score
    
    def _calculate_avg_rest_days(self) -> float:
        """Calculate average rest days between workouts"""
        if len(self.df) < 2:
            return 0
            
        dates = sorted(self.df['Date'].unique())
        rest_days = []
        
        for i in range(1, len(dates)):
            rest_days.append((dates[i] - dates[i-1]).days)
            
        return np.mean(rest_days) if rest_days else 0
    
    def _assess_recovery_status(self, recent_workouts: pd.DataFrame) -> str:
        """Assess recovery status based on recent workouts"""
        if len(recent_workouts) == 0:
            return 'ready'
            
        # Check for consecutive high RPE workouts
        high_rpe_count = (recent_workouts['RPE'] > 8.5).sum()
        
        if high_rpe_count >= 3:
            return 'needs_rest'
        elif high_rpe_count >= 2:
            return 'light_workout'
        else:
            return 'ready'
    
    def get_all_features(self, target_date: datetime = None) -> Dict:
        """Get all engineered features"""
        features = {}
        
        features.update(self.create_user_features())
        features.update(self.create_muscle_group_features())
        features.update(self.create_exercise_features())
        features.update(self.create_temporal_features())
        features.update(self.create_context_features(target_date))
        
        return features


def create_exercise_embeddings(df: pd.DataFrame) -> Dict:
    """Create exercise embeddings based on muscle groups and characteristics"""
    embeddings = {}
    
    # Exercise characteristics
    exercise_chars = {
        'compound': ['squat', 'deadlift', 'bench', 'press', 'row', 'pull'],
        'isolation': ['curl', 'extension', 'fly', 'raise'],
        'upper_body': ['bench', 'press', 'curl', 'row', 'pull', 'fly'],
        'lower_body': ['squat', 'deadlift', 'lunge', 'press'],
        'push': ['bench', 'press', 'extension', 'fly'],
        'pull': ['row', 'curl', 'pull', 'lat']
    }
    
    for exercise in df['Exercise'].unique():
        exercise_lower = exercise.lower()
        embedding = []
        
        for category, keywords in exercise_chars.items():
            embedding.append(1 if any(keyword in exercise_lower for keyword in keywords) else 0)
            
        # Add muscle group info
        exercise_muscle = df[df['Exercise'] == exercise]['Muscle Group'].iloc[0]
        muscle_groups = ['Back', 'Chest', 'Shoulders', 'Arms', 'Legs', 'Recovery']
        for muscle in muscle_groups:
            embedding.append(1 if muscle in exercise_muscle else 0)
            
        embeddings[exercise] = np.array(embedding)
        
    return embeddings


def create_workout_sequences(df: pd.DataFrame, sequence_length: int = 5) -> List[List[str]]:
    """Create workout sequences for sequence-based recommendations"""
    sequences = []
    
    # Group by date and create sequences
    df_sorted = df.sort_values('Date')
    
    for i in range(len(df_sorted) - sequence_length + 1):
        sequence = df_sorted.iloc[i:i+sequence_length]['Exercise'].tolist()
        sequences.append(sequence)
        
    return sequences
