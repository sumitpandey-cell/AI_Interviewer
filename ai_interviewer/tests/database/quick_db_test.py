#!/usr/bin/env python3
"""
Quick database connection check
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from ai_interviewer.database import engine
    from ai_interviewer.config import settings
    from sqlalchemy import text
    
    print(f"Database URL: {settings.DATABASE_URL}")
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
        
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    sys.exit(1)
