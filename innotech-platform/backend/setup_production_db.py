#!/usr/bin/env python3
"""
Setup production database tables on AWS RDS
"""
import os
import psycopg2
from sqlalchemy import create_engine, text
from app.models.user import User
from app.models.course import Course  
from app.models.assignment import Assignment
from app.database import Base

def setup_production_database():
    """Setup all tables in production PostgreSQL database"""
    
    # Production database URL
    DATABASE_URL = "postgresql://postgres:zextoc-mewmu4-rImraw@innotech-platform-db.cjwsk6a0ob16.ap-southeast-2.amazonaws.com:5432/innotech_platform"
    
    print("🔄 Connecting to production database...")
    try:
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            print(f"✅ Connected to: {result.fetchone()[0]}")
        
        print("🔄 Creating all tables...")
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ All tables created successfully!")
        
        # Verify tables exist
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"📋 Tables created: {', '.join(tables)}")
            
        print("🎉 Production database setup complete!")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False
        
    return True

if __name__ == "__main__":
    setup_production_database()