import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.database.db import engine

def test_connection():
    try:
        with engine.connect() as connection:
            print("Successfully connected to the database!")
    except Exception as e:
        print(f"Failed to connect to the database: {e}")

if __name__ == "__main__":
    test_connection()
