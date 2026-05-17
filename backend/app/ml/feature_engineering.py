import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.database.db import engine

def extract_event_features():
    """
    STEP 4 - FEATURE ENGINEERING
    Extracts raw data from PostgreSQL and converts it into ML-ready features
    for each webhook event.
    """
    print("Extracting raw delivery logs from PostgreSQL...")
    
    # 1. Event & Endpoint Data
    events_query = """
        SELECT 
            e.event_id,
            e.event_type,
            e.priority,
            e.payload_size_kb,
            ep.endpoint_id,
            ep.avg_success_rate AS endpoint_health_score,
            ep.rate_limit_per_minute
        FROM webhook_events e
        LEFT JOIN delivery_attempts da ON e.event_id = da.event_id
        LEFT JOIN endpoints ep ON da.endpoint_id = ep.endpoint_id
        GROUP BY e.event_id, e.event_type, e.priority, e.payload_size_kb, ep.endpoint_id, ep.avg_success_rate, ep.rate_limit_per_minute
    """
    events_df = pd.read_sql(events_query, con=engine)

    # 2. Delivery Attempts Analytics
    attempts_query = """
        SELECT 
            event_id,
            COUNT(attempt_id) AS total_attempts,
            SUM(CASE WHEN timeout = true THEN 1 ELSE 0 END) AS timeout_count,
            SUM(CASE WHEN http_status >= 500 THEN 1 ELSE 0 END) AS server_error_count,
            SUM(CASE WHEN http_status >= 400 AND http_status < 500 THEN 1 ELSE 0 END) AS client_error_count,
            SUM(CASE WHEN http_status >= 200 AND http_status < 300 THEN 1 ELSE 0 END) AS success_count,
            AVG(response_time_ms) AS avg_response_time,
            MAX(response_time_ms) AS max_response_time
        FROM delivery_attempts
        GROUP BY event_id
    """
    attempts_df = pd.read_sql(attempts_query, con=engine)

    # 3. Replay Actions Analytics
    replay_query = """
        SELECT
            event_id,
            COUNT(replay_id) AS replay_count,
            SUM(CASE WHEN duplicate_detected = true THEN 1 ELSE 0 END) AS duplicate_count
        FROM replay_actions
        GROUP BY event_id
    """
    replay_df = pd.read_sql(replay_query, con=engine)

    print("Merging features and performing Feature Engineering...")

    # Merge DataFrames
    features_df = events_df.merge(attempts_df, on='event_id', how='left')
    features_df = features_df.merge(replay_df, on='event_id', how='left')

    # FEATURE ENGINEERING LOGIC
    features_df['replay_count'] = features_df['replay_count'].fillna(0)
    features_df['duplicate_count'] = features_df['duplicate_count'].fillna(0)
    
    # Calculate Retry Count
    features_df['retry_count'] = features_df['total_attempts'] - 1
    features_df['retry_count'] = features_df['retry_count'].clip(lower=0)
    
    # Calculate Ratios
    features_df['timeout_ratio'] = features_df['timeout_count'] / features_df['total_attempts']
    features_df['error_ratio'] = (features_df['server_error_count'] + features_df['client_error_count']) / features_df['total_attempts']
    
    # Target Variable: Was the event ultimately recovered/successful?
    features_df['is_recovered'] = (features_df['success_count'] > 0).astype(int)

    # Fill NaNs for missing metrics
    features_df['avg_response_time'] = features_df['avg_response_time'].fillna(0)
    features_df['max_response_time'] = features_df['max_response_time'].fillna(0)
    features_df['timeout_ratio'] = features_df['timeout_ratio'].fillna(0)
    features_df['error_ratio'] = features_df['error_ratio'].fillna(0)

    # One-hot encode categorical variables (priority, event_type)
    features_df = pd.get_dummies(features_df, columns=['priority'], dummy_na=False)

    return features_df

def verify_feature_quality(df):
    print("\n--- Feature Quality Verification ---")
    
    # 1. Null values check
    null_counts = df.isnull().sum()
    print("\n1. Null Values Count:")
    print(null_counts[null_counts > 0] if null_counts.sum() > 0 else "No null values found.")

    # 2. Class Imbalance
    print("\n2. Class Imbalance (is_recovered):")
    class_counts = df['is_recovered'].value_counts(normalize=True) * 100
    for idx, percentage in class_counts.items():
        print(f"Class {idx}: {percentage:.2f}%")

    # 3. Feature Distributions (selected key metrics)
    print("\n3. Feature Distributions:")
    cols_to_check = ['retry_count', 'timeout_ratio', 'avg_response_time', 'endpoint_health_score']
    print(df[cols_to_check].describe().T)


if __name__ == "__main__":
    df = extract_event_features()
    print(f"Generated ML Features for {len(df)} webhook events.")
    
    # Save the features to CSV
    processed_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../datasets/processed'))
    os.makedirs(processed_dir, exist_ok=True)
    
    csv_path = os.path.join(processed_dir, 'features.csv')
    df.to_csv(csv_path, index=False)
    print(f"Engineered features saved to {csv_path}")

    # Verify quality
    verify_feature_quality(df)
