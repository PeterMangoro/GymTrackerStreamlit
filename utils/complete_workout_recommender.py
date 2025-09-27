"""
Complete Workout Recommendation Engine
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import random


class CompleteWorkoutRecommender:
    """Recommends complete workouts with sets, reps, and weights"""
    
    def __init__(self):
        self.exercise_database = {}
        self.user_progression = {}
        
    def build_exercise_database(self, df: pd.DataFrame):
        """Build database of exercise patterns and progressions"""
        self.exercise_database = {}
        
        for exercise in df['Exercise'].unique():
            exercise_data = df[df['Exercise'] == exercise]
            
            # Calculate exercise statistics
            stats = {
                'avg_weight': exercise_data['Avg_Weight'].mean(),
                'max_weight': exercise_data['Max_Weight'].max(),
                'avg_reps': exercise_data['Total_Reps'].mean() / exercise_data['Total_Reps'].count(),
                'max_reps': exercise_data['Max_Reps'].max(),
                'avg_sets': len(exercise_data) / exercise_data['Date'].nunique(),
                'muscle_group': exercise_data['Muscle Group'].iloc[0],
                'recent_rpe': exercise_data.tail(3)['RPE'].mean(),
                'progression_rate': self._calculate_progression_rate(exercise_data),
                'frequency': len(exercise_data),
                'last_performed': exercise_data['Date'].max()
            }
            
            self.exercise_database[exercise] = stats
    
    def _calculate_progression_rate(self, exercise_data: pd.DataFrame) -> float:
        """Calculate weight progression rate for an exercise"""
        if len(exercise_data) < 2:
            return 0
        
        # Sort by date and calculate progression
        sorted_data = exercise_data.sort_values('Date')
        weights = sorted_data['Avg_Weight'].values
        
        if len(weights) < 2:
            return 0
            
        # Calculate average weekly progression
        progression = (weights[-1] - weights[0]) / max(len(weights), 1)
        return max(0, progression)  # Only positive progression
    
    def recommend_complete_workout(self, df: pd.DataFrame, workout_type: str = "balanced", 
                                 duration_minutes: int = 60) -> Dict:
        """Recommend a complete workout with sets, reps, and weights"""
        
        # Build exercise database
        self.build_exercise_database(df)
        
        # Determine workout structure based on type and duration
        workout_structure = self._get_workout_structure(workout_type, duration_minutes)
        
        # Get recent context
        recent_context = self._get_recent_context(df)
        
        # Select exercises
        selected_exercises = self._select_exercises(workout_structure, recent_context)
        
        # Generate sets, reps, and weights
        complete_workout = self._generate_workout_details(selected_exercises, recent_context)
        
        # Calculate estimated duration and volume
        workout_summary = self._calculate_workout_summary(complete_workout)
        
        return {
            'workout_type': workout_type,
            'estimated_duration': workout_summary['duration'],
            'total_volume': workout_summary['volume'],
            'exercises': complete_workout,
            'recommendations': self._get_workout_tips(workout_type, recent_context)
        }
    
    def _get_workout_structure(self, workout_type: str, duration_minutes: int) -> Dict:
        """Define workout structure based on type and duration"""
        
        structures = {
            'balanced': {
                'muscle_groups': ['Chest', 'Back', 'Legs', 'Shoulders', 'Arms'],
                'exercises_per_group': 1,
                'total_exercises': 5,
                'sets_per_exercise': 3,
                'rest_time': 90  # seconds
            },
            'upper_body': {
                'muscle_groups': ['Chest', 'Back', 'Shoulders', 'Arms'],
                'exercises_per_group': 2,
                'total_exercises': 8,
                'sets_per_exercise': 3,
                'rest_time': 90
            },
            'lower_body': {
                'muscle_groups': ['Legs', 'Glutes', 'Hamstrings', 'Quads'],
                'exercises_per_group': 2,
                'total_exercises': 8,
                'sets_per_exercise': 3,
                'rest_time': 120
            },
            'push': {
                'muscle_groups': ['Chest', 'Shoulders', 'Triceps'],
                'exercises_per_group': 2,
                'total_exercises': 6,
                'sets_per_exercise': 3,
                'rest_time': 90
            },
            'pull': {
                'muscle_groups': ['Back', 'Biceps', 'Rear Delts'],
                'exercises_per_group': 2,
                'total_exercises': 6,
                'sets_per_exercise': 3,
                'rest_time': 90
            },
            'cardio': {
                'muscle_groups': ['Legs', 'Cardio'],
                'exercises_per_group': 1,
                'total_exercises': 4,
                'sets_per_exercise': 1,
                'rest_time': 30
            }
        }
        
        base_structure = structures.get(workout_type, structures['balanced'])
        
        # Adjust for duration
        if duration_minutes < 45:
            base_structure['total_exercises'] = max(3, base_structure['total_exercises'] - 2)
            base_structure['sets_per_exercise'] = max(2, base_structure['sets_per_exercise'] - 1)
        elif duration_minutes > 90:
            base_structure['total_exercises'] += 2
            base_structure['sets_per_exercise'] += 1
            
        return base_structure
    
    def _get_recent_context(self, df: pd.DataFrame) -> Dict:
        """Get recent workout context"""
        recent_workouts = df.tail(5)
        
        context = {
            'last_workout_date': recent_workouts.iloc[-1]['Date'] if len(recent_workouts) > 0 else None,
            'days_since_last': (datetime.now() - recent_workouts.iloc[-1]['Date']).days if len(recent_workouts) > 0 else 7,
            'recent_muscle_groups': recent_workouts['Muscle Group'].tolist(),
            'recent_rpe_avg': recent_workouts['RPE'].mean() if len(recent_workouts) > 0 else 7,
            'recent_volume_avg': recent_workouts['Total_Volume'].mean() if len(recent_workouts) > 0 else 1000,
            'recovery_status': self._assess_recovery_status(recent_workouts)
        }
        
        return context
    
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
    
    def _select_exercises(self, structure: Dict, context: Dict) -> List[str]:
        """Select exercises based on structure and context"""
        selected_exercises = []
        
        # Get available exercises by muscle group
        muscle_group_exercises = {}
        for exercise, stats in self.exercise_database.items():
            muscle_group = stats['muscle_group']
            if muscle_group not in muscle_group_exercises:
                muscle_group_exercises[muscle_group] = []
            muscle_group_exercises[muscle_group].append(exercise)
        
        # Select exercises based on workout structure
        target_muscle_groups = structure['muscle_groups']
        exercises_per_group = structure['exercises_per_group']
        
        for muscle_group in target_muscle_groups:
            if muscle_group in muscle_group_exercises:
                available_exercises = muscle_group_exercises[muscle_group]
                
                # Sort by frequency and recency
                available_exercises.sort(key=lambda x: (
                    self.exercise_database[x]['frequency'],
                    -(datetime.now() - self.exercise_database[x]['last_performed']).days
                ), reverse=True)
                
                # Select top exercises for this muscle group
                for i in range(min(exercises_per_group, len(available_exercises))):
                    if len(selected_exercises) < structure['total_exercises']:
                        selected_exercises.append(available_exercises[i])
        
        # Fill remaining slots with most frequent exercises
        while len(selected_exercises) < structure['total_exercises']:
            remaining_exercises = [ex for ex in self.exercise_database.keys() 
                                 if ex not in selected_exercises]
            if remaining_exercises:
                # Sort by frequency
                remaining_exercises.sort(key=lambda x: self.exercise_database[x]['frequency'], reverse=True)
                selected_exercises.append(remaining_exercises[0])
            else:
                break
                
        return selected_exercises
    
    def _generate_workout_details(self, exercises: List[str], context: Dict) -> List[Dict]:
        """Generate detailed workout with sets, reps, and weights"""
        workout_details = []
        
        for i, exercise in enumerate(exercises):
            if exercise not in self.exercise_database:
                continue
                
            stats = self.exercise_database[exercise]
            
            # Determine workout intensity based on context
            intensity_multiplier = self._get_intensity_multiplier(context)
            
            # Calculate sets, reps, and weight
            sets = self._calculate_sets(stats, context)
            reps = self._calculate_reps(stats, context)
            weight = self._calculate_weight(stats, context, intensity_multiplier)
            
            # Calculate rest time
            rest_time = self._calculate_rest_time(stats, context)
            
            # Generate RPE target
            rpe_target = self._calculate_rpe_target(context)
            
            exercise_detail = {
                'exercise': exercise,
                'muscle_group': stats['muscle_group'],
                'sets': sets,
                'reps': reps,
                'weight': weight,
                'rest_time': rest_time,
                'rpe_target': rpe_target,
                'notes': self._generate_exercise_notes(exercise, stats, context)
            }
            
            workout_details.append(exercise_detail)
            
        return workout_details
    
    def _get_intensity_multiplier(self, context: Dict) -> float:
        """Get intensity multiplier based on context"""
        recovery_status = context['recovery_status']
        days_since_last = context['days_since_last']
        
        if recovery_status == 'needs_rest':
            return 0.7  # Light intensity
        elif recovery_status == 'light_workout':
            return 0.85  # Moderate intensity
        elif days_since_last > 3:
            return 1.1  # Higher intensity after rest
        else:
            return 1.0  # Normal intensity
    
    def _calculate_sets(self, stats: Dict, context: Dict) -> int:
        """Calculate number of sets"""
        base_sets = 3
        
        # Adjust based on exercise frequency
        if stats['frequency'] > 10:
            base_sets += 1  # More sets for familiar exercises
        
        # Adjust based on recovery status
        if context['recovery_status'] == 'needs_rest':
            base_sets = max(2, base_sets - 1)
        elif context['recovery_status'] == 'light_workout':
            base_sets = max(2, base_sets)
            
        return base_sets
    
    def _calculate_reps(self, stats: Dict, context: Dict) -> int:
        """Calculate target reps"""
        avg_reps = stats['avg_reps']
        
        if avg_reps == 0:
            avg_reps = 10  # Default
        
        # Adjust based on exercise type
        if 'squat' in stats['muscle_group'].lower() or 'deadlift' in stats['muscle_group'].lower():
            target_reps = max(5, min(8, avg_reps))  # Lower reps for compound lifts
        elif 'curl' in stats['muscle_group'].lower() or 'extension' in stats['muscle_group'].lower():
            target_reps = max(8, min(15, avg_reps))  # Higher reps for isolation
        else:
            target_reps = max(6, min(12, avg_reps))  # Moderate reps
        
        # Adjust based on recovery
        if context['recovery_status'] == 'needs_rest':
            target_reps = min(15, target_reps + 2)  # Higher reps, lighter weight
        elif context['recovery_status'] == 'light_workout':
            target_reps = min(12, target_reps + 1)
            
        return int(target_reps)
    
    def _calculate_weight(self, stats: Dict, context: Dict, intensity_multiplier: float) -> float:
        """Calculate target weight"""
        avg_weight = stats['avg_weight']
        max_weight = stats['max_weight']
        
        if avg_weight == 0:
            avg_weight = max_weight * 0.7  # Estimate from max
        
        # Start with 80% of average weight
        base_weight = avg_weight * 0.8
        
        # Apply intensity multiplier
        target_weight = base_weight * intensity_multiplier
        
        # Ensure we don't exceed max weight
        target_weight = min(target_weight, max_weight * 0.9)
        
        # Round to nearest 5 lbs
        target_weight = round(target_weight / 5) * 5
        
        return max(5, target_weight)  # Minimum 5 lbs
    
    def _calculate_rest_time(self, stats: Dict, context: Dict) -> int:
        """Calculate rest time in seconds"""
        base_rest = 90  # 90 seconds default
        
        # Adjust based on exercise type
        if 'squat' in stats['muscle_group'].lower() or 'deadlift' in stats['muscle_group'].lower():
            base_rest = 120  # Longer rest for compound lifts
        elif 'curl' in stats['muscle_group'].lower() or 'extension' in stats['muscle_group'].lower():
            base_rest = 60  # Shorter rest for isolation
        
        # Adjust based on recovery status
        if context['recovery_status'] == 'needs_rest':
            base_rest += 30  # Longer rest when recovering
        elif context['recovery_status'] == 'light_workout':
            base_rest += 15
            
        return base_rest
    
    def _calculate_rpe_target(self, context: Dict) -> float:
        """Calculate target RPE"""
        base_rpe = 7.5
        
        # Adjust based on recovery status
        if context['recovery_status'] == 'needs_rest':
            base_rpe = 6.0  # Light intensity
        elif context['recovery_status'] == 'light_workout':
            base_rpe = 7.0  # Moderate intensity
        elif context['days_since_last'] > 3:
            base_rpe = 8.0  # Higher intensity after rest
            
        return base_rpe
    
    def _generate_exercise_notes(self, exercise: str, stats: Dict, context: Dict) -> str:
        """Generate helpful notes for the exercise"""
        notes = []
        
        # Progression note
        if stats['progression_rate'] > 0:
            notes.append(f"Great progression! Keep increasing weight gradually.")
        
        # Frequency note
        if stats['frequency'] > 15:
            notes.append("You're very familiar with this exercise.")
        elif stats['frequency'] < 5:
            notes.append("Consider adding this exercise more often.")
        
        # Recovery note
        if context['recovery_status'] == 'needs_rest':
            notes.append("Focus on form over intensity today.")
        elif context['recovery_status'] == 'light_workout':
            notes.append("Moderate intensity - listen to your body.")
        
        # Recent performance note
        if stats['recent_rpe'] > 8.5:
            notes.append("You've been pushing hard recently - good work!")
        
        return " | ".join(notes) if notes else "Focus on proper form and controlled movement."
    
    def _calculate_workout_summary(self, workout_details: List[Dict]) -> Dict:
        """Calculate workout summary statistics"""
        total_volume = 0
        total_duration = 0
        
        for exercise in workout_details:
            volume = exercise['sets'] * exercise['reps'] * exercise['weight']
            total_volume += volume
            
            # Estimate exercise duration (sets * reps * 3 seconds + rest time)
            exercise_time = (exercise['sets'] * exercise['reps'] * 3) + (exercise['sets'] * exercise['rest_time'])
            total_duration += exercise_time
        
        return {
            'volume': total_volume,
            'duration': total_duration // 60,  # Convert to minutes
            'exercises': len(workout_details)
        }
    
    def _get_workout_tips(self, workout_type: str, context: Dict) -> List[str]:
        """Get workout tips based on type and context"""
        tips = []
        
        # General tips
        tips.append("Warm up for 5-10 minutes before starting")
        tips.append("Focus on proper form over heavy weights")
        
        # Recovery-based tips
        if context['recovery_status'] == 'needs_rest':
            tips.append("Today is a recovery day - lighter weights, higher reps")
            tips.append("Consider adding stretching or mobility work")
        elif context['recovery_status'] == 'light_workout':
            tips.append("Moderate intensity - you're still recovering")
        
        # Workout type specific tips
        if workout_type == 'upper_body':
            tips.append("Start with compound movements (bench, rows)")
            tips.append("Finish with isolation exercises (curls, extensions)")
        elif workout_type == 'lower_body':
            tips.append("Start with squats or deadlifts")
            tips.append("Use longer rest periods between heavy sets")
        elif workout_type == 'balanced':
            tips.append("Alternate between push and pull movements")
            tips.append("Include both compound and isolation exercises")
        
        # Time-based tips
        if context['days_since_last'] > 3:
            tips.append("You're well-rested - you can push harder today")
        elif context['days_since_last'] < 2:
            tips.append("Short rest between workouts - moderate intensity")
        
        return tips
