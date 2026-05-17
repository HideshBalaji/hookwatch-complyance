import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.database.db import engine

class AnalyticsEngine:
    """
    STEP 3 - ANALYTICS ENGINE
    Uses Pandas and PostgreSQL to analyze retry counts, timeout patterns,
    failure rates, endpoint instability, and replay frequency.
    """
    
    @staticmethod
    def get_endpoint_instability():
        """
        Analyzes endpoint instability based on failure rates and timeouts.
        """
        query = """
            SELECT 
                endpoint_id,
                COUNT(attempt_id) AS total_attempts,
                SUM(CASE WHEN http_status >= 500 OR timeout = true THEN 1 ELSE 0 END) AS failure_count,
                SUM(CASE WHEN timeout = true THEN 1 ELSE 0 END) AS timeout_count,
                AVG(response_time_ms) AS avg_response_time
            FROM delivery_attempts
            GROUP BY endpoint_id
            HAVING COUNT(attempt_id) > 5
        """
        df = pd.read_sql(query, con=engine)
        
        # Calculate failure rate
        df['failure_rate'] = df['failure_count'] / df['total_attempts']
        df['timeout_rate'] = df['timeout_count'] / df['total_attempts']
        
        # Sort by most unstable
        return df.sort_values(by='failure_rate', ascending=False)

    @staticmethod
    def get_event_retry_patterns():
        """
        Analyzes the system's retry effectiveness.
        """
        query = """
            SELECT 
                attempt_number,
                COUNT(attempt_id) as count,
                AVG(response_time_ms) as avg_response_time,
                SUM(CASE WHEN http_status >= 200 AND http_status < 300 THEN 1 ELSE 0 END) * 100.0 / COUNT(attempt_id) as success_rate_percent
            FROM delivery_attempts
            GROUP BY attempt_number
            ORDER BY attempt_number
        """
        df = pd.read_sql(query, con=engine)
        return df

    @staticmethod
    def get_replay_frequency():
        """
        Analyzes the frequency and success of replay actions.
        """
        query = """
            SELECT 
                replay_result,
                COUNT(replay_id) as count,
                SUM(CASE WHEN duplicate_detected = true THEN 1 ELSE 0 END) as duplicates_detected
            FROM replay_actions
            GROUP BY replay_result
        """
        df = pd.read_sql(query, con=engine)
        return df

if __name__ == "__main__":
    print("--- Analytics Engine Output ---")
    
    print("\n1. Endpoint Instability (Top 5 Unstable Endpoints):")
    instability_df = AnalyticsEngine.get_endpoint_instability()
    print(instability_df.head(5))
    
    print("\n2. Retry Patterns (Success rate by attempt number):")
    retry_df = AnalyticsEngine.get_event_retry_patterns()
    print(retry_df)
    
    print("\n3. Replay Frequency:")
    replay_df = AnalyticsEngine.get_replay_frequency()
    print(replay_df)
