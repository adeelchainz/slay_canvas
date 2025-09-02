"""
Simple database setup script
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database():
    """Create PostgreSQL database"""
    try:
        # Connect to PostgreSQL server (default postgres database)
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="090078601",
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'mediaboard_ai'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("CREATE DATABASE mediaboard_ai")
            print("✅ Database 'mediaboard_ai' created successfully!")
        else:
            print("✅ Database 'mediaboard_ai' already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        print("Make sure PostgreSQL is running and the credentials are correct")
        return False

if __name__ == "__main__":
    create_database()
