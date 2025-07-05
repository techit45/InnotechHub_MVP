#!/usr/bin/env python3
"""
Database Migration Script: SQLite to PostgreSQL
Run this script to migrate your data from SQLite to PostgreSQL
"""

import os
import sys
import json
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.db_migration import DatabaseMigration

def main():
    print("🚀 Innotech Platform: Database Migration")
    print("=" * 50)
    
    # Database URLs
    sqlite_url = "sqlite:///./innotech_db.sqlite"
    postgres_url = "postgresql://innotech_user:secure_password_2024@localhost:5433/innotech_production"
    
    print(f"📁 Source (SQLite): {sqlite_url}")
    print(f"🐘 Target (PostgreSQL): {postgres_url}")
    print()
    
    # Auto-confirm migration for automation
    print("✅ Auto-confirming migration...")
    
    # Create migrator instance
    migrator = DatabaseMigration(sqlite_url, postgres_url)
    
    # Start migration
    success = migrator.migrate()
    
    if success:
        print()
        print("🎉 Migration completed successfully!")
        print()
        print("Next steps:")
        print("1. Update your .env file to use PostgreSQL URL")
        print("2. Test your application with PostgreSQL")
        print("3. Backup your SQLite file for safety")
        print()
        print("Production URL:")
        print("DATABASE_URL=postgresql://innotech_user:secure_password_2024@localhost:5433/innotech_production")
    else:
        print()
        print("❌ Migration failed!")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main()