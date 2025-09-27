"""
Data processing utilities for the Gym Progress Tracker app.
"""

import pandas as pd
import re
import os
import streamlit as st
from config import REQUIRED_COLUMNS


@st.cache_data
def load_workout_data(csv_path, file_mtime):
    """Load and preprocess workout data from CSV"""
    try:
        try:
            df = pd.read_csv(csv_path)
        except pd.errors.ParserError:
            # Retry with permissive parser and skip malformed lines
            df = pd.read_csv(csv_path, engine='python', on_bad_lines='skip')
    except FileNotFoundError:
        st.error("workouts.csv file not found. Please ensure the file exists in the same directory.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error reading workouts.csv: {str(e)}")
        return pd.DataFrame()
    
    # Validate required columns
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        st.error(f"workouts.csv is missing required columns: {', '.join(missing_columns)}")
        return pd.DataFrame()
    
    # Convert date column
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Expand compound muscle groups into separate rows
    df = expand_compound_muscle_groups(df)
    
    # Add grouped muscle groups for analytics
    df = add_grouped_muscle_groups(df)
    
    # Parse sets x reps x weight data
    df['Parsed_Sets'] = df['Sets x Reps x Weight'].apply(parse_sets_reps_weight)
    
    # Calculate total volume (sets * reps * weight)
    df['Total_Volume'] = df['Parsed_Sets'].apply(calculate_total_volume)
    
    # Calculate average weight
    df['Avg_Weight'] = df['Parsed_Sets'].apply(calculate_avg_weight)
    
    # Calculate total reps
    df['Total_Reps'] = df['Parsed_Sets'].apply(calculate_total_reps)
    
    # Calculate estimated 1RM
    df['Estimated_1RM'] = df['Parsed_Sets'].apply(calculate_1rm)
    
    # Calculate max weight and reps
    df['Max_Weight'], df['Max_Reps'] = zip(*df['Parsed_Sets'].apply(get_max_weight_and_reps))
    
    return df


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


def calculate_1rm(sets_data):
    """Calculate estimated 1RM using Epley formula: 1RM = weight * (1 + reps / 30)"""
    if not sets_data:
        return 0
    
    max_1rm = 0
    for set_data in sets_data:
        if set_data['reps'] > 0 and set_data['weight'] > 0:
            # Epley formula: 1RM = weight * (1 + reps / 30)
            estimated_1rm = set_data['weight'] * (1 + set_data['reps'] / 30)
            max_1rm = max(max_1rm, estimated_1rm)
    return max_1rm


def get_max_weight_and_reps(sets_data):
    """Get the maximum weight lifted and corresponding reps"""
    if not sets_data:
        return 0, 0
    
    max_weight = 0
    max_reps_at_max_weight = 0
    
    for set_data in sets_data:
        if set_data['weight'] > max_weight:
            max_weight = set_data['weight']
            max_reps_at_max_weight = set_data['reps']
        elif set_data['weight'] == max_weight:
            max_reps_at_max_weight = max(max_reps_at_max_weight, set_data['reps'])
    
    return max_weight, max_reps_at_max_weight


def expand_compound_muscle_groups(df):
    """Expand compound muscle groups into separate rows for each muscle group"""
    expanded_rows = []
    
    for _, row in df.iterrows():
        muscle_group = row['Muscle Group']
        
        # Check if it's a compound muscle group (contains '/' or parentheses with '/')
        if '/' in muscle_group:
            # Handle parentheses case like "Posterior Chain (Glutes/Hamstrings/Back)"
            if '(' in muscle_group and ')' in muscle_group:
                # Extract the part inside parentheses
                start = muscle_group.find('(') + 1
                end = muscle_group.find(')')
                groups_part = muscle_group[start:end]
                individual_groups = [group.strip() for group in groups_part.split('/')]
            else:
                # Regular case like "Back/Biceps"
                individual_groups = [group.strip() for group in muscle_group.split('/')]
            
            # Create a separate row for each muscle group
            for group in individual_groups:
                new_row = row.copy()
                new_row['Muscle Group'] = group
                expanded_rows.append(new_row)
        else:
            # Single muscle group, keep as is
            expanded_rows.append(row)
    
    return pd.DataFrame(expanded_rows)


def add_grouped_muscle_groups(df):
    """Add grouped muscle group column for analytics"""
    from config import MUSCLE_GROUP_MAPPING
    
    df['Grouped_Muscle_Group'] = df['Muscle Group'].map(MUSCLE_GROUP_MAPPING)
    # Handle any unmapped groups
    df['Grouped_Muscle_Group'] = df['Grouped_Muscle_Group'].fillna(df['Muscle Group'])
    
    return df


def get_file_mtime(csv_path):
    """Get file modification time for cache invalidation"""
    try:
        return os.path.getmtime(csv_path)
    except FileNotFoundError:
        return 0
