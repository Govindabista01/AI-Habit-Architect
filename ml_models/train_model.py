import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score
)
import joblib
import os
from preprocess_data import DataPreprocessor


class ModelTrainer:
    def __init__(self):
        self.model = None
        self.training_accuracy = None
        self.testing_accuracy = None

    def train(self, X_train, y_train):
        """Train Logistic Regression model"""
        print("\n" + "=" * 60)
        print("TRAINING LOGISTIC REGRESSION MODEL")
        print("=" * 60)

        self.model = LogisticRegression(
            random_state=42,
            max_iter=1000,
            solver='lbfgs',
            C=1.0,
            class_weight='balanced'
        )

        print("\n Training started...")
        self.model.fit(X_train, y_train)

        self.training_accuracy = self.model.score(X_train, y_train)
        print(f"Training complete")
        print(f"Training Accuracy: {self.training_accuracy*100:.2f}%")

        return self.model

    def evaluate(self, X_test, y_test):
        """Evaluate model performance"""
        print("\n" + "=" * 60)
        print("MODEL EVALUATION")
        print("=" * 60)

        # Predictions
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]

        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)

        try:
            roc_auc = roc_auc_score(y_test, y_pred_proba)
        except:
            roc_auc = 0.0

        self.testing_accuracy = accuracy

        # Display
        print(f"\n Performance Metrics:")
        print(f"  Accuracy:  {accuracy*100:.2f}%")
        print(f"  Precision: {precision*100:.2f}%")
        print(f"  Recall:    {recall*100:.2f}%")
        print(f"  F1-Score:  {f1*100:.2f}%")
        print(f"  ROC-AUC:   {roc_auc*100:.2f}%")

        print("\n Classification Report:")
        print(classification_report(y_test, y_pred,
                                    target_names=['Not Completed', 'Completed']))

        cm = confusion_matrix(y_test, y_pred)
        print("\n Confusion Matrix:")
        print(cm)
        print(f"\n  True Negatives:  {cm[0,0]}")
        print(f"  False Positives: {cm[0,1]}")
        print(f"  False Negatives: {cm[1,0]}")
        print(f"  True Positives:  {cm[1,1]}")

        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'roc_auc': roc_auc,
            'confusion_matrix': cm
        }

    def feature_importance(self, feature_names):
        """Show feature importance"""
        print("\n" + "=" * 60)
        print("FEATURE IMPORTANCE")
        print("=" * 60)

        coefficients = self.model.coef_[0]

        importance_df = pd.DataFrame({
            'Feature': feature_names,
            'Coefficient': coefficients,
            'Abs_Coefficient': np.abs(coefficients)
        }).sort_values('Abs_Coefficient', ascending=False)

        print("\n Feature Ranking:")
        print(importance_df.to_string(index=False))

        # THIS PART WAS MISSING/BROKEN IN YOUR CODE
        print("\n Interpretation:")
        print("  (+) Positive  → Increases completion probability")
        print("  (-) Negative  → Decreases completion probability")
        print("  Larger value  → More important feature")

        return importance_df

    def save_model(self):
        """Save trained model to disk"""
        print("\n" + "=" * 60)
        print("SAVING MODEL")
        print("=" * 60)

        # Create folder if it doesn't exist
        trained_dir = os.path.join(os.path.dirname(__file__), 'trained')
        os.makedirs(trained_dir, exist_ok=True)
 
        # Save the trained model
        model_path = os.path.join(trained_dir, 'habit_predictor.pkl')
        joblib.dump(self.model, model_path)
        print(f"Model saved to: {model_path}")

    def summary(self, results):
        """Print final summary report"""
        print("\n" + "=" * 60)
        print("FINAL SUMMARY REPORT")
        print("=" * 60)

        print(f"\n  Model Type:       Logistic Regression")
        print(f"  Training Acc:     {self.training_accuracy*100:.2f}%")
        print(f"  Testing Acc:      {self.testing_accuracy*100:.2f}%")
        print(f"  Precision:        {results['precision']*100:.2f}%")
        print(f"  Recall:           {results['recall']*100:.2f}%")
        print(f"  F1-Score:         {results['f1_score']*100:.2f}%")
        print(f"  ROC-AUC:          {results['roc_auc']*100:.2f}%")

        # Model quality check
        if self.testing_accuracy >= 0.85:
            print("\n Model Quality: EXCELLENT")
        elif self.testing_accuracy >= 0.75:
            print("\n Model Quality: GOOD")
        elif self.testing_accuracy >= 0.65:
            print("\n Model Quality: FAIR")
        else:
            print("\n Model Quality: NEEDS IMPROVEMENT")

        # Overfitting check
        diff = self.training_accuracy - self.testing_accuracy
        print(f"\n  Train-Test Difference: {diff*100:.2f}%")
        if diff > 0.10:
            print("WARNING: Model might be overfitting")
            print("Try increasing C value or collecting more data")
        else:
            print("No overfitting detected")

        print("\n" + "=" * 60)


# ─────────────────────────────────────────────
# MAIN: This runs when you execute the script
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print(" AI HABIT ARCHITECT - MODEL TRAINING")
    print("=" * 60)

    # Step 1: Preprocess data
    print("\n Step 1: Preprocessing data...")
    preprocessor = DataPreprocessor()
    data = preprocessor.run_pipeline()

    if data is None:
        print("Preprocessing failed. Check your CSV file.")
        exit()

    # Step 2: Train model
    print("\n Step 2: Training model...")
    trainer = ModelTrainer()
    trainer.train(data['X_train'], data['y_train'])

    # Step 3: Evaluate model
    print("\n Step 3: Evaluating model...")
    results = trainer.evaluate(data['X_test'], data['y_test'])

    # Step 4: Feature importance
    print("\n Step 4: Analyzing features...")
    trainer.feature_importance(data['feature_names'])

    # Step 5: Save model
    print("\n Step 5: Saving model...")
    trainer.save_model()

    # Step 6: Print summary
    print("\n Step 6: Final Summary")
    trainer.summary(results)

    print("\n TRAINING PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 60)