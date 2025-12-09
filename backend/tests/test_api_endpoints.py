# backend/tests/test_api_endpoints.py
"""
Unit tests for FastAPI endpoints
Testing HTTP request/response handling
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json

class TestAPIEndpoints:
    """Test suite for API endpoint functionality"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns health info"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["status"] == "healthy"
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["api"] == "running"
    
    @patch('main.get_supabase_client')
    @patch('main.hash_password')
    def test_signup_success(self, mock_hash, mock_supabase, client):
        """Test successful user signup"""
        # Mock hash
        mock_hash.return_value = "$2b$12$test_hash"
        
        # Mock database - no existing user
        mock_db = MagicMock()
        mock_db.table().select().eq().execute.return_value = MagicMock(data=[])
        mock_db.table().insert().execute.return_value = MagicMock(
            data=[{"id": "user-123", "name": "testuser"}]
        )
        mock_supabase.return_value = mock_db
        
        # Execute
        response = client.post("/api/signup", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "success" in data["message"].lower()
    
    @patch('main.get_supabase_client')
    def test_signup_username_taken(self, mock_supabase, client):
        """Test signup fails when username exists"""
        # Mock database - existing user
        mock_db = MagicMock()
        mock_db.table().select().eq().execute.return_value = MagicMock(
            data=[{"id": "existing-user", "email": "testuser"}]
        )
        mock_supabase.return_value = mock_db
        
        # Execute
        response = client.post("/api/signup", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        # Verify
        assert response.status_code == 409
        data = response.json()
        assert "already taken" in data["detail"].lower()
    
    @patch('main.create_session')
    @patch('main.verify_password')
    @patch('main.get_supabase_client')
    def test_login_success(self, mock_supabase, mock_verify, mock_create_session, client):
        """Test successful login"""
        # Mock database
        mock_db = MagicMock()
        mock_db.table().select().eq().execute.return_value = MagicMock(
            data=[{
                "id": "user-123",
                "name": "testuser",
                "email": "testuser",
                "password_hash": "$2b$12$test_hash"
            }]
        )
        mock_supabase.return_value = mock_db
        
        # Mock password verification
        mock_verify.return_value = True
        
        # Mock session creation
        mock_create_session.return_value = "session-token-123"
        
        # Execute
        response = client.post("/api/login", json={
            "username": "testuser",
            "password": "testpass123"
        })
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert response.cookies.get("session_id") == "session-token-123"
    
    @patch('main.get_supabase_client')
    def test_login_invalid_credentials(self, mock_supabase, client):
        """Test login fails with invalid credentials"""
        # Mock database - no user found
        mock_db = MagicMock()
        mock_db.table().select().eq().execute.return_value = MagicMock(data=[])
        mock_supabase.return_value = mock_db
        
        # Execute
        response = client.post("/api/login", json={
            "username": "nonexistent",
            "password": "wrongpass"
        })
        
        # Verify
        assert response.status_code == 401
        data = response.json()
        assert "invalid credentials" in data["detail"].lower()
    
    @patch('main.delete_session')
    def test_logout_success(self, mock_delete, client):
        """Test successful logout"""
        # Set cookie
        client.cookies.set("session_id", "test-session-123")
        
        # Execute
        response = client.post("/api/logout")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert "logged out" in data["message"].lower()
        mock_delete.assert_called_once()
    
    @patch('main.generate_plan_from_llm')
    @patch('main.RulesEngine')
    def test_generate_plan_success(self, mock_rules_engine, mock_llm, client, sample_llm_response):
        """Test successful plan generation"""
        # Mock LLM response
        mock_llm.return_value = sample_llm_response
        
        # Mock rules engine
        mock_engine = MagicMock()
        mock_engine.apply_rules.return_value = {
            "meals": sample_llm_response["meals"],
            "workouts": sample_llm_response["workouts"],
            "replacements": {"meals": [], "workouts": []}
        }
        mock_rules_engine.return_value = mock_engine
        
        # Execute
        response = client.post("/generate-plan", json={
            "goal": "build muscle",
            "allergies": ["peanuts"],
            "injuries": [{"name": "knee injury", "severity": "moderate"}]
        })
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert "safe_plan" in data
        assert "meals" in data["safe_plan"]
        assert "workouts" in data["safe_plan"]
        assert len(data["safe_plan"]["meals"]) == 4
        assert len(data["safe_plan"]["workouts"]) == 4
    
    @patch('main.get_session')
    @patch('main.get_supabase_client')
    def test_get_saved_plans_authenticated(self, mock_supabase, mock_get_session, client):
        """Test retrieving saved plans when authenticated"""
        # Mock authentication
        mock_get_session.return_value = {
            "user_id": "user-123",
            "username": "testuser"
        }
        
        # Mock database
        mock_db = MagicMock()
        mock_db.table().select().eq().order().execute.return_value = MagicMock(
            data=[{
                "id": "plan-1",
                "goal": "build muscle",
                "created_at": "2024-01-01T00:00:00Z"
            }]
        )
        mock_db.table().select().eq().execute.return_value = MagicMock(data=[])
        mock_supabase.return_value = mock_db
        
        # Execute
        client.cookies.set("session_id", "valid-session")
        response = client.get("/api/plans")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        assert data["success"] is True
    
    def test_get_saved_plans_unauthenticated(self, client):
        """Test retrieving saved plans fails when not authenticated"""
        # Execute without session cookie
        response = client.get("/api/plans")
        
        # Verify
        assert response.status_code == 401