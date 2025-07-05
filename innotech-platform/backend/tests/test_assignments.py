"""
Test assignment endpoints
"""
import pytest
from fastapi.testclient import TestClient
import io

def test_create_assignment_as_trainer(client: TestClient, trainer_headers):
    """Test creating assignment as trainer"""
    # First create a course
    course_response = client.post("/courses/", 
        headers=trainer_headers,
        json={
            "title": "Test Course",
            "description": "Test course description",
            "status": "published"
        }
    )
    course_id = course_response.json()["id"]
    
    # Create assignment
    response = client.post("/assignments/", 
        headers=trainer_headers,
        json={
            "course_id": course_id,
            "title": "Test Assignment",
            "description": "Test assignment description",
            "max_score": 100,
            "is_required": True
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Assignment"
    assert data["max_score"] == 100
    assert data["is_required"] == True

def test_create_assignment_as_student_fails(client: TestClient, auth_headers):
    """Test that students cannot create assignments"""
    response = client.post("/assignments/", 
        headers=auth_headers,
        json={
            "course_id": 1,
            "title": "Test Assignment",
            "description": "Test assignment description"
        }
    )
    
    assert response.status_code == 403

def test_get_assignments(client: TestClient, auth_headers):
    """Test getting assignments list"""
    response = client.get("/assignments/", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_submit_assignment_with_content(client: TestClient, auth_headers, trainer_headers):
    """Test submitting assignment with text content"""
    # Create course and assignment first
    course_response = client.post("/courses/", 
        headers=trainer_headers,
        json={
            "title": "Test Course",
            "description": "Test course description",
            "status": "published"
        }
    )
    course_id = course_response.json()["id"]
    
    assignment_response = client.post("/assignments/", 
        headers=trainer_headers,
        json={
            "course_id": course_id,
            "title": "Test Assignment",
            "description": "Test assignment description",
            "max_score": 100
        }
    )
    assignment_id = assignment_response.json()["id"]
    
    # Submit assignment with content
    response = client.post(f"/assignments/{assignment_id}/submissions",
        headers=auth_headers,
        data={"content": "This is my assignment submission"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "This is my assignment submission"
    assert data["status"] == "submitted"

def test_submit_assignment_with_file(client: TestClient, auth_headers, trainer_headers):
    """Test submitting assignment with file"""
    # Create course and assignment first
    course_response = client.post("/courses/", 
        headers=trainer_headers,
        json={
            "title": "Test Course",
            "description": "Test course description",
            "status": "published"
        }
    )
    course_id = course_response.json()["id"]
    
    assignment_response = client.post("/assignments/", 
        headers=trainer_headers,
        json={
            "course_id": course_id,
            "title": "Test Assignment",
            "description": "Test assignment description",
            "max_score": 100
        }
    )
    assignment_id = assignment_response.json()["id"]
    
    # Create a test file
    test_file = io.BytesIO(b"Test file content")
    test_file.name = "test.txt"
    
    # Submit assignment with file
    response = client.post(f"/assignments/{assignment_id}/submissions",
        headers=auth_headers,
        files={"file": ("test.txt", test_file, "text/plain")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["file_name"] == "test.txt"
    assert data["status"] == "submitted"

def test_grade_submission(client: TestClient, auth_headers, trainer_headers):
    """Test grading a submission"""
    # Create course, assignment, and submission
    course_response = client.post("/courses/", 
        headers=trainer_headers,
        json={
            "title": "Test Course",
            "description": "Test course description",
            "status": "published"
        }
    )
    course_id = course_response.json()["id"]
    
    assignment_response = client.post("/assignments/", 
        headers=trainer_headers,
        json={
            "course_id": course_id,
            "title": "Test Assignment",
            "description": "Test assignment description",
            "max_score": 100
        }
    )
    assignment_id = assignment_response.json()["id"]
    
    submission_response = client.post(f"/assignments/{assignment_id}/submissions",
        headers=auth_headers,
        data={"content": "This is my assignment submission"}
    )
    submission_id = submission_response.json()["id"]
    
    # Grade the submission
    response = client.put(f"/assignments/submissions/{submission_id}",
        headers=trainer_headers,
        json={
            "score": 85,
            "feedback": "Good work!",
            "status": "approved"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 85
    assert data["feedback"] == "Good work!"
    assert data["status"] == "approved"

def test_duplicate_submission_fails(client: TestClient, auth_headers, trainer_headers):
    """Test that students cannot submit the same assignment twice"""
    # Create course and assignment
    course_response = client.post("/courses/", 
        headers=trainer_headers,
        json={
            "title": "Test Course",
            "description": "Test course description",
            "status": "published"
        }
    )
    course_id = course_response.json()["id"]
    
    assignment_response = client.post("/assignments/", 
        headers=trainer_headers,
        json={
            "course_id": course_id,
            "title": "Test Assignment",
            "description": "Test assignment description",
            "max_score": 100
        }
    )
    assignment_id = assignment_response.json()["id"]
    
    # First submission should succeed
    response1 = client.post(f"/assignments/{assignment_id}/submissions",
        headers=auth_headers,
        data={"content": "First submission"}
    )
    assert response1.status_code == 200
    
    # Second submission should fail
    response2 = client.post(f"/assignments/{assignment_id}/submissions",
        headers=auth_headers,
        data={"content": "Second submission"}
    )
    assert response2.status_code == 400