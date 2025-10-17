#!/usr/bin/env python3
"""
Create a baseline database with schema and default settings.

This script should be run whenever the database schema changes
to create a fresh baseline database for new deployments.

Usage:
    python backend/create_baseline_db.py
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database
from database_models import Base, AppSettings
from timezone_utils import to_iso_string


def create_baseline_database():
    """Create a clean baseline database with schema and default settings."""
    baseline_path = os.path.join(os.path.dirname(__file__), 'pharma_exam_baseline.db')

    # Remove if exists
    if os.path.exists(baseline_path):
        print(f"Removing existing baseline database: {baseline_path}")
        os.remove(baseline_path)

    # Create new database with schema
    print(f"Creating baseline database: {baseline_path}")
    db = Database(db_path=baseline_path)

    # Create all tables
    Base.metadata.create_all(db.engine)
    print(f"✅ Created tables: {', '.join(Base.metadata.tables.keys())}")

    # Add default timezone setting
    with db.session() as session:
        timezone_setting = AppSettings(
            setting_key='timezone',
            setting_value='America/Puerto_Rico',
            updated_at=to_iso_string()
        )
        session.add(timezone_setting)
        session.commit()
        print(f"✅ Added default timezone: America/Puerto_Rico (AST)")

    print(f"\n✅ Baseline database created successfully!")
    print(f"   Location: {baseline_path}")
    print(f"\nNext steps:")
    print(f"  1. Verify the database: sqlite3 {baseline_path} '.tables'")
    print(f"  2. Commit to git: git add {baseline_path} && git commit")
    print(f"  3. Push to GitHub: git push origin main")


if __name__ == '__main__':
    create_baseline_database()
