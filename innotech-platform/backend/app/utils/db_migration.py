"""
Database migration utilities for moving from SQLite to PostgreSQL
"""
import os
import subprocess
from sqlalchemy import create_engine, text
from ..database import get_db
from ..models import user, course, assignment
import json
from typing import Dict, Any

class DatabaseMigration:
    def __init__(self, sqlite_url: str, postgres_url: str):
        self.sqlite_engine = create_engine(sqlite_url)
        self.postgres_engine = create_engine(postgres_url)
    
    def export_sqlite_data(self) -> Dict[str, Any]:
        """Export all data from SQLite database"""
        data = {}
        
        with self.sqlite_engine.connect() as conn:
            # Export users
            users = conn.execute(text("SELECT * FROM users")).fetchall()
            data['users'] = [dict(user._mapping) for user in users]
            
            # Export courses
            courses = conn.execute(text("SELECT * FROM courses")).fetchall()
            data['courses'] = [dict(course._mapping) for course in courses]
            
            # Export modules
            modules = conn.execute(text("SELECT * FROM modules")).fetchall()
            data['modules'] = [dict(module._mapping) for module in modules]
            
            # Export enrollments
            enrollments = conn.execute(text("SELECT * FROM enrollments")).fetchall()
            data['enrollments'] = [dict(enrollment._mapping) for enrollment in enrollments]
            
            # Export assignments
            assignments = conn.execute(text("SELECT * FROM assignments")).fetchall()
            data['assignments'] = [dict(assignment._mapping) for assignment in assignments]
            
            # Export submissions
            submissions = conn.execute(text("SELECT * FROM submissions")).fetchall()
            data['submissions'] = [dict(submission._mapping) for submission in submissions]
        
        return data
    
    def test_postgres_connection(self) -> bool:
        """Test PostgreSQL connection"""
        try:
            with self.postgres_engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                return True
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}")
            return False
    
    def create_postgres_tables(self):
        """Create tables in PostgreSQL using Alembic"""
        try:
            # Run Alembic upgrade
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                capture_output=True,
                text=True,
                env=dict(os.environ, DATABASE_URL=str(self.postgres_engine.url))
            )
            
            if result.returncode == 0:
                print("✅ PostgreSQL tables created successfully")
                return True
            else:
                print(f"❌ Alembic error: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False
    
    def import_data_to_postgres(self, data: Dict[str, Any]):
        """Import data to PostgreSQL database"""
        try:
            with self.postgres_engine.connect() as conn:
                transaction = conn.begin()
                
                try:
                    # Import users
                    for user_data in data['users']:
                        # Convert SQLite boolean integers to PostgreSQL booleans
                        user_data['is_active'] = bool(user_data['is_active'])
                        user_data['is_verified'] = bool(user_data['is_verified'])
                        
                        conn.execute(text("""
                            INSERT INTO users (id, email, hashed_password, first_name, last_name, 
                                             role, is_active, is_verified, created_at, updated_at)
                            VALUES (:id, :email, :hashed_password, :first_name, :last_name,
                                   :role, :is_active, :is_verified, :created_at, :updated_at)
                        """), user_data)
                    
                    # Import courses
                    for course_data in data['courses']:
                        # Convert boolean for courses
                        course_data['is_free'] = bool(course_data['is_free'])
                        
                        conn.execute(text("""
                            INSERT INTO courses (id, title, description, short_description, thumbnail_url,
                                               instructor_id, status, duration_hours, price, is_free,
                                               created_at, updated_at)
                            VALUES (:id, :title, :description, :short_description, :thumbnail_url,
                                   :instructor_id, :status, :duration_hours, :price, :is_free,
                                   :created_at, :updated_at)
                        """), course_data)
                    
                    # Import modules
                    for module_data in data['modules']:
                        # Convert boolean for modules
                        module_data['is_published'] = bool(module_data['is_published'])
                        
                        conn.execute(text("""
                            INSERT INTO modules (id, course_id, title, description, content, video_url,
                                               order_index, duration_minutes, is_published, created_at, updated_at)
                            VALUES (:id, :course_id, :title, :description, :content, :video_url,
                                   :order_index, :duration_minutes, :is_published, :created_at, :updated_at)
                        """), module_data)
                    
                    # Import enrollments
                    for enrollment_data in data['enrollments']:
                        conn.execute(text("""
                            INSERT INTO enrollments (id, user_id, course_id, status, progress_percentage,
                                                    enrolled_at, completed_at)
                            VALUES (:id, :user_id, :course_id, :status, :progress_percentage,
                                   :enrolled_at, :completed_at)
                        """), enrollment_data)
                    
                    # Import assignments
                    for assignment_data in data['assignments']:
                        # Convert boolean for assignments
                        assignment_data['is_required'] = bool(assignment_data['is_required'])
                        
                        conn.execute(text("""
                            INSERT INTO assignments (id, course_id, title, description, instructions,
                                                    max_score, due_date, is_required, created_at, updated_at)
                            VALUES (:id, :course_id, :title, :description, :instructions,
                                   :max_score, :due_date, :is_required, :created_at, :updated_at)
                        """), assignment_data)
                    
                    # Import submissions
                    for submission_data in data['submissions']:
                        conn.execute(text("""
                            INSERT INTO submissions (id, assignment_id, student_id, file_url, file_name,
                                                    content, status, score, feedback, submitted_at, reviewed_at)
                            VALUES (:id, :assignment_id, :student_id, :file_url, :file_name,
                                   :content, :status, :score, :feedback, :submitted_at, :reviewed_at)
                        """), submission_data)
                    
                    transaction.commit()
                    print("✅ Data imported successfully to PostgreSQL")
                    return True
                
                except Exception as e:
                    transaction.rollback()
                    print(f"❌ Error importing data: {e}")
                    return False
                    
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            return False
    
    def migrate(self) -> bool:
        """Complete migration process"""
        print("🚀 Starting database migration from SQLite to PostgreSQL...")
        
        # Step 1: Test PostgreSQL connection
        print("1. Testing PostgreSQL connection...")
        if not self.test_postgres_connection():
            return False
        
        # Step 2: Export SQLite data
        print("2. Exporting data from SQLite...")
        data = self.export_sqlite_data()
        
        # Save backup
        with open('sqlite_backup.json', 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"   📁 Backup saved to sqlite_backup.json")
        
        # Step 3: Create PostgreSQL tables
        print("3. Creating PostgreSQL tables...")
        if not self.create_postgres_tables():
            return False
        
        # Step 4: Import data
        print("4. Importing data to PostgreSQL...")
        if not self.import_data_to_postgres(data):
            return False
        
        print("✅ Migration completed successfully!")
        return True

def setup_postgresql_locally():
    """Setup PostgreSQL locally using Homebrew"""
    commands = [
        "brew install postgresql@14",
        "brew services start postgresql@14",
        "createdb innotech_production",
        "psql innotech_production -c \"CREATE USER innotech_user WITH PASSWORD 'secure_password_2024';\""
        "psql innotech_production -c \"GRANT ALL PRIVILEGES ON DATABASE innotech_production TO innotech_user;\""
    ]
    
    print("🍺 Setting up PostgreSQL locally...")
    for cmd in commands:
        print(f"Running: {cmd}")
        result = subprocess.run(cmd.split(), capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Command failed: {result.stderr}")
        else:
            print(f"✅ Success: {result.stdout}")

if __name__ == "__main__":
    # Example usage
    sqlite_url = "sqlite:///./innotech_db.sqlite"
    postgres_url = "postgresql://innotech_user:secure_password_2024@localhost:5432/innotech_production"
    
    migrator = DatabaseMigration(sqlite_url, postgres_url)
    migrator.migrate()