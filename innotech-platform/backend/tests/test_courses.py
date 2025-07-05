"""
Test course endpoints
"""
import pytest
from fastapi.testclient import TestClient

def test_create_course_as_trainer(client: TestClient, trainer_headers):
    """Test creating course as trainer"""
    response = client.post("/courses/", 
        headers=trainer_headers,
        json={
            "title": "Python Programming",
            "description": "Learn Python from basics to advanced",
            "short_description": "Python course",
            "status": "published",
            "duration_hours": 40,
            "price": 299900,  # 2999.00 THB in cents
            "is_free": False
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Python Programming"
    assert data["description"] == "Learn Python from basics to advanced"
    assert data["status"] == "published"
    assert data["duration_hours"] == 40
    assert data["price"] == 299900
    assert data["is_free"] == False

def test_create_course_as_student_fails(client: TestClient, auth_headers):
    """Test that students cannot create courses"""
    response = client.post("/courses/", 
        headers=auth_headers,
        json={
            "title": "Unauthorized Course",
            "description": "This should fail",
            "status": "published"
        }
    )
    
    assert response.status_code == 403

def test_get_courses_public(client: TestClient):
    """Test getting public courses list"""
    response = client.get("/courses/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_enroll_in_course(client: TestClient, auth_headers, trainer_headers):
    """Test enrolling in a course"""
    # First create a course
    course_response = client.post("/courses/", 
        headers=trainer_headers,
        json={
            "title": "Test Course",
            "description": "Test course for enrollment",
            "status": "published",
            "is_free": True
        }
    )
    
    course_id = course_response.json()["id"]
    
    # Enroll in the course
    response = client.post(f"/courses/{course_id}/enroll", headers=auth_headers)
    
    assert response.status_code == 200

def test_get_my_enrollments(client: TestClient, auth_headers):
    """Test getting user's enrollments"""
    response = client.get("/courses/my/enrollments", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_course_with_modules(client: TestClient, trainer_headers):
    """Test creating course with modules"""
    # Create course
    course_response = client.post("/courses/", 
        headers=trainer_headers,
        json={
            "title": "Course with Modules",
            "description": "Test course with modules",
            "status": "published"
        }
    )
    
    course_id = course_response.json()["id"]
    
    # Add module
    module_response = client.post(f"/courses/{course_id}/modules",
        headers=trainer_headers,
        json={
            "title": "Module 1",
            "description": "First module",
            "content": "Module content here",
            "order_index": 1,
            "duration_minutes": 60,
            "is_published": True
        }
    )
    
    assert module_response.status_code == 200
    module_data = module_response.json()
    assert module_data["title"] == "Module 1"
    assert module_data["course_id"] == course_id

def test_get_course_with_modules(client: TestClient, trainer_headers):
    """Test getting course details with modules"""
    # Create course
    course_response = client.post("/courses/", 
        headers=trainer_headers,
        json={
            "title": "Detailed Course",
            "description": "Course with details",
            "status": "published"
        }
    )
    
    course_id = course_response.json()["id"]
    
    # Get course details
    response = client.get(f"/courses/{course_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Detailed Course"
    assert "modules" in data
    assert isinstance(data["modules"], list)

def test_update_course(client: TestClient, trainer_headers):
    """Test updating course"""
    # Create course
    course_response = client.post("/courses/", 
        headers=trainer_headers,
        json={
            "title": "Original Title",
            "description": "Original description",
            "status": "draft"
        }
    )
    
    course_id = course_response.json()["id"]
    
    # Update course
    response = client.put(f"/courses/{course_id}",
        headers=trainer_headers,
        json={
            "title": "Updated Title",
            "description": "Updated description",
            "status": "published"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated description"
    assert data["status"] == "published"