"""
Machine Learning Models for Workout Recommendations
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')


class CollaborativeFilteringModel:
    """Collaborative filtering for exercise recommendations"""
    
    def __init__(self, n_neighbors: int = 5):
        self.n_neighbors = n_neighbors
        self.model = None
        self.exercise_encoder = LabelEncoder()
        self.user_features = None
        
    def fit(self, df: pd.DataFrame, user_features: Dict):
        """Fit the collaborative filtering model"""
        self.user_features = user_features
        
        # Create user-exercise interaction matrix
        exercise_counts = df['Exercise'].value_counts()
        top_exercises = exercise_counts.head(20).index.tolist()
        
        # Filter data to top exercises
        df_filtered = df[df['Exercise'].isin(top_exercises)]
        
        # Create user profile based on exercise preferences
        user_profile = self._create_user_profile(df_filtered)
        
        # Create exercise similarity matrix
        exercise_similarity = self._create_exercise_similarity(df_filtered)
        
        self.exercise_encoder.fit(top_exercises)
        self.exercise_similarity = exercise_similarity
        self.top_exercises = top_exercises
        
    def _create_user_profile(self, df: pd.DataFrame) -> Dict:
        """Create user profile based on exercise history"""
        profile = {}
        
        # Exercise frequency
        exercise_counts = df['Exercise'].value_counts()
        total_workouts = len(df)
        
        for exercise in exercise_counts.index:
            profile[exercise] = exercise_counts[exercise] / total_workouts
            
        return profile
    
    def _create_exercise_similarity(self, df: pd.DataFrame) -> np.ndarray:
        """Create exercise similarity matrix based on co-occurrence"""
        exercises = df['Exercise'].unique()
        n_exercises = len(exercises)
        similarity_matrix = np.zeros((n_exercises, n_exercises))
        
        # Calculate co-occurrence based on muscle groups and workout sessions
        for i, ex1 in enumerate(exercises):
            for j, ex2 in enumerate(exercises):
                if i == j:
                    similarity_matrix[i][j] = 1.0
                else:
                    # Find workouts where both exercises appear
                    ex1_workouts = set(df[df['Exercise'] == ex1]['Date'].dt.date)
                    ex2_workouts = set(df[df['Exercise'] == ex2]['Date'].dt.date)
                    
                    # Calculate Jaccard similarity
                    intersection = len(ex1_workouts & ex2_workouts)
                    union = len(ex1_workouts | ex2_workouts)
                    
                    similarity_matrix[i][j] = intersection / max(union, 1)
                    
        return similarity_matrix
    
    def recommend(self, recent_exercises: List[str], n_recommendations: int = 5) -> List[str]:
        """Recommend exercises based on collaborative filtering"""
        if not recent_exercises:
            return self.top_exercises[:n_recommendations]
            
        recommendations = []
        exercise_scores = {}
        
        for exercise in self.top_exercises:
            if exercise not in recent_exercises:
                # Calculate similarity score
                score = 0
                for recent_ex in recent_exercises:
                    if recent_ex in self.top_exercises:
                        idx1 = self.top_exercises.index(exercise)
                        idx2 = self.top_exercises.index(recent_ex)
                        score += self.exercise_similarity[idx1][idx2]
                        
                exercise_scores[exercise] = score / len(recent_exercises)
                
        # Sort by score and return top recommendations
        sorted_exercises = sorted(exercise_scores.items(), key=lambda x: x[1], reverse=True)
        recommendations = [ex[0] for ex in sorted_exercises[:n_recommendations]]
        
        return recommendations


class ContentBasedModel:
    """Content-based filtering for exercise recommendations"""
    
    def __init__(self):
        self.exercise_features = None
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=10)
        
    def fit(self, df: pd.DataFrame, exercise_embeddings: Dict):
        """Fit the content-based model"""
        self.exercise_features = exercise_embeddings
        
        # Create feature matrix
        exercises = list(exercise_embeddings.keys())
        feature_matrix = np.array([exercise_embeddings[ex] for ex in exercises])
        
        # Scale and reduce dimensionality
        feature_matrix_scaled = self.scaler.fit_transform(feature_matrix)
        feature_matrix_pca = self.pca.fit_transform(feature_matrix_scaled)
        
        # Store processed features
        self.processed_features = dict(zip(exercises, feature_matrix_pca))
        
    def recommend(self, preferred_exercises: List[str], n_recommendations: int = 5) -> List[str]:
        """Recommend exercises based on content similarity"""
        if not preferred_exercises:
            return list(self.processed_features.keys())[:n_recommendations]
            
        # Calculate average preference vector
        preference_vector = np.mean([self.processed_features[ex] for ex in preferred_exercises 
                                   if ex in self.processed_features], axis=0)
        
        # Calculate similarity scores
        similarities = {}
        for exercise, features in self.processed_features.items():
            if exercise not in preferred_exercises:
                similarity = cosine_similarity([preference_vector], [features])[0][0]
                similarities[exercise] = similarity
                
        # Return top recommendations
        sorted_exercises = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        return [ex[0] for ex in sorted_exercises[:n_recommendations]]


class HybridRecommendationModel:
    """Hybrid model combining collaborative filtering and content-based filtering"""
    
    def __init__(self, collaborative_weight: float = 0.6, content_weight: float = 0.4):
        self.collaborative_weight = collaborative_weight
        self.content_weight = content_weight
        self.collaborative_model = CollaborativeFilteringModel()
        self.content_model = ContentBasedModel()
        self.context_model = None
        
    def fit(self, df: pd.DataFrame, user_features: Dict, exercise_embeddings: Dict):
        """Fit all models"""
        self.collaborative_model.fit(df, user_features)
        self.content_model.fit(df, exercise_embeddings)
        
        # Train context-aware model
        self._train_context_model(df, user_features)
        
    def _train_context_model(self, df: pd.DataFrame, user_features: Dict):
        """Train context-aware recommendation model"""
        # Create training data
        X, y = self._create_training_data(df)
        
        if len(X) > 0:
            # Train Random Forest for context-aware recommendations
            self.context_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.context_model.fit(X, y)
            
    def _create_training_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Create training data for context model"""
        X, y = [], []
        
        # Create features for each workout
        for i in range(1, len(df)):
            # Context features (before the workout)
            context_features = self._extract_context_features(df.iloc[:i])
            
            # Target (the actual workout)
            target_exercise = df.iloc[i]['Exercise']
            
            X.append(context_features)
            y.append(target_exercise)
            
        return np.array(X), np.array(y)
    
    def _extract_context_features(self, historical_data: pd.DataFrame) -> np.ndarray:
        """Extract context features from historical data"""
        features = []
        
        if len(historical_data) == 0:
            return np.zeros(20)  # Default feature vector
            
        # Recent workout features
        recent_data = historical_data.tail(3)
        
        # Days since last workout
        if len(historical_data) > 1:
            last_date = historical_data.iloc[-1]['Date']
            days_since = (historical_data.iloc[-1]['Date'] - historical_data.iloc[-2]['Date']).days
        else:
            days_since = 0
            
        features.append(days_since)
        
        # Recent muscle group frequency
        muscle_groups = ['Back', 'Chest', 'Shoulders', 'Arms', 'Legs', 'Recovery']
        for muscle in muscle_groups:
            count = len(recent_data[recent_data['Muscle Group'] == muscle])
            features.append(count)
            
        # Recent RPE patterns
        features.append(recent_data['RPE'].mean() if len(recent_data) > 0 else 0)
        features.append(recent_data['RPE'].std() if len(recent_data) > 0 else 0)
        
        # Volume patterns
        features.append(recent_data['Total_Volume'].mean() if len(recent_data) > 0 else 0)
        features.append(recent_data['Total_Volume'].std() if len(recent_data) > 0 else 0)
        
        # Exercise variety
        features.append(len(recent_data['Exercise'].unique()))
        
        # Fill remaining features with zeros
        while len(features) < 20:
            features.append(0)
            
        return np.array(features[:20])
    
    def recommend(self, recent_exercises: List[str], context_features: Dict, 
                 n_recommendations: int = 5) -> List[str]:
        """Generate hybrid recommendations"""
        # Get collaborative filtering recommendations
        collab_recs = self.collaborative_model.recommend(recent_exercises, n_recommendations * 2)
        
        # Get content-based recommendations
        content_recs = self.content_model.recommend(recent_exercises, n_recommendations * 2)
        
        # Combine recommendations with weights
        combined_scores = {}
        
        for i, exercise in enumerate(collab_recs):
            score = self.collaborative_weight * (1 - i / len(collab_recs))
            combined_scores[exercise] = combined_scores.get(exercise, 0) + score
            
        for i, exercise in enumerate(content_recs):
            score = self.content_weight * (1 - i / len(content_recs))
            combined_scores[exercise] = combined_scores.get(exercise, 0) + score
            
        # Apply context-based adjustments
        context_adjustments = self._get_context_adjustments(context_features)
        for exercise in combined_scores:
            combined_scores[exercise] *= context_adjustments.get(exercise, 1.0)
            
        # Return top recommendations
        sorted_exercises = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        return [ex[0] for ex in sorted_exercises[:n_recommendations]]
    
    def _get_context_adjustments(self, context_features: Dict) -> Dict:
        """Get context-based adjustments for recommendations"""
        adjustments = {}
        
        # Recovery status adjustments
        recovery_status = context_features.get('recovery_status', 'ready')
        
        if recovery_status == 'needs_rest':
            # Favor lighter exercises
            light_exercises = ['Calf Raises', 'Lateral Raises', 'Facepulls']
            for exercise in light_exercises:
                adjustments[exercise] = 1.5
        elif recovery_status == 'light_workout':
            # Favor moderate exercises
            moderate_exercises = ['Arnold Press', 'Cable Rows', 'Leg Press']
            for exercise in moderate_exercises:
                adjustments[exercise] = 1.3
                
        # Muscle group balance adjustments
        last_muscle_group = context_features.get('last_workout_muscle_group')
        if last_muscle_group:
            # Favor different muscle groups
            opposite_groups = {
                'Chest': ['Back', 'Legs'],
                'Back': ['Chest', 'Legs'],
                'Legs': ['Chest', 'Back'],
                'Shoulders': ['Legs', 'Back'],
                'Arms': ['Legs', 'Chest']
            }
            
            if last_muscle_group in opposite_groups:
                for group in opposite_groups[last_muscle_group]:
                    # This would need exercise-to-muscle-group mapping
                    pass
                    
        return adjustments


class WorkoutSequenceModel:
    """Sequence-based model for workout recommendations"""
    
    def __init__(self, sequence_length: int = 5):
        self.sequence_length = sequence_length
        self.sequences = []
        self.transition_matrix = None
        
    def fit(self, df: pd.DataFrame):
        """Fit the sequence model"""
        # Create workout sequences
        sequences = self._create_sequences(df)
        
        # Build transition matrix
        self._build_transition_matrix(sequences)
        
    def _create_sequences(self, df: pd.DataFrame) -> List[List[str]]:
        """Create workout sequences from data"""
        sequences = []
        df_sorted = df.sort_values('Date')
        
        # Group by date to get daily workout sequences
        daily_workouts = df_sorted.groupby('Date')['Exercise'].apply(list).tolist()
        
        # Create sequences of daily workouts
        for i in range(len(daily_workouts) - self.sequence_length + 1):
            sequence = daily_workouts[i:i+self.sequence_length]
            sequences.append(sequence)
            
        return sequences
    
    def _build_transition_matrix(self, sequences: List[List[str]]):
        """Build transition matrix for sequence predictions"""
        # Get all unique exercises
        all_exercises = set()
        for sequence in sequences:
            for day_workouts in sequence:
                all_exercises.update(day_workouts)
                
        self.exercises = list(all_exercises)
        n_exercises = len(self.exercises)
        
        # Initialize transition matrix
        self.transition_matrix = np.zeros((n_exercises, n_exercises))
        
        # Count transitions
        for sequence in sequences:
            for day_workouts in sequence:
                for exercise in day_workouts:
                    if exercise in self.exercises:
                        exercise_idx = self.exercises.index(exercise)
                        self.transition_matrix[exercise_idx][exercise_idx] += 1
                        
        # Normalize to probabilities
        row_sums = self.transition_matrix.sum(axis=1)
        self.transition_matrix = self.transition_matrix / (row_sums[:, np.newaxis] + 1e-8)
        
    def recommend_next(self, current_sequence: List[str], n_recommendations: int = 5) -> List[str]:
        """Recommend next exercises based on sequence"""
        if not current_sequence:
            return self.exercises[:n_recommendations]
            
        # Calculate probabilities for next exercises
        probabilities = {}
        
        for exercise in self.exercises:
            if exercise not in current_sequence:
                # Calculate probability based on sequence context
                prob = 0
                for seq_exercise in current_sequence:
                    if seq_exercise in self.exercises:
                        seq_idx = self.exercises.index(seq_exercise)
                        ex_idx = self.exercises.index(exercise)
                        prob += self.transition_matrix[seq_idx][ex_idx]
                        
                probabilities[exercise] = prob / len(current_sequence)
                
        # Return top recommendations
        sorted_exercises = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
        return [ex[0] for ex in sorted_exercises[:n_recommendations]]
