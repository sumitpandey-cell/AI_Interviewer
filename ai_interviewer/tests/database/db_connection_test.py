#!/usr/bin/env python3
"""
Simple database connection test for AI Interviewer
"""

import os
import sys
from pathlib import Path

# Set the working directory and Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Change to project directory so relative paths work
os.chdir(project_root)

def test_config():
    """Test configuration loading."""
    print("🔧 Testing configuration...")
    try:
        from ...src.ai_interviewer.config import settings
        print(f"✅ Config loaded successfully")
        print(f"📍 Database URL: {settings.DATABASE_URL}")
        print(f"🔐 Debug mode: {settings.DEBUG}")
        return True
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False

def test_database_engine():
    """Test database engine creation and connection."""
    print("\n🗄️  Testing database engine...")
    try:
        from ...src.ai_interviewer.database import engine
        from sqlalchemy import text
        
        print(f"✅ Engine created successfully")
        print(f"🔧 Engine dialect: {engine.dialect.name}")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("✅ Database connection successful!")
                return True
            else:
                print("❌ Connection test failed")
                return False
                
    except Exception as e:
        print(f"❌ Database engine test failed: {e}")
        return False

def test_session():
    """Test database session."""
    print("\n🔗 Testing database session...")
    try:
        from ai_interviewer.database.session import create_db_session
        from sqlalchemy import text
        
        db = create_db_session()
        try:
            result = db.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("✅ Database session test successful!")
                return True
            else:
                print("❌ Session test failed")
                return False
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Database session test failed: {e}")
        return False

def check_database_file():
    """Check if database file exists and show info."""
    print("\n📁 Checking database file...")
    try:
        from ai_interviewer.config import settings
        
        db_url = settings.DATABASE_URL
        if "sqlite:///" in db_url:
            # Extract file path
            db_file = db_url.replace("sqlite:///", "")
            if db_file.startswith("./"):
                db_file = db_file[2:]
            
            db_path = Path(db_file)
            if db_path.exists():
                size = db_path.stat().st_size
                print(f"✅ Database file exists: {db_path}")
                print(f"📊 File size: {size} bytes")
                return True
            else:
                print(f"⚠️  Database file does not exist: {db_path}")
                print("ℹ️  This is normal for a new installation")
                return True
        else:
            print(f"ℹ️  Using non-SQLite database: {db_url}")
            return True
            
    except Exception as e:
        print(f"❌ Database file check failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 AI Interviewer Database Connection Test")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_config),
        ("Database Engine", test_database_engine),
        ("Database Session", test_session),
        ("Database File", check_database_file),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All database tests passed! Your database connection is working.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
