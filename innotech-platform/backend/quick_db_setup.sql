-- Quick database setup for production
-- Run this SQL directly on RDS

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(50) DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create courses table
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    instructor_id INTEGER REFERENCES users(id),
    code VARCHAR(50) UNIQUE NOT NULL,
    credits INTEGER DEFAULT 3,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create assignments table
CREATE TABLE IF NOT EXISTS assignments (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    course_id INTEGER REFERENCES courses(id),
    due_date TIMESTAMP,
    max_score INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create submissions table
CREATE TABLE IF NOT EXISTS submissions (
    id SERIAL PRIMARY KEY,
    assignment_id INTEGER REFERENCES assignments(id),
    student_id INTEGER REFERENCES users(id),
    content TEXT,
    file_path VARCHAR(500),
    score INTEGER,
    feedback TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    graded_at TIMESTAMP,
    UNIQUE(assignment_id, student_id)
);

-- Insert sample data
INSERT INTO users (email, username, first_name, last_name, hashed_password, role) VALUES
('admin@innotech.com', 'admin', 'Admin', 'User', '$2b$12$dummy.hash.for.admin', 'instructor'),
('student@innotech.com', 'student1', 'John', 'Doe', '$2b$12$dummy.hash.for.student', 'student')
ON CONFLICT (email) DO NOTHING;

INSERT INTO courses (name, description, instructor_id, code) VALUES
('Introduction to Programming', 'Learn the basics of programming', 1, 'CS101'),
('Web Development', 'Build modern web applications', 1, 'WEB201')
ON CONFLICT (code) DO NOTHING;

INSERT INTO assignments (title, description, course_id, due_date) VALUES
('Hello World Program', 'Write your first program', 1, NOW() + INTERVAL '7 days'),
('Personal Website', 'Create a personal portfolio website', 2, NOW() + INTERVAL '14 days')
ON CONFLICT DO NOTHING;