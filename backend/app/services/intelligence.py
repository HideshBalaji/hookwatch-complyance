import os
import pickle
import pandas as pd
from fastapi import HTTPException
import numpy as np

# Global models
XGB_MODEL = None
IF_MODEL = None
FEATURES_DF = None

def load_models_and_data():
    global XGB_MODEL, IF_MODEL, FEATURES_DF
    base_dir = os.path.dirname(__file__)
    
    xgb_path = os.path.join(base_dir, '../ml/models/xgb_model.pkl')
    if_path = os.path.join(base_dir, '../ml/models/if_model.pkl')
    features_path = os.path.join(base_dir, '../../datasets/processed/features.csv')

    try:
        with open(xgb_path, 'rb') as f:
            XGB_MODEL = pickle.load(f)
            
        with open(if_path, 'rb') as f:
            IF_MODEL = pickle.load(f)
            
        if os.path.exists(features_path):
            FEATURES_DF = pd.read_csv(features_path)
            FEATURES_DF.set_index('event_id', inplace=True)
            
            # Drop the same columns we dropped during training to match the model input shape
            drop_cols = ['event_type', 'endpoint_id', 'is_recovered', 
                         'total_attempts', 'timeout_count', 'server_error_count', 
                         'client_error_count', 'success_count', 'duplicate_count', 'replay_count']
            
            FEATURES_DF.drop(columns=drop_cols, inplace=True, errors='ignore')
            
            # Convert booleans to int just like in training
            for col in FEATURES_DF.select_dtypes(include=['bool']).columns:
                FEATURES_DF[col] = FEATURES_DF[col].astype(int)
    except Exception as e:
        print(f"Warning: Could not load ML models or features. Error: {e}")

# Pre-load into memory when service boots
load_models_and_data()

def get_event_intelligence(event_id: str):
    if FEATURES_DF is None or event_id not in FEATURES_DF.index:
        raise HTTPException(status_code=404, detail="Event features not found or ML models not loaded.")

    # 1. Extract feature row
    feature_row = FEATURES_DF.loc[[event_id]]

    # 2. ML Inference
    is_safe_to_replay_pred = XGB_MODEL.predict(feature_row)[0]
    anomaly_pred = IF_MODEL.predict(feature_row)[0] # -1 is anomaly, 1 is normal

    is_safe = bool(is_safe_to_replay_pred == 1)
    is_anomaly = bool(anomaly_pred == -1)

    # 3. Synthesize Rule-Based & ML Intelligence
    timeout_ratio = float(feature_row['timeout_ratio'].values[0])
    error_ratio = float(feature_row['error_ratio'].values[0])
    health = float(feature_row['endpoint_health_score'].values[0])
    
    # Determine probable failure reason based on ratios
    failure_reason = "unknown"
    if timeout_ratio > 0.0:
        failure_reason = "timeout"
    elif error_ratio > 0.0:
        failure_reason = "server_error"
    elif health < 0.7:
        failure_reason = "endpoint_offline"
        
    # Decision Engine for Recommendations
    recommended_action = "none"
    if is_anomaly:
        recommended_action = "block_source_anomaly_detected"
    elif is_safe:
        recommended_action = "trigger_auto_replay"
    elif health < 0.8:
        recommended_action = "monitor_endpoint_health"
    else:
        recommended_action = "manual_review_required"

    # Assume delivery state based on safety prediction
    delivery_state = "failed"
    if is_safe: 
        delivery_state = "recovered"
        
    return {
        "event_id": event_id,
        "delivery_state": delivery_state,
        "failure_reason": failure_reason,
        "safe_to_replay": is_safe,
        "is_anomaly": is_anomaly,
        "recommended_action": recommended_action,
        "metrics": {
            "endpoint_health": round(health, 2),
            "timeout_ratio": round(timeout_ratio, 2)
        }
    }
