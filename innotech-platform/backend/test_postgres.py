#!/usr/bin/env python3
"""
Test script for PostgreSQL backend
"""
import os
import sys
from dotenv import load_dotenv

# Load PostgreSQL environment
load_dotenv('.env.postgres')

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import engine, get_db
from sqlalchemy import text

def test_database_connection():
    """Test PostgreSQL database connection"""
    print("🐘 Testing PostgreSQL Database Connection")
    print("=" * 50)
    
    try:
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Database connection successful!")
            print(f"PostgreSQL Version: {version[:80]}...")
            print()
            
            # Test tables
            tables = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)).fetchall()
            
            print("📋 Available Tables:")
            for table in tables:
                count = conn.execute(text(f"SELECT COUNT(*) FROM {table[0]}")).fetchone()
                print(f"  - {table[0]}: {count[0]} records")
            print()
            
            # Test users data
            users = conn.execute(text("""
                SELECT id, email, first_name, last_name, role 
                FROM users 
                LIMIT 5
            """)).fetchall()
            
            print("👥 Sample Users:")
            for user in users:
                print(f"  - {user[0]}: {user[1]} ({user[2]} {user[3]}) - {user[4]}")
            
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_api_functionality():
    """Test API functionality with PostgreSQL"""
    print("\n🔌 Testing API with PostgreSQL")
    print("=" * 50)
    
    try:
        # Import API models
        from app.models.user import User
        from app.models.course import Course
        from app.database import SessionLocal
        
        db = SessionLocal()
        
        # Test user query
        users = db.query(User).all()
        print(f"✅ Found {len(users)} users in database")
        
        # Test course query
        courses = db.query(Course).all()
        print(f"✅ Found {len(courses)} courses in database")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    print("🚀 PostgreSQL Backend Testing")
    print("🔗 Database URL:", os.getenv('DATABASE_URL', 'Not set'))
    print()
    
    # Test database connection
    db_success = test_database_connection()
    
    if db_success:
        # Test API functionality
        api_success = test_api_functionality()
        
        if api_success:
            print("\n🎉 All tests passed!")
            print("✅ PostgreSQL backend is ready for production")
            print()
            print("Next steps:")
            print("1. Update your main .env file to use PostgreSQL")
            print("2. Restart your FastAPI server")
            print("3. Test the frontend with PostgreSQL backend")
        else:
            print("\n❌ API tests failed!")
    else:
        print("\n❌ Database connection failed!")

if __name__ == "__main__":
    main()