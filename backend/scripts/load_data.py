import pandas as pd
import sys
import os
import uuid

# Add backend directory to sys path so we can import from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from app.database.db import engine

def load_data():
    dataset_dir = os.path.join(os.path.dirname(__file__), '../datasets')
    
    print("Loading endpoints...")
    endpoints_df = pd.read_csv(os.path.join(dataset_dir, 'endpoints.csv'))
    # Ensure pandas aligns the data and does not replace the table, just appends
    endpoints_df.to_sql('endpoints', con=engine, if_exists='append', index=False)
    print(f"Loaded {len(endpoints_df)} endpoints.")

    print("Loading webhook events...")
    events_df = pd.read_csv(os.path.join(dataset_dir, 'webhook_events.csv'))
    events_df.to_sql('webhook_events', con=engine, if_exists='append', index=False)
    print(f"Loaded {len(events_df)} webhook events.")

    print("Loading delivery attempts...")
    attempts_df = pd.read_csv(os.path.join(dataset_dir, 'delivery_attempts.csv'))
    attempts_df.to_sql('delivery_attempts', con=engine, if_exists='append', index=False)
    print(f"Loaded {len(attempts_df)} delivery attempts.")

    print("Loading replay actions...")
    replay_df = pd.read_csv(os.path.join(dataset_dir, 'replay_actions.csv'))
    # Generate UUIDs for replay_id since it's missing in the CSV
    replay_df['replay_id'] = [str(uuid.uuid4()) for _ in range(len(replay_df))]
    replay_df.to_sql('replay_actions', con=engine, if_exists='append', index=False)
    print(f"Loaded {len(replay_df)} replay actions.")

    print("Data ingestion complete!")

if __name__ == "__main__":
    load_data()
