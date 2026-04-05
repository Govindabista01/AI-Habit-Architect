import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os

class DataPreprocessor:
    def __init__(self, csv_path='ml_models/data/habit_architect_dataset.csv', dataframe=None):
        self.csv_path = csv_path
        self.dataframe = dataframe
        self.scaler = StandardScaler()
        self.feature_columns = [
            'habit_frequency_per_week',
            'streak_length',
            'completed_days_last_7',
            'missed_days_last_7',
            'completion_rate_last_30',
            'previous_day_completed',
            'motivation_score',
            'habit_difficulty',
            'is_weekend'
        ]
        self.categorical_columns = ['habit_category', 'day_of_week']
        self.target_column = 'habit_completed_today'
        self.all_categories = ['health', 'productivity', 'learning', 'mindfulness', 'social', 'finance', 'other']
        self.all_days = [0, 1, 2, 3, 4, 5, 6]  # Mon-Sun
    
    def load_data(self):
        """Load dataset from DataFrame or CSV"""
        print("=" * 60)
        print("LOADING DATASET")
        print("=" * 60)
        
        if self.dataframe is not None:
            df = self.dataframe.copy()
            print("Dataset loaded from provided DataFrame")
        else:
            if not os.path.exists(self.csv_path):
                print(f"ERROR: File not found at {self.csv_path}")
                return None
            df = pd.read_csv(self.csv_path)
            print("Dataset loaded from CSV")
            
        print(f"Dataset Shape: {df.shape[0]} rows × {df.shape[1]} columns")
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
        X_num = df[self.feature_columns].copy()
        X_cat = df[self.categorical_columns].copy()
        y = df[self.target_column].copy()
        
        # Handle missing values in numerical features
        X_num = X_num.fillna(X_num.mean())
        
        # One-hot encode categorical features
        X_cat_encoded = pd.get_dummies(X_cat, columns=self.categorical_columns)
        
        # Ensure all expected category columns are present
        for cat in self.all_categories:
            col_name = f"habit_category_{cat}"
            if col_name not in X_cat_encoded.columns:
                X_cat_encoded[col_name] = 0
        
        # Ensure all expected day columns are present
        for day in self.all_days:
            col_name = f"day_of_week_{day}"
            if col_name not in X_cat_encoded.columns:
                X_cat_encoded[col_name] = 0
                
        # Combine numerical and encoded categorical features
        X = pd.concat([X_num, X_cat_encoded], axis=1)
        
        # Ensure consistent column ordering (sorted)
        X = X.reindex(sorted(X.columns), axis=1)
        
        # Save the list of feature names for the predictor
        trained_dir = os.path.join(os.path.dirname(__file__), 'trained')
        os.makedirs(trained_dir, exist_ok=True)
        joblib.dump(list(X.columns), os.path.join(trained_dir, 'feature_names.pkl'))
        
        print(f"Features: {X.shape[1]} columns (including one-hot variants)")
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
        trained_dir = os.path.join(os.path.dirname(__file__), 'trained')
        os.makedirs(trained_dir, exist_ok=True)
        joblib.dump(self.scaler, os.path.join(trained_dir, 'scaler.pkl'))
        
        print(f"Features scaled and scaler saved to {trained_dir}/scaler.pkl")
        
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