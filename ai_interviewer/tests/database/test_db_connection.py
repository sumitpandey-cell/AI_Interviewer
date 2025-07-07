#!/usr/bin/env python3
"""
Database connection test script
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from ai_interviewer.database.base import engine, SessionLocal
from ai_interviewer.database.session import create_db_session
from ai_interviewer.config import settings


def test_engine_connection():
    """Test database connection using engine directly."""
    print("🔍 Testing database engine connection...")
    print(f"📍 Database URL: {settings.DATABASE_URL}")
    
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("✅ Engine connection successful!")
                return True
            else:
                print("❌ Engine connection failed - unexpected result")
                return False
    except SQLAlchemyError as e:
        print(f"❌ Engine connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_session_connection():
    """Test database connection using session."""
    print("\n🔍 Testing database session connection...")
    
    try:
        db = create_db_session()
        try:
            # Execute a simple query
            result = db.execute(text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("✅ Session connection successful!")
                return True
            else:
                print("❌ Session connection failed - unexpected result")
                return False
        finally:
            db.close()
    except SQLAlchemyError as e:
        print(f"❌ Session connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_database_info():
    """Get database information."""
    print("\n📊 Getting database information...")
    
    try:
        with engine.connect() as connection:
            # Check database type
            db_url = str(engine.url)
            print(f"🗄️  Database type: {engine.dialect.name}")
            print(f"🔗 Connection URL: {db_url}")
            
            # For SQLite, check if file exists
            if "sqlite" in db_url:
                db_file = db_url.replace("sqlite:///", "").replace("./", "")
                if os.path.exists(db_file):
                    size = os.path.getsize(db_file)
                    print(f"📁 Database file: {db_file} ({size} bytes)")
                else:
                    print(f"⚠️  Database file not found: {db_file}")
            
            # Try to get table information
            try:
                result = connection.execute(text(
                    "SELECT name FROM sqlite_master WHERE type='table'" 
                    if "sqlite" in db_url 
                    else "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
                ))
                tables = [row[0] for row in result.fetchall()]
                if tables:
                    print(f"📋 Tables found: {', '.join(tables)}")
                else:
                    print("📋 No tables found")
            except Exception as e:
                print(f"⚠️  Could not retrieve table information: {e}")
                
        return True
    except Exception as e:
        print(f"❌ Could not get database info: {e}")
        return False


def test_dependency_injection():
    """Test the FastAPI dependency injection pattern."""
    print("\n🔍 Testing dependency injection pattern...")
    
    try:
        from ai_interviewer.database.session import get_db
        
        # Get the generator
        db_generator = get_db()
        
        # Get the session
        db = next(db_generator)
        
        try:
            # Test the session
            result = db.execute(text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("✅ Dependency injection pattern works!")
                return True
            else:
                print("❌ Dependency injection test failed")
                return False
        finally:
            # Close the generator
            try:
                next(db_generator)
            except StopIteration:
                pass  # This is expected
                
    except Exception as e:
        print(f"❌ Dependency injection test failed: {e}")
        return False


def main():
    """Run all database connection tests."""
    print("🚀 AI Interviewer Database Connection Test")
    print("=" * 50)
    
    tests = [
        test_engine_connection,
        test_session_connection,
        test_database_info,
        test_dependency_injection
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All database connection tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check your database configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
