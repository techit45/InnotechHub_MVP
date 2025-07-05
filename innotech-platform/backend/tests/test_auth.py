"""
Test authentication endpoints
"""
import pytest
from fastapi.testclient import TestClient

def test_user_registration(client: TestClient):
    """Test user registration"""
    response = client.post("/auth/register", json={
        "email": "newuser@example.com",
        "password": "password123",
        "first_name": "New",
        "last_name": "User",
        "role": "student"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["first_name"] == "New"
    assert data["last_name"] == "User"
    assert data["role"] == "student"
    assert "hashed_password" not in data

def test_user_login(client: TestClient):
    """Test user login"""
    # First register a user
    client.post("/auth/register", json={
        "email": "loginuser@example.com",
        "password": "password123",
        "first_name": "Login",
        "last_name": "User",
        "role": "student"
    })
    
    # Then login
    response = client.post("/auth/login", json={
        "email": "loginuser@example.com",
        "password": "password123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client: TestClient):
    """Test login with invalid credentials"""
    response = client.post("/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401

def test_get_current_user(client: TestClient, auth_headers):
    """Test getting current user info"""
    response = client.get("/auth/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["first_name"] == "Test"
    assert data["last_name"] == "User"

def test_get_current_user_unauthorized(client: TestClient):
    """Test getting current user without auth"""
    response = client.get("/auth/me")
    
    assert response.status_code == 403

def test_duplicate_email_registration(client: TestClient):
    """Test registering with duplicate email"""
    user_data = {
        "email": "duplicate@example.com",
        "password": "password123",
        "first_name": "First",
        "last_name": "User",
        "role": "student"
    }
    
    # First registration should succeed
    response1 = client.post("/auth/register", json=user_data)
    assert response1.status_code == 200
    
    # Second registration with same email should fail
    response2 = client.post("/auth/register", json=user_data)
    assert response2.status_code == 400