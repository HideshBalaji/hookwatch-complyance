import sys
import os
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from app.database.db import engine, SessionLocal
import app.models.webhook as models

def migrate_db():
    print("Migrating Database to support multi-tenant Users...")
    
    # Create the users table using SQLAlchemy
    models.Base.metadata.create_all(bind=engine)
    
    # We must run raw SQL to ALTER existing tables because create_all doesn't add columns to existing tables
    alter_queries = [
        "ALTER TABLE webhook_events ADD COLUMN IF NOT EXISTS user_id VARCHAR REFERENCES users(user_id);",
        "ALTER TABLE endpoints ADD COLUMN IF NOT EXISTS user_id VARCHAR REFERENCES users(user_id);",
        "ALTER TABLE delivery_attempts ADD COLUMN IF NOT EXISTS user_id VARCHAR REFERENCES users(user_id);",
        "ALTER TABLE replay_actions ADD COLUMN IF NOT EXISTS user_id VARCHAR REFERENCES users(user_id);"
    ]
    
    with engine.connect() as conn:
        for q in alter_queries:
            conn.execute(text(q))
        conn.commit()
        print("Added user_id columns to all existing tables.")
        
    # Now create the dummy user
    db = SessionLocal()
    try:
        # Check if user1 exists
        user = db.query(models.User).filter(models.User.email == 'user1@hookwatch.com').first()
        if not user:
            user = models.User(
                user_id="user_1",
                name="Demo User",
                email="user1@hookwatch.com",
                password_hash="hashed_password_placeholder"
            )
            db.add(user)
            db.commit()
            print("Created dummy user: user_1")
        else:
            print("Dummy user already exists.")
            
        # Update existing records to belong to user_1
        update_queries = [
            "UPDATE webhook_events SET user_id = 'user_1' WHERE user_id IS NULL;",
            "UPDATE endpoints SET user_id = 'user_1' WHERE user_id IS NULL;",
            "UPDATE delivery_attempts SET user_id = 'user_1' WHERE user_id IS NULL;",
            "UPDATE replay_actions SET user_id = 'user_1' WHERE user_id IS NULL;"
        ]
        
        with engine.connect() as conn:
            for q in update_queries:
                conn.execute(text(q))
            conn.commit()
            print("Mapped all existing historical data to user_1.")
            
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        db.close()
        
    print("Migration Complete!")

if __name__ == "__main__":
    migrate_db()
