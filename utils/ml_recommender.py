"""
Main ML Recommendation Engine
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import streamlit as st

from utils.ml_features import WorkoutFeatureEngineer, create_exercise_embeddings, create_workout_sequences
from utils.ml_models import (
    CollaborativeFilteringModel, 
    ContentBasedModel, 
    HybridRecommendationModel,
    WorkoutSequenceModel
)


class MLWorkoutRecommender:
    """Main ML-based workout recommendation engine"""
    
    def __init__(self):
        self.feature_engineer = None
        self.exercise_embeddings = None
        self.hybrid_model = None
        self.sequence_model = None
        self.is_trained = False
        
    def train(self, df: pd.DataFrame):
        """Train all ML models"""
        try:
            # Initialize feature engineer
            self.feature_engineer = WorkoutFeatureEngineer(df)
            
            # Create exercise embeddings
            self.exercise_embeddings = create_exercise_embeddings(df)
            
            # Get user features
            user_features = self.feature_engineer.get_all_features()
            
            # Train individual models first
            self.collaborative_model = CollaborativeFilteringModel()
            self.collaborative_model.fit(df, user_features)
            
            self.content_model = ContentBasedModel()
            self.content_model.fit(df, self.exercise_embeddings)
            
            # Train sequence model
            self.sequence_model = WorkoutSequenceModel()
            self.sequence_model.fit(df)
            
            # Create simplified hybrid model
            self.hybrid_model = HybridRecommendationModel()
            self.hybrid_model.collaborative_model = self.collaborative_model
            self.hybrid_model.content_model = self.content_model
            
            self.is_trained = True
            
            return True
            
        except Exception as e:
            print(f"Error training ML models: {str(e)}")
            return False
    
    def get_recommendations(self, df: pd.DataFrame, recommendation_type: str = "hybrid", 
                          n_recommendations: int = 5) -> Dict:
        """Get workout recommendations"""
        if not self.is_trained:
            return {"error": "Models not trained yet"}
            
        try:
            # Get current context
            context_features = self.feature_engineer.create_context_features()
            
            # Get recent exercises
            recent_exercises = self._get_recent_exercises(df, days=7)
            
            recommendations = {}
            
            if recommendation_type == "hybrid":
                recommendations = self._get_hybrid_recommendations(
                    recent_exercises, context_features, n_recommendations
                )
            elif recommendation_type == "collaborative":
                recommendations = self._get_collaborative_recommendations(
                    recent_exercises, n_recommendations
                )
            elif recommendation_type == "content":
                recommendations = self._get_content_recommendations(
                    recent_exercises, n_recommendations
                )
            elif recommendation_type == "sequence":
                recommendations = self._get_sequence_recommendations(
                    recent_exercises, n_recommendations
                )
            elif recommendation_type == "context_aware":
                recommendations = self._get_context_aware_recommendations(
                    df, context_features, n_recommendations
                )
                
            return recommendations
            
        except Exception as e:
            return {"error": f"Error generating recommendations: {str(e)}"}
    
    def _get_recent_exercises(self, df: pd.DataFrame, days: int = 7) -> List[str]:
        """Get exercises from recent workouts"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_data = df[df['Date'] >= cutoff_date]
        return recent_data['Exercise'].unique().tolist()
    
    def _get_hybrid_recommendations(self, recent_exercises: List[str], 
                                  context_features: Dict, n_recommendations: int) -> Dict:
        """Get hybrid recommendations"""
        recommendations = self.hybrid_model.recommend(
            recent_exercises, context_features, n_recommendations
        )
        
        return {
            "type": "Hybrid (Collaborative + Content + Context)",
            "recommendations": recommendations,
            "reasoning": self._generate_reasoning("hybrid", recent_exercises, context_features)
        }
    
    def _get_collaborative_recommendations(self, recent_exercises: List[str], 
                                         n_recommendations: int) -> Dict:
        """Get collaborative filtering recommendations"""
        recommendations = self.hybrid_model.collaborative_model.recommend(
            recent_exercises, n_recommendations
        )
        
        return {
            "type": "Collaborative Filtering",
            "recommendations": recommendations,
            "reasoning": self._generate_reasoning("collaborative", recent_exercises)
        }
    
    def _get_content_recommendations(self, recent_exercises: List[str], 
                                   n_recommendations: int) -> Dict:
        """Get content-based recommendations"""
        recommendations = self.hybrid_model.content_model.recommend(
            recent_exercises, n_recommendations
        )
        
        return {
            "type": "Content-Based Filtering",
            "recommendations": recommendations,
            "reasoning": self._generate_reasoning("content", recent_exercises)
        }
    
    def _get_sequence_recommendations(self, recent_exercises: List[str], 
                                    n_recommendations: int) -> Dict:
        """Get sequence-based recommendations"""
        recommendations = self.sequence_model.recommend_next(
            recent_exercises, n_recommendations
        )
        
        return {
            "type": "Sequence-Based",
            "recommendations": recommendations,
            "reasoning": self._generate_reasoning("sequence", recent_exercises)
        }
    
    def _get_context_aware_recommendations(self, df: pd.DataFrame, 
                                         context_features: Dict, n_recommendations: int) -> Dict:
        """Get context-aware recommendations"""
        # Analyze current state
        muscle_balance = self._analyze_muscle_balance(df)
        recovery_status = context_features.get('recovery_status', 'ready')
        last_muscle_group = context_features.get('last_workout_muscle_group')
        
        recommendations = []
        reasoning_parts = []
        
        # Recovery-based recommendations
        if recovery_status == 'needs_rest':
            recommendations = ['Rest Day', 'Light Stretching', 'Walking']
            reasoning_parts.append("High RPE trend suggests need for recovery")
        elif recovery_status == 'light_workout':
            recommendations = ['Calf Raises', 'Lateral Raises', 'Facepulls', 'Light Cardio']
            reasoning_parts.append("Moderate recovery needed - light exercises recommended")
        else:
            # Muscle balance-based recommendations
            if muscle_balance['weakest_muscle_group']:
                weakest = muscle_balance['weakest_muscle_group']
                recommendations = self._get_exercises_for_muscle_group(weakest, df)
                reasoning_parts.append(f"{weakest} is undertrained - focusing on {weakest} exercises")
            
            # Avoid same muscle group as last workout
            if last_muscle_group and last_muscle_group != 'Recovery':
                opposite_groups = self._get_opposite_muscle_groups(last_muscle_group)
                if opposite_groups:
                    additional_recs = []
                    for group in opposite_groups:
                        additional_recs.extend(self._get_exercises_for_muscle_group(group, df))
                    recommendations.extend(additional_recs[:3])
                    reasoning_parts.append(f"Last workout was {last_muscle_group} - focusing on different muscle groups")
        
        # Remove duplicates and limit
        recommendations = list(dict.fromkeys(recommendations))[:n_recommendations]
        
        return {
            "type": "Context-Aware",
            "recommendations": recommendations,
            "reasoning": " | ".join(reasoning_parts)
        }
    
    def _analyze_muscle_balance(self, df: pd.DataFrame) -> Dict:
        """Analyze muscle group balance"""
        muscle_volume = df.groupby('Muscle Group')['Total_Volume'].sum()
        total_volume = muscle_volume.sum()
        
        if total_volume == 0:
            return {"weakest_muscle_group": None, "balance_score": 0}
        
        muscle_percentages = (muscle_volume / total_volume * 100).round(1)
        
        # Find weakest muscle group (excluding Recovery)
        non_recovery = muscle_percentages.drop('Recovery', errors='ignore')
        weakest = non_recovery.idxmin() if len(non_recovery) > 0 else None
        
        # Calculate balance score
        balance_score = 1 - (muscle_percentages.std() / muscle_percentages.mean())
        
        return {
            "weakest_muscle_group": weakest,
            "balance_score": balance_score,
            "muscle_percentages": muscle_percentages.to_dict()
        }
    
    def _get_exercises_for_muscle_group(self, muscle_group: str, df: pd.DataFrame) -> List[str]:
        """Get exercises for a specific muscle group"""
        muscle_exercises = df[df['Muscle Group'] == muscle_group]['Exercise'].unique()
        return muscle_exercises.tolist()[:5]  # Limit to 5 exercises
    
    def _get_opposite_muscle_groups(self, muscle_group: str) -> List[str]:
        """Get opposite muscle groups for balanced training"""
        opposites = {
            'Chest': ['Back', 'Legs'],
            'Back': ['Chest', 'Legs'],
            'Legs': ['Chest', 'Back', 'Shoulders'],
            'Shoulders': ['Legs', 'Back'],
            'Arms': ['Legs', 'Chest'],
            'Biceps': ['Triceps', 'Legs'],
            'Triceps': ['Biceps', 'Legs']
        }
        return opposites.get(muscle_group, [])
    
    def _generate_reasoning(self, model_type: str, recent_exercises: List[str], 
                          context_features: Dict = None) -> str:
        """Generate reasoning for recommendations"""
        reasoning_parts = []
        
        if model_type == "hybrid":
            reasoning_parts.append("Combines your exercise preferences with similar exercise characteristics")
            if context_features:
                recovery_status = context_features.get('recovery_status', 'ready')
                if recovery_status != 'ready':
                    reasoning_parts.append(f"Adjusted for recovery status: {recovery_status}")
                    
        elif model_type == "collaborative":
            reasoning_parts.append("Based on exercises you've done frequently")
            
        elif model_type == "content":
            reasoning_parts.append("Based on similarity to exercises you prefer")
            
        elif model_type == "sequence":
            reasoning_parts.append("Based on your workout patterns and sequences")
            
        if recent_exercises:
            reasoning_parts.append(f"Considering your recent exercises: {', '.join(recent_exercises[:3])}")
            
        return " | ".join(reasoning_parts)
    
    def get_model_performance(self, df: pd.DataFrame) -> Dict:
        """Get model performance metrics"""
        if not self.is_trained:
            return {"error": "Models not trained yet"}
            
        try:
            # Calculate basic metrics
            total_workouts = len(df)
            unique_exercises = df['Exercise'].nunique()
            muscle_groups = df['Muscle Group'].nunique()
            
            # Calculate prediction accuracy (simplified)
            accuracy = self._calculate_prediction_accuracy(df)
            
            return {
                "total_workouts": total_workouts,
                "unique_exercises": unique_exercises,
                "muscle_groups": muscle_groups,
                "prediction_accuracy": accuracy,
                "model_status": "Trained and Ready"
            }
            
        except Exception as e:
            return {"error": f"Error calculating performance: {str(e)}"}
    
    def _calculate_prediction_accuracy(self, df: pd.DataFrame) -> float:
        """Calculate prediction accuracy (simplified)"""
        # This is a simplified accuracy calculation
        # In a real implementation, you'd use proper train/test splits
        
        if len(df) < 10:
            return 0.0
            
        # Use last 20% of data for "testing"
        test_size = max(1, len(df) // 5)
        test_data = df.tail(test_size)
        
        correct_predictions = 0
        total_predictions = 0
        
        for i in range(len(test_data) - 1):
            # Get context up to this point
            historical_data = df.iloc[:len(df) - test_size + i]
            
            # Get actual next exercise
            actual_exercise = test_data.iloc[i + 1]['Exercise']
            
            # Get prediction
            recent_exercises = historical_data.tail(3)['Exercise'].tolist()
            context_features = self.feature_engineer.create_context_features()
            
            try:
                predictions = self.hybrid_model.recommend(recent_exercises, context_features, 5)
                
                if actual_exercise in predictions:
                    correct_predictions += 1
                total_predictions += 1
                
            except:
                continue
                
        return correct_predictions / max(total_predictions, 1)
