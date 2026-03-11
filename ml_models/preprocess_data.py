import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os

class DataPreprocessor:
    def __init__(self, csv_path='ml_models/data/habit_architect_dataset.csv'):
        self.csv_path = csv_path
        self.scaler = StandardScaler()
        self.feature_columns = [
            'habit_frequency_per_week',
            'streak_length',
            'completed_days_last_7',
            'missed_days_last_7',
            'completion_rate_last_30',
            'previous_day_completed',
            'motivation_score',
            'habit_difficulty'
        ]
        self.target_column = 'habit_completed_today'
    
    def load_data(self):
        """Load CSV dataset"""
        print("=" * 60)
        print("LOADING DATASET")
        print("=" * 60)
        
        if not os.path.exists(self.csv_path):
            print(f"ERROR: File not found at {self.csv_path}")
            return None
        
        df = pd.read_csv(self.csv_path)
        print(f"Dataset loaded: {df.shape[0]} rows × {df.shape[1]} columns")
        return df
    
    def explore_data(self, df):
        """Display data information"""
        print("\n" + "=" * 60)
        print("DATA EXPLORATION")
        print("=" * 60)
        
        print("\n Dataset Shape:", df.shape)
        print("\n Columns:")
        for col in df.columns:
            print(f"  - {col}")
        
        print("\n First 5 Rows:")
        print(df.head())
        
        print("\n Statistical Summary:")
        print(df[self.feature_columns].describe())
        
        print("\n Missing Values:")
        missing = df.isnull().sum()
        if missing.sum() == 0:
            print("  No missing values")
        else:
            print(missing[missing > 0])
        
        print("\n Target Distribution:")
        target_dist = df[self.target_column].value_counts()
        print(target_dist)
        print(f"  Completion Rate: {df[self.target_column].mean()*100:.2f}%")
        
        return df
    
    def prepare_features(self, df):
        """Extract features and target"""
        print("\n" + "=" * 60)
        print("PREPARING FEATURES")
        print("=" * 60)
        
        # Check columns exist
        missing_cols = [col for col in self.feature_columns if col not in df.columns]
        if missing_cols:
            print(f"Missing columns: {missing_cols}")
            return None, None
        
        if self.target_column not in df.columns:
            print(f"Target column '{self.target_column}' not found")
            return None, None
        
        # Extract features and target
        X = df[self.feature_columns].copy()
        y = df[self.target_column].copy()
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        print(f"Features: {X.shape[1]} columns")
        print(f"Samples: {X.shape[0]} rows")
        print(f"Target variable prepared")
        
        return X, y
    
    def split_data(self, X, y, test_size=0.2, random_state=42):
        """Split into train and test sets"""
        print("\n" + "=" * 60)
        print("SPLITTING DATA")
        print("=" * 60)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state,
            stratify=y
        )
        
        print(f"Training set: {X_train.shape[0]} samples ({(1-test_size)*100}%)")
        print(f"Testing set: {X_test.shape[0]} samples ({test_size*100}%)")
        
        return X_train, X_test, y_train, y_test
    
    def scale_features(self, X_train, X_test):
        """Normalize features"""
        print("\n" + "=" * 60)
        print("SCALING FEATURES")
        print("=" * 60)
        
        # Fit on training data
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Save scaler
        os.makedirs('ml_models/trained', exist_ok=True)
        joblib.dump(self.scaler, 'ml_models/trained/scaler.pkl')
        
        print("Features scaled using StandardScaler")
        print("Scaler saved to ml_models/trained/scaler.pkl")
        
        return X_train_scaled, X_test_scaled
    
    def run_pipeline(self):
        """Complete preprocessing pipeline"""
        print("\n" + "=" * 60)
        print("STARTING PREPROCESSING PIPELINE")
        print("=" * 60)
        
        # Load
        df = self.load_data()
        if df is None:
            return None
        
        # Explore
        df = self.explore_data(df)
        
        # Prepare
        X, y = self.prepare_features(df)
        if X is None:
            return None
        
        # Split
        X_train, X_test, y_train, y_test = self.split_data(X, y)
        
        # Scale
        X_train_scaled, X_test_scaled = self.scale_features(X_train, X_test)
        
        print("\n" + "=" * 60)
        print("PREPROCESSING COMPLETE")
        print("=" * 60)
        
        return {
            'X_train': X_train_scaled,
            'X_test': X_test_scaled,
            'y_train': y_train,
            'y_test': y_test,
            'feature_names': self.feature_columns
        }

# Run independently
if __name__ == "__main__":
    preprocessor = DataPreprocessor()
    data = preprocessor.run_pipeline()
    
    if data:
        print("\n Ready for model training!")