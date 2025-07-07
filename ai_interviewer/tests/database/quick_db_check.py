#!/usr/bin/env python3
"""
One-line database connection test
Usage: python quick_db_check.py
"""

import sys
import os
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))
os.chdir(project_root)

try:
    from ai_interviewer.database.base import engine
    from sqlalchemy import text
    
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("✅ Database connection OK")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    sys.exit(1)
