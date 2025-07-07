#!/usr/bin/env python3
"""
Simple startup script to test the authentication and database setup
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai_interviewer.database.base import engine, Base
from ai_interviewer.auth.models import User
from ai_interviewer.config import settings

def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False

def test_database_connection():
    """Test database connection."""
    print("Testing database connection...")
    try:
        from ai_interviewer.database.session import create_db_session
        
        db = create_db_session()
        
        # Try a simple query
        users_count = db.query(User).count()
        print(f"✅ Database connection successful! Found {users_count} users in database.")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Main function to test the setup."""
    print("🚀 AI Interviewer - Authentication & Database Setup Test")
    print("=" * 60)
    
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"Debug Mode: {settings.DEBUG}")
    print("-" * 60)
    
    # Test database setup
    db_setup_ok = create_tables()
    if not db_setup_ok:
        print("❌ Database setup failed. Exiting.")
        sys.exit(1)
    
    # Test database connection
    db_connection_ok = test_database_connection()
    if not db_connection_ok:
        print("❌ Database connection failed. Exiting.")
        sys.exit(1)
    
    print("-" * 60)
    print("✅ All tests passed! Authentication and database setup is working.")
    print("\nYou can now:")
    print("1. Run the FastAPI server: uvicorn ai_interviewer.main:app --reload")
    print("2. Run tests: pytest")
    print("3. Generate database migrations: alembic revision --autogenerate -m 'Initial migration'")
    print("4. Run migrations: alembic upgrade head")

if __name__ == "__main__":
    main()
