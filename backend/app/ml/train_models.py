import pandas as pd
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.ensemble import IsolationForest
import xgboost as xgb

def train():
    print("--- STEP 5: REPLAY INTELLIGENCE ML ---")
    # 1. Load Data
    base_dir = os.path.dirname(__file__)
    data_path = os.path.abspath(os.path.join(base_dir, '../../datasets/processed/features.csv'))
    
    print(f"Loading engineered features from {data_path}...")
    df = pd.read_csv(data_path)

    # 2. Prepare features (X) and target (y)
    # Drop identifiers and variables that would cause data leakage (e.g., raw counts that deterministically reveal the target)
    leak_cols = [
        'total_attempts', 
        'timeout_count', 
        'server_error_count', 
        'client_error_count', 
        'success_count', 
        'duplicate_count', 
        'replay_count'
    ]
    drop_cols = ['event_id', 'event_type', 'endpoint_id', 'is_recovered'] + leak_cols
    
    X = df.drop(columns=drop_cols)
    y = df['is_recovered']

    # Convert booleans to int for XGBoost compatibility
    for col in X.select_dtypes(include=['bool']).columns:
        X[col] = X[col].astype(int)

    # Train/Test Split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print(f"Training features selected: {list(X.columns)}")
    print(f"Training Set Shape: {X_train.shape} | Test Set Shape: {X_test.shape}")

    # 3. Model 1: XGBoost (Predict Replay Safety / Recovery)
    print("\n[1/2] Training Model 1: XGBoost Classifier...")
    # Calculate scale_pos_weight for class imbalance
    # Note: Target is highly imbalanced (85% Class 1 vs 15% Class 0)
    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

    xgb_model = xgb.XGBClassifier(
        n_estimators=150,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        eval_metric='logloss',
        use_label_encoder=False
    )
    xgb_model.fit(X_train, y_train)

    y_pred = xgb_model.predict(X_test)
    print("\n>>> XGBoost Evaluation (Predicting if webhook can be recovered):")
    print(classification_report(y_test, y_pred))

    # 4. Model 2: Isolation Forest (Anomaly Detection)
    print("\n[2/2] Training Model 2: Isolation Forest...")
    # We estimate about 5% of webhooks are anomalous based on industry norms
    if_model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    if_model.fit(X_train)

    # Predict anomalies on test set (-1 is anomaly, 1 is normal)
    anomalies = if_model.predict(X_test)
    anomaly_count = (anomalies == -1).sum()
    print(f">>> Isolation Forest detected {anomaly_count} anomalous events out of {len(X_test)} in the test set ({(anomaly_count/len(X_test))*100:.2f}%).")

    # 5. Save Models
    models_dir = os.path.join(base_dir, 'models')
    os.makedirs(models_dir, exist_ok=True)

    xgb_path = os.path.join(models_dir, 'xgb_model.pkl')
    if_path = os.path.join(models_dir, 'if_model.pkl')

    with open(xgb_path, 'wb') as f:
        pickle.dump(xgb_model, f)
    with open(if_path, 'wb') as f:
        pickle.dump(if_model, f)

    print(f"\nTraining Complete! Models successfully serialized to:")
    print(f"- {xgb_path}")
    print(f"- {if_path}")

if __name__ == "__main__":
    train()
